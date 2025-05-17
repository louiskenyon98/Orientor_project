import networkx as nx
import pandas as pd
import torch
import json
import os
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer
import pickle


MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBED_MODEL = SentenceTransformer(MODEL_NAME)

def log_progress(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def verify_embedding(embedding, node_id, count):
    if embedding is None or len(embedding) == 0:
        log_progress(f"WARNING: Empty embedding for node {node_id}")
    elif count % 1000 == 0:
        log_progress(f"Embedding shape for {node_id}: {len(embedding)} dimensions (processed {count} items)")

def clean_label(value):
    return str(value).strip() if pd.notna(value) and value != "" else "unknown"

def ensure_node(G, node_id, node_type, label=None):
    if node_id not in G:
        G.add_node(node_id, label=label or node_id, type=node_type)

def generate_formatted_text(row, node_type):
    if node_type == 'skill':
        return f"{row.get('PREFERREDLABEL', '')}: {row.get('DESCRIPTION', '')}"
    elif node_type == 'skillgroup':
        return f"{row.get('PREFERREDLABEL', '')}: {row.get('DESCRIPTION', '')}"
    elif node_type == 'occupation':
        return f"{row.get('PREFERREDLABEL', '')}: {row.get('DESCRIPTION', '')} {row.get('DEFINITION', '')}"
    elif node_type == 'iscogroup':
        return f"{row.get('PREFERREDLABEL', '')}: {row.get('DESCRIPTION', '')}"
    else:
        return row.get('PREFERREDLABEL', '')

def limit_graph(G, max_nodes):
    if len(G) <= max_nodes:
        return G
    print(f"[LOG] Limiting graph to {max_nodes} nodes...")
    H = nx.DiGraph()
    for i, (node, data) in enumerate(G.nodes(data=True)):
        if i >= max_nodes:
            break
        H.add_node(node, **data)
    for u, v, d in G.edges(data=True):
        if u in H and v in H:
            H.add_edge(u, v, **d)
    return H

def save_labeled_skill_occ_pairs(G, out_path):
    triplets = []
    for u, v, data in G.edges(data=True):
        if (
            G.nodes[u]["type"] == "skill"
            and G.nodes[v]["type"] == "occupation"
            and data.get("type") in {"essential", "optional"}
        ):
            triplets.append({
                "skill": u,
                "occupation": v,
                "relation_type": data["type"]
            })

    with open(out_path, "w") as f:
        for t in triplets:
            f.write(json.dumps(t) + "\n")
    log_progress(f"Saved {len(triplets)} skill→occupation triplets to {out_path}")

def build_graph(esco_data):
    start_time = time.time()
    log_progress("Building graph from ESCO data...")
    G = nx.DiGraph()

    def add_embedded_node(row, node_type, node_id):
        text = generate_formatted_text(row, node_type)
        embedding = EMBED_MODEL.encode(text)
        verify_embedding(embedding, node_id, -1)
        return embedding.tolist()

    def add_node_with_logging(row, node_type, label_key, counter=None):
        node_id = f"{node_type}::{row['ID']}"
        embedding = add_embedded_node(row, node_type, node_id)
        node_data = {
            "label": clean_label(row[label_key]),
            "type": node_type,
            "embedding": embedding
        }
        for k, v in row.items():
            if k != "ID":
                node_data[k.lower()] = v
        G.add_node(node_id, **node_data)
        if counter is not None and counter % 100 == 0:
            log_progress(f"Processed {counter} {node_type}s...")

    log_progress("Adding skills...")
    for i, row in enumerate(esco_data['skills'].iterrows()):
        add_node_with_logging(row[1], 'skill', 'PREFERREDLABEL', i)

    log_progress("Adding skill groups...")
    for i, row in enumerate(esco_data['skill_groups'].iterrows()):
        add_node_with_logging(row[1], 'skillgroup', 'PREFERREDLABEL', i)

    log_progress("Adding occupations...")
    for i, row in enumerate(esco_data['occupations'].iterrows()):
        add_node_with_logging(row[1], 'occupation', 'PREFERREDLABEL', i)

    log_progress("Adding ISCO groups...")
    if 'isco_groups' in esco_data:
        for i, row in enumerate(esco_data['isco_groups'].iterrows()):
            add_node_with_logging(row[1], 'iscogroup', 'PREFERREDLABEL', i)

    log_progress("Linking skills to other skills...")
    for _, row in esco_data['skill_to_skill_relations'].iterrows():
        source = f"skill::{row['REQUIRINGID']}"
        target = f"skill::{row['REQUIREDID']}"
        ensure_node(G, source, 'skill')
        ensure_node(G, target, 'skill')
        G.add_edge(source, target, type=row['RELATIONTYPE'].lower())

    log_progress("Linking occupations to skills...")
    for _, row in esco_data['occupation_to_skill_relations'].iterrows():
        occ = f"occupation::{row['OCCUPATIONID']}"
        skill = f"skill::{row['SKILLID']}"
        ensure_node(G, occ, 'occupation')
        ensure_node(G, skill, 'skill')
        G.add_edge(skill, occ, type=row['RELATIONTYPE'].lower())  # flipped

    log_progress("Adding skill hierarchy...")
    for _, row in esco_data['skill_hierarchy'].iterrows():
        parent = f"{row['PARENTOBJECTTYPE']}::{row['PARENTID']}"
        child = f"{row['CHILDOBJECTTYPE']}::{row['CHILDID']}"
        ensure_node(G, parent, row['PARENTOBJECTTYPE'])
        ensure_node(G, child, row['CHILDOBJECTTYPE'])
        G.add_edge(parent, child, type='is_parent_of')

    log_progress("Adding occupation hierarchy...")
    for _, row in esco_data['occupation_hierarchy'].iterrows():
        parent = f"{row['PARENTOBJECTTYPE']}::{row['PARENTID']}"
        child = f"{row['CHILDOBJECTTYPE']}::{row['CHILDID']}"
        ensure_node(G, parent, row['PARENTOBJECTTYPE'])
        ensure_node(G, child, row['CHILDOBJECTTYPE'])
        G.add_edge(parent, child, type='is_parent_of')

    save_labeled_skill_occ_pairs(G, out_path="/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data/esco_labeled_triplets.jsonl")

    end_time = time.time()
    duration = end_time - start_time
    log_progress(f"Finished building graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges in {duration:.2f} seconds.")
    return G


def export_graph_for_gnn(G, out_dir):
    start_time = time.time()
    log_progress("Exporting graph for GNN training...")
    os.makedirs(out_dir, exist_ok=True)

    valid_nodes = [n for n in G.nodes() if 'embedding' in G.nodes[n]]
    node2idx = {node: idx for idx, node in enumerate(valid_nodes)}
    idx2node = {idx: node for node, idx in node2idx.items()}

    edge_index = []
    edge_type = []
    for u, v, data in G.edges(data=True):
        if u in node2idx and v in node2idx:
            edge_index.append([node2idx[u], node2idx[v]])
            edge_type.append(data.get("type", "unknown"))

    features = []
    missing_nodes = []

    for n in G.nodes():
        if 'embedding' in G.nodes[n]:
            features.append(G.nodes[n]['embedding'])
        else:
            missing_nodes.append(n)

    if missing_nodes:
        print(f"[WARN] {len(missing_nodes)} nodes missing embeddings (e.g. {missing_nodes[:3]}).")
        print("They will be excluded from the feature matrix. Ensure this is acceptable for your GNN model.")

    torch.save(torch.tensor(edge_index).t().long(), os.path.join(out_dir, "edge_index.pt"))
    torch.save(torch.tensor(features).float(), os.path.join(out_dir, "node_features.pt"))

    with open(os.path.join(out_dir, "edge_type.json"), "w") as f:
        json.dump(edge_type, f)

    with open(os.path.join(out_dir, "node2idx.json"), "w") as f:
        json.dump(node2idx, f)

    with open(os.path.join(out_dir, "idx2node.json"), "w") as f:
        json.dump(idx2node, f)
  
    end_time = time.time()
    duration = end_time - start_time
    log_progress(f"Exported {len(G.nodes())} nodes and {len(G.edges())} edges to '{out_dir}' in {duration:.2f} seconds")
