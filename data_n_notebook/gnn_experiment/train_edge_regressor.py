import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from pathlib import Path
import mlflow
import json
import random
from itertools import product
from models.gat import CareerTreeModel
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import time
from datetime import datetime
import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
import pandas as pd
import glob
import torch.serialization
from pinecone import Pinecone
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Get Pinecone API key from environment
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
if not PINECONE_API_KEY:
    raise ValueError("Please set PINECONE_API_KEY in your .env file")

# === Device Setup === #
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
# device = torch.device("cpu")
print(f"Using device: {device}")


# === Load Data === #
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXPERIMENT_DIR = BASE_DIR / "experiment_results"
CHECKPOINT_DIR = EXPERIMENT_DIR / "checkpoints"
RESULTS_DIR = EXPERIMENT_DIR / "results"

# Create directories if they don't exist
EXPERIMENT_DIR.mkdir(exist_ok=True)
CHECKPOINT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

x = torch.load(DATA_DIR / "node_features.pt").to(device)
edge_index = torch.load(DATA_DIR / "edge_index.pt").to(device)
edge_type = torch.tensor(json.load(open(DATA_DIR / "edge_type.json")), dtype=torch.long).to(device)

# from collections import Counter
# print("Relation type distribution in edge_type.json:")
# print(Counter(edge_type))

# Load node mappings
with open(DATA_DIR / "node2idx.json", "r") as f:
    node2idx = json.load(f)
with open(DATA_DIR / "idx2node.json", "r") as f:
    idx2node = json.load(f)
with open(DATA_DIR / "edge_type.json", "r") as f:
    edge_types = json.load(f)

# Load relation type dictionary
with open(DATA_DIR / "relation_types.json", "r") as f:
    relation_types = json.load(f)
num_relations = len(relation_types)

import random

# === Prepare Edge Regression Data === #
def prepare_edge_data():
    print("Preparing edge data...")
    # Create triplets for edge regression
    triplets = []
    
    # Debug: Print more entries of node2idx and look for occupation nodes
    print("\nAnalyzing node2idx for occupation nodes...")
    occupation_prefixes = ['occ::', 'occ_', 'occupation::', 'occupation_']
    found_prefixes = set()
    
    for node, idx in node2idx.items():
        for prefix in occupation_prefixes:
            if node.startswith(prefix):
                found_prefixes.add(prefix)
                break
    
    print(f"Found occupation nodes with prefixes: {found_prefixes}")
    
    # Process existing edges with all relation types
    edge_index_tensor = edge_index.t()
    for i, (u, v) in enumerate(edge_index_tensor):
        relation_id = edge_types[i]  # this is already an integer
        triplets.append((u.item(), v.item(), relation_id))
    
    print(f"Found {len(triplets)} edges with {len(set(t[2] for t in triplets))} different relation types")
    
    # Generate negative samples
    num_negatives = len(triplets)
    negatives = []
    
    # Get all occupation and skill nodes
    occupation_nodes = []
    skill_nodes = []
    
    print("\nAnalyzing node types in node2idx...")
    for node, idx in node2idx.items():
        if node.startswith('skill::key_'):
            skill_nodes.append(idx)
        elif any(node.startswith(prefix) for prefix in found_prefixes):
            occupation_nodes.append(idx)
    
    print(f"Found {len(occupation_nodes)} occupation nodes and {len(skill_nodes)} skill nodes")
    
    if not occupation_nodes or not skill_nodes:
        raise ValueError("No occupation or skill nodes found in node2idx. Please check the node naming convention.")
    
    print("Generating negative samples...")
    for _ in range(num_negatives):
        s = random.choice(skill_nodes)
        o = random.choice(occupation_nodes)
        # Use unknown relation type for negative samples
        negatives.append((s, o, relation_types["unknown"]))
    
    # Combine positive and negative samples
    all_edges = triplets + negatives
    random.shuffle(all_edges)
    
    # Split into train/val/test
    train_edges, temp_edges = train_test_split(all_edges, test_size=0.3, random_state=42)
    val_edges, test_edges = train_test_split(temp_edges, test_size=0.5, random_state=42)
    
    print(f"Data split: {len(train_edges)} train, {len(val_edges)} val, {len(test_edges)} test")
    return train_edges, val_edges, test_edges

