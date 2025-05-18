import pickle
import sys
from pathlib import Path
import time

from loader import load_esco
from builder import build_graph, limit_graph #, build_occupation_subgraph
from visualizer import visualize_pyvis, export_to_json

from builder import export_graph_for_gnn

def search_occupations(esco_data, keyword):
    keyword = keyword.lower()
    matches = [
        (oid, label)
        for oid, label in esco_data['occupations_lookup'].items()
        if keyword in label.lower()
    ]
    return matches

def run_pipeline():
    print("[LOG] Starting ESCO pipeline...")
    start_time = time.time()
    data_dir = Path("/Users/philippebeliveau/Desktop/Notebook/Esco-Oasis/taxonomy-model-application/data-sets/csv/esco-v1.1.2")
    esco_data = load_esco(data_dir, limit=None)
    
    # Build full ESCO graph
    G_full = build_graph(esco_data)
    # SHow me the size 
    print(f"[LOG] FULL ESCO graph size: {len(G_full.nodes())} nodes, {len(G_full.edges())} edges")
    data_dir = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data"
    export_graph_for_gnn(G_full, out_dir=data_dir)
    # Save it
    with open("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/ESCO/esco_graph.pkl", "wb") as f:
        pickle.dump(G_full, f)

if __name__ == "__main__":
    run_pipeline()


