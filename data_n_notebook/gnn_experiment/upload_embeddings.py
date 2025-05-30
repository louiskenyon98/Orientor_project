
import torch
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from models.GraphSage import CareerTreeModel

# Load environment variables
load_dotenv()

# Get Pinecone API key from environment
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
if not PINECONE_API_KEY:
    raise ValueError("Please set PINECONE_API_KEY in your .env file")

# === Setup Paths === #
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXPERIMENT_DIR = BASE_DIR / "experiment_results"
RESULTS_DIR = EXPERIMENT_DIR / "results/GraphSage"
CHECKPOINT_DIR = EXPERIMENT_DIR / "checkpoints/GraphSage"

# Create directories if they don't exist
EXPERIMENT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# === Load Data === #
print("Loading data...")
x = torch.load(DATA_DIR / "node_features.pt")
edge_index = torch.load(DATA_DIR / "edge_index.pt")
edge_type = torch.tensor(json.load(open(DATA_DIR / "edge_type.json")), dtype=torch.long)

# Load node mappings
with open(DATA_DIR / "node2idx.json", "r") as f:
    node2idx = json.load(f)
with open(DATA_DIR / "idx2node.json", "r") as f:
    idx2node = json.load(f)

# === Load Model === #
print("Loading model checkpoint...")
checkpoint_path = CHECKPOINT_DIR / "pause_checkpoint_20250519_113135.pt"

# Add safe globals for numpy types
torch.serialization.add_safe_globals(['numpy._core.multiarray.scalar'])

try:
    # First try loading with weights_only=True (safer)
    checkpoint = torch.load(checkpoint_path, weights_only=True)
except Exception as e:
    print("Warning: Safe loading failed, attempting full load...")
    # If that fails, try loading with weights_only=False
    checkpoint = torch.load(checkpoint_path, weights_only=False)

# Initialize model with same config
model = CareerTreeModel(
    input_dim=x.size(1),
    hidden_dim=checkpoint['config']['hidden_dim'],
    output_dim=checkpoint['config']['hidden_dim'],
    dropout=checkpoint['config']['dropout']
)

# Load model weights
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# === Extract Embeddings === #
print("\nExtracting node embeddings...")
with torch.no_grad():
    embeddings = model.get_node_embeddings(x, edge_index, edge_type)
    node_embeddings = embeddings.cpu().numpy()

# Save embeddings locally
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
embeddings_path = RESULTS_DIR / f"node_embeddings_{timestamp}.npy"
np.save(embeddings_path, node_embeddings)
print(f"Saved embeddings to {embeddings_path}")

# Save embedding metadata
embedding_metadata = {
    "num_nodes": len(node_embeddings),
    "embedding_dim": node_embeddings.shape[1],
    "node_mapping": {str(idx): node for node, idx in node2idx.items()}
}
metadata_path = RESULTS_DIR / f"embedding_metadata_{timestamp}.json"
with open(metadata_path, "w") as f:
    json.dump(embedding_metadata, f, indent=2)
print(f"Saved metadata to {metadata_path}")

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