def plot_precision_recall_curves(predictions, actuals, save_path):
    """Plot Precision@k and Recall@k curves."""
    ks = [1, 3, 5, 10]
    precision_scores = []
    recall_scores = []
    
    # Calculate precision and recall for each k
    for k in ks:
        top_k_idx = np.argsort(predictions)[-k:]
        precision = np.mean(actuals[top_k_idx] > 0)
        recall = np.mean(actuals[top_k_idx] == 1.0)  # Recall for essential edges
        
        precision_scores.append(precision)
        recall_scores.append(recall)
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(ks, precision_scores, 'b-', label='Precision@k', marker='o')
    plt.plot(ks, recall_scores, 'r-', label='Recall@k (Essential)', marker='s')
    plt.xlabel("k")
    plt.ylabel("Score")
    plt.title("Precision and Recall @k")
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()
    
    return precision_scores, recall_scores

def plot_prediction_distribution(predictions, actuals, save_path):
    """Plot distribution of predictions for each class."""
    plt.figure(figsize=(10, 6))
    
    # Separate predictions by class
    essential_preds = predictions[actuals == 1.0]
    optional_preds = predictions[actuals == 0.5]
    negative_preds = predictions[actuals == 0.0]
    
    plt.hist([essential_preds, optional_preds, negative_preds],
             bins=30, label=['Essential', 'Optional', 'Negative'], 
             alpha=0.7, density=True)
    plt.title('Distribution of Predictions by Class')
    plt.xlabel('Predicted Score')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()

def save_run_summary(config, metrics, save_path):
    """Save run summary to CSV."""
    summary = {
        **config,
        **metrics,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
    }
    
    # Convert to DataFrame and save
    df = pd.DataFrame([summary])
    df.to_csv(save_path, index=False)
    return summary

def calculate_metrics(predictions, actuals):
    """Calculate various metrics for model evaluation."""
    metrics = {}
    
    # ROC AUC
    metrics['roc_auc'] = roc_auc_score(actuals > 0, predictions)
    
    # Precision@K for different K values
    for k in [1, 3, 5, 10]:
        top_k_idx = np.argsort(predictions)[-k:]
        metrics[f'precision_at_{k}'] = np.mean(actuals[top_k_idx] > 0)
    
    # Recall@K for essential edges
    essential_mask = actuals == 1.0
    for k in [1, 3, 5, 10]:
        top_k_idx = np.argsort(predictions)[-k:]
        metrics[f'recall_essential_at_{k}'] = np.mean(essential_mask[top_k_idx])
    
    return metrics

# === Hyperparameter Search Space === #
# search_space = {
#     "hidden_dim": [128, 256],
#     "heads": [4, 8],
#     "lr": [1e-4, 2e-4],
#     "dropout": [0.3, 0.5],
#     "weight_decay": [1e-4, 5e-4],
#     "batch_size": [64, 128]  # Increased batch sizes for M1 Pro
# }

# === Hyperparameter Search Space === #
search_space = {
    'hidden_dim': [128],
    'heads': [4],
    'lr': [0.0001],
    'dropout': [0.3],
    'weight_decay': [0.0001],
    'batch_size': [32]
}



combinations = list(product(*search_space.values()))
print(f"Total combinations to try: {len(combinations)}")

# === MLflow Setup === #
mlflow.set_experiment("Career_Tree_Edge_Regression")

def find_latest_checkpoint(checkpoint_dir):
    """Find the latest checkpoint file."""
    checkpoint_files = glob.glob(str(checkpoint_dir / "pause_checkpoint_*.pt"))
    if not checkpoint_files:
        return None
    return max(checkpoint_files, key=os.path.getctime)

