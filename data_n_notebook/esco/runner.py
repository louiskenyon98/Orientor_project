# # runner.py
# import sys
# from pathlib import Path
# import time  # Importing time module for timer
# sys.path.append(str(Path(__file__).resolve().parent))

# # runner.py
# from pathlib import Path
# from loader import load_esco
# from builder import build_graph, limit_graph, build_occupation_subgraph
# from visualizer import visualize_pyvis, export_to_json

# def run_pipeline():
#     print("[LOG] Starting ESCO pipeline...")
#     start_time = time.time()  # Start timer
#     data_dir = Path("/Users/philippebeliveau/Desktop/Notebook/Esco-Oasis/taxonomy-model-application/data-sets/csv/esco-v1.1.2")
#     esco_data = load_esco(data_dir)
#     G = build_graph(esco_data)
#     G = limit_graph(G, max_nodes=500)
#     G = build_occupation_subgraph(esco_data, "key_17619") # key_17619, key_15156
#     visualize_pyvis(G, "esco_graph.html")
#     export_to_json(G, "esco_graph.json")
#     end_time = time.time()  # End timer
#     print(f"Pipeline executed in {end_time - start_time:.2f} seconds.")  # Print execution time

# if __name__ == "__main__":
#     run_pipeline()

# runner.py
import sys
from pathlib import Path
import time

from loader import load_esco
from builder import build_graph, limit_graph, build_occupation_subgraph
from visualizer import visualize_pyvis, export_to_json

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
    esco_data = load_esco(data_dir)

    # 🔍 Ask for user input
    keyword = input("Enter occupation keyword (e.g., 'data', 'director'): ").strip()
    matches = search_occupations(esco_data, keyword)

    if not matches:
        print(f"[ERROR] No matches found for '{keyword}'")
        return

    print("\n[SELECT] Matching occupations:")
    for i, (oid, label) in enumerate(matches):
        print(f"{i + 1:2d}. {label} ({oid})")

    choice = input("\nEnter number of desired occupation: ").strip()
    try:
        occ_id = matches[int(choice) - 1][0]
    except Exception:
        print("[ERROR] Invalid selection.")
        return

    # G = build_graph(esco_data)
    G = build_occupation_subgraph(esco_data, occ_id, depth=10, include_groups=True, include_isco=True)
    visualize_pyvis(G, "esco_graph.html")
    export_to_json(G, "esco_graph.json")
    end_time = time.time()
    print(f"[LOG] Pipeline executed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    run_pipeline()
