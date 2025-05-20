import os
import json
import hashlib
import torch
from dotenv import load_dotenv
from typing import Dict, List
from pinecone import Pinecone
import numpy as np

# === Load environment variables ===
load_dotenv()

# === Configuration ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "esco-368"
BATCH_SIZE = 100

# Paths to data files
NODE_FEATURES_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data/node_features.pt"
NODE_METADATA_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data/node_metadata.json"
NODE2IDX_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data/node2idx.json"

# === Init Pinecone ===
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def load_data():
    """Load node features, metadata, and node2idx mapping."""
    print("Loading node features...")
    node_features = torch.load(NODE_FEATURES_PATH)
    
    print("Loading node metadata...")
    with open(NODE_METADATA_PATH, 'r') as f:
        node_metadata = json.load(f)
    
    print("Loading node2idx mapping...")
    with open(NODE2IDX_PATH, 'r') as f:
        node2idx = json.load(f)
    
    return node_features, node_metadata, node2idx

def process_node(node_id: str, features: torch.Tensor, metadata: Dict, debug: bool = False) -> Dict:
    """Process a single node into Pinecone format."""
    # Ensure node_id is in one of the valid formats
    valid_prefixes = ['skill::key_', 'occupation::key_', 'iscogroup::key_']
    if not any(node_id.startswith(prefix) for prefix in valid_prefixes):
        print(f"⚠️ Unexpected node_id format: {node_id}")
        return None
    
    # Use the original node_id directly
    doc_id = node_id
    
    # Convert features to list format
    feature_vector = features.tolist()
    
    # Log the first few nodes for debugging
    if debug:
        print(f"Processing node: {node_id}")
        print(f"Metadata: {metadata}")
    
    return {
        "id": doc_id,
        "values": feature_vector,
        "metadata": {
            "node_id": node_id,
            **metadata  # Include all metadata fields
        }
    }

def main():
    print(f"\n🚀 Uploading ESCO node features to Pinecone")
    total_processed = 0
    failed = 0
    batch: List[Dict] = []

    try:
        # Load all data
        node_features, node_metadata, node2idx = load_data()
        
        # Clear existing vectors
        try:
            print("🧹 Clearing existing vectors from index...")
            index.delete(delete_all=True)
        except Exception as clear_err:
            print(f"⚠️ Could not clear index: {clear_err}")

        # Process nodes in batches
        for node_id, idx in node2idx.items():
            try:
                features = node_features[idx]
                metadata = node_metadata.get(node_id, {})
                
                # Pass debug=True for the first 5 nodes
                debug = total_processed < 5
                item = process_node(node_id, features, metadata, debug)
                if item:
                    batch.append(item)
                    
                    if len(batch) >= BATCH_SIZE:
                        index.upsert(vectors=batch)
                        total_processed += len(batch)
                        print(f"✅ Upserted batch of {len(batch)}. Total: {total_processed}")
                        batch = []
                        
            except Exception as e:
                print(f"❌ Error processing node {node_id}: {e}")
                failed += 1

        # Upload remaining batch
        if batch:
            index.upsert(vectors=batch)
            total_processed += len(batch)
            print(f"✅ Final upsert of {len(batch)}. Total: {total_processed}")

        print("\n✅ Done.")
        print(f"Total processed: {total_processed}, Failed: {failed}")

    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    main()