def load_checkpoint(checkpoint_path, model, optimizer):
    """Load model and optimizer state from checkpoint."""
    print(f"Loading checkpoint from {checkpoint_path}")
    
    # Add safe globals for numpy types
    torch.serialization.add_safe_globals(['numpy._core.multiarray.scalar'])
    
    try:
        # First try loading with weights_only=True (safer)
        checkpoint = torch.load(checkpoint_path, weights_only=True)
    except Exception as e:
        print("Warning: Safe loading failed, attempting full load...")
        # If that fails, try loading with weights_only=False
        checkpoint = torch.load(checkpoint_path, weights_only=False)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    return checkpoint['epoch'], checkpoint['val_loss'], checkpoint['val_metrics']

# Load environment variables
load_dotenv()

# Get Pinecone API key from environment
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
if not PINECONE_API_KEY:
    raise ValueError("Please set PINECONE_API_KEY in your .env file")

for combo_idx, combo in enumerate(combinations, 1):
    config = dict(zip(search_space.keys(), combo))
    print(f"\n=== Starting combination {combo_idx}/{len(combinations)} ===")
    print(f"Config: {config}")
    
    with mlflow.start_run():
        # Log hyperparameters
        for k, v in config.items():
            mlflow.log_param(k, v)
        
        mlflow.log_param("embedding_dim", x.size(1))
        mlflow.log_param("epochs", 100)
        
        # Initialize model
        model = CareerTreeModel(
            input_dim=x.size(1),
            hidden_dim=config["hidden_dim"],
            output_dim=config["hidden_dim"],
            heads=config["heads"],
            dropout=config["dropout"],
            num_relations=num_relations  # Add number of relation types
        ).to(device)
        
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config["lr"],
            weight_decay=config["weight_decay"]
        )
        
        # Prepare data
        train_edges, val_edges, test_edges = prepare_edge_data()
        
        # Training loop
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0
        start_time = time.time()
        
        # Check for existing checkpoint
        latest_checkpoint = find_latest_checkpoint(CHECKPOINT_DIR)
        start_epoch = 1
        
        if latest_checkpoint:
            print(f"\nFound checkpoint: {latest_checkpoint}")
            response = input("Do you want to resume training from this checkpoint? (y/n): ")
            if response.lower() == 'y':
                start_epoch, best_val_loss, val_metrics = load_checkpoint(latest_checkpoint, model, optimizer)
                print(f"Resuming training from epoch {start_epoch}")
                print(f"Previous best validation loss: {best_val_loss:.4f}")
            else:
                print("Starting fresh training run")
        
        try:
            for epoch in range(start_epoch, 100):
                epoch_start = time.time()
                model.train()
                total_loss = 0
                
                # Training
                for batch_start in range(0, len(train_edges), config["batch_size"]):
                    batch_edges = train_edges[batch_start:batch_start + config["batch_size"]]
                    
                    # Get positive and negative pairs
                    pos_edges = [e for e in batch_edges if e[2] > 0]
                    neg_edges = [e for e in batch_edges if e[2] == 0]
                    
                    # Ensure equal numbers
                    min_size = min(len(pos_edges), len(neg_edges))
                    if min_size == 0:
                        continue
                        
                    # Sample up to batch_size//2 positive and negative pairs
                    max_per_class = config["batch_size"] // 2
                    pos_edges = random.sample(pos_edges, min(len(pos_edges), max_per_class))
                    neg_edges = random.sample(neg_edges, min(len(neg_edges), max_per_class))
                    
                    # Create tensors
                    pos_pairs = torch.tensor([[e[0], e[1]] for e in pos_edges]).t().to(device)
                    neg_pairs = torch.tensor([[e[0], e[1]] for e in neg_edges]).t().to(device)
                    
                    # Get predictions for positive and negative pairs
                    pos_pred = model(x, edge_index, edge_type, pos_pairs).view(-1)
                    neg_pred = model(x, edge_index, edge_type, neg_pairs).view(-1)
                    
                    # Drop batch if not enough examples
                    if pos_pred.numel() < 2 or neg_pred.numel() < 2:
                        continue
                    
                    # Calculate margin ranking loss
                    margin_value = 0.2
                    loss = F.margin_ranking_loss(pos_pred, neg_pred, 
                                               torch.ones_like(pos_pred), 
                                               margin=margin_value)
                    
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                    
                    if batch_start % 100 == 0:
                        print(f"Batch {batch_start//config['batch_size']}, Loss: {loss.item():.4f}")
                
                # Validation
                model.eval()
                val_loss = 0
                val_predictions = []
                val_actuals = []
                
                with torch.no_grad():
                    for batch_start in range(0, len(val_edges), config["batch_size"]):
                        batch_edges = val_edges[batch_start:batch_start + config["batch_size"]]
                        edge_pairs = torch.tensor([[e[0], e[1]] for e in batch_edges]).t().to(device)
                        labels = torch.tensor([e[2] for e in batch_edges]).float().to(device)
                        
                        pred = model(x, edge_index, edge_type, edge_pairs).squeeze()
                        val_loss += F.mse_loss(pred, labels).item()
                        
                        val_predictions.extend(pred.cpu().tolist())
                        val_actuals.extend(labels.cpu().tolist())
                
                # Calculate validation metrics
                val_predictions = np.array(val_predictions)
                val_actuals = np.array(val_actuals)
                val_metrics = calculate_metrics(val_predictions, val_actuals)
                
                # Log metrics
                mlflow.log_metric("val_loss", val_loss / len(val_edges), step=epoch)
                for metric_name, metric_value in val_metrics.items():
                    mlflow.log_metric(f"val_{metric_name}", metric_value, step=epoch)
                
                # Print epoch summary
                epoch_time = time.time() - epoch_start
                print(f"\nEpoch {epoch} Summary:")
                print(f"Train Loss: {total_loss/len(train_edges):.4f}")
                print(f"Val Loss: {val_loss/len(val_edges):.4f}")
                print(f"Val AUC: {val_metrics['roc_auc']:.4f}")
                print(f"Time: {epoch_time:.1f}s")
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    # Save best model
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    checkpoint_path = CHECKPOINT_DIR / f"best_model_{timestamp}.pt"
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'val_loss': val_loss,
                        'val_metrics': val_metrics,
                        'config': config
                    }, checkpoint_path)
                    mlflow.log_artifact(str(checkpoint_path))
                    print(f"\nSaved best model checkpoint to {checkpoint_path}")
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        print(f"\nEarly stopping at epoch {epoch}")
                        break
                        
        except Keyboardinterrupt:
            print("\n⏸️ Training interrupted. Saving checkpoint...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pause_checkpoint_path = CHECKPOINT_DIR / f"pause_checkpoint_{timestamp}.pt"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_metrics': val_metrics,
                'config': config,
                'best_val_loss': best_val_loss,
                'patience_counter': patience_counter
            }, pause_checkpoint_path)
            print(f"✅ Checkpoint saved to {pause_checkpoint_path}")
            exit()
        
        # Final evaluation on test set
        print("\nEvaluating on test set...")
        model.eval()
        test_predictions = []
        test_actuals = []
        
        with torch.no_grad():
            for batch_start in range(0, len(test_edges), config["batch_size"]):
                batch_edges = test_edges[batch_start:batch_start + config["batch_size"]]
                edge_pairs = torch.tensor([[e[0], e[1]] for e in batch_edges]).t().to(device)
                labels = torch.tensor([e[2] for e in batch_edges]).float().to(device)
                
                pred = model(x, edge_index, edge_type, edge_pairs).squeeze()
                test_predictions.extend(pred.cpu().tolist())
                test_actuals.extend(labels.cpu().tolist())
        
        # Convert to numpy arrays
        test_predictions = np.array(test_predictions)
        test_actuals = np.array(test_actuals)
        
        # Calculate metrics
        test_metrics = calculate_metrics(test_predictions, test_actuals)
        
        # Calculate total training time
        total_time = time.time() - start_time
        print(f"\nTotal training time: {total_time/60:.2f} minutes")
        
        # Generate and save visualizations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Plot precision/recall curves
        pr_curve_path = RESULTS_DIR / f"precision_recall_curve_{timestamp}.png"
        precision_scores, recall_scores = plot_precision_recall_curves(
            test_predictions, test_actuals, pr_curve_path)
        mlflow.log_artifact(str(pr_curve_path))
        
        # Plot prediction distribution
        dist_path = RESULTS_DIR / f"prediction_distribution_{timestamp}.png"
        plot_prediction_distribution(test_predictions, test_actuals, dist_path)
        mlflow.log_artifact(str(dist_path))
        
        # Save run summary
        summary_path = RESULTS_DIR / f"run_summary_{timestamp}.csv"
        summary = save_run_summary(config, test_metrics, summary_path)
        mlflow.log_artifact(str(summary_path))
        
        # Save final results
        results = {
            "config": config,
            "test_metrics": test_metrics,
            "training_time_minutes": total_time/60,
            "precision_scores": precision_scores,
            "recall_scores": recall_scores
        }
        
        results_path = RESULTS_DIR / f"results_{timestamp}.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        mlflow.log_artifact(str(results_path))
        
        print(f"\nResults saved to {results_path}")
        print("\nTest Metrics:")
        for metric_name, metric_value in test_metrics.items():
            print(f"{metric_name}: {metric_value:.4f}")
        print(f"\nTraining time: {total_time/60:.2f} minutes")

def get_node_embeddings(model, x, edge_index, edge_type, device):
    """Extract node embeddings from the trained model."""
    model.eval()
    with torch.no_grad():
        embeddings = model.get_node_embeddings(x, edge_index, edge_type)
        return embeddings.cpu().numpy() 

# Get final node embeddings
print("\nExtracting node embeddings...")
node_embeddings = get_node_embeddings(model, x, edge_index, edge_type, device)

# Save embeddings locally
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
embeddings_path = RESULTS_DIR / f"node_embeddings_{timestamp}.npy"
np.save(embeddings_path, node_embeddings)
mlflow.log_artifact(str(embeddings_path))

# Save embedding metadata
embedding_metadata = {
    "num_nodes": len(node_embeddings),
    "embedding_dim": node_embeddings.shape[1],
    "node_mapping": {str(idx): node for node, idx in node2idx.items()}
}
metadata_path = RESULTS_DIR / f"embedding_metadata_{timestamp}.json"
with open(metadata_path, "w") as f:
    json.dump(embedding_metadata, f, indent=2)
mlflow.log_artifact(str(metadata_path))

# Load node information
print("\nLoading node information...")
with open(DATA_DIR / "node_metadata.json", "r") as f:
    node_metadata = json.load(f)

# Upload embeddings to Pinecone
print("\nUploading embeddings to Pinecone with detailed metadata...")
try:
    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Get or create index
    index_name = "gnn-embeddings"
    if index_name not in pc.list_indexes().names():
        print(f"Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=node_embeddings.shape[1],
            metric="cosine"
        )
    
    index = pc.Index(index_name)
    
    # Prepare vectors for upload
    vectors_to_upsert = []
    for idx, embedding in enumerate(node_embeddings):
        node_name = idx2node[str(idx)]
        node_data = node_metadata.get(node_name, {})
        
        vectors_to_upsert.append({
            "id": node_name,
            "values": embedding.tolist(),
            "metadata": {
                "type": node_data.get("type", "unknown"),
                "original_id": node_name,
                "preferred_label": node_data.get("label", ""),
                "description": node_data.get("description", ""),
                "definition": node_data.get("definition", ""),
                "alt_labels": node_data.get("alt_labels", []),
                "broader": node_data.get("broader", []),
                "narrower": node_data.get("narrower", []),
                "related": node_data.get("related", [])
            }
        })
    
    # Upload in batches
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i//batch_size + 1}/{(len(vectors_to_upsert) + batch_size - 1)//batch_size}")
    
    print(f"✅ Successfully uploaded {len(vectors_to_upsert)} embeddings with detailed metadata to Pinecone index: {index_name}")
    
except Exception as e:
    print(f"❌ Error uploading to Pinecone: {str(e)}")
    print("Embeddings are still saved locally at:", embeddings_path)
 