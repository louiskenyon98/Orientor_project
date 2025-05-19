import networkx as nx
import pandas as pd
import torch
import json
import os
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer
import pickle


# Dictionnaire de types de relations normalisés pour RGAT
relation_types = {
    "essential": 0,
    "optional": 1,
    "requires": 2,
    "produces": 3,
    "is_parent_of": 4,
    "related": 5,
    "unknown": 6
}

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


def save_all_labeled_triplets(G, out_path):
    triplets = []
    for u, v, data in G.edges(data=True):
        edge_type = data.get("type", "unknown")
        triplets.append({
            "source": u,
            "target": v,
            "relation_type": edge_type
        })
    with open(out_path, "w") as f:
        for t in triplets:
            f.write(json.dumps(t) + "\n")
    log_progress(f"Saved {len(triplets)} total triplets to {out_path}")


def get_skill_label(esco_data, skill_id):
    skill_row = esco_data['skills'].query("ID == @skill_id")
    if not skill_row.empty:
        return clean_label(skill_row.iloc[0]['PREFERREDLABEL'])
    print(f"[WARN] Skill ID {skill_id} not found in skills.csv")
    return f"skill::{skill_id}"

def get_skill_group_label(esco_data, group_id):
    group_row = esco_data['skill_groups'].query("ID == @group_id")
    if not group_row.empty:
        return clean_label(group_row.iloc[0]['PREFERREDLABEL'])
    return f"skillgroup::{group_id}"

def get_isco_group_label(esco_data, group_id):
    if 'isco_groups' not in esco_data:
        print("[WARN] 'isco_groups' not found in esco_data.")
        return f"iscogroup::{group_id}"
    group_row = esco_data['isco_groups'].query("ID == @group_id")
    if not group_row.empty:
        return clean_label(group_row.iloc[0]['PREFERREDLABEL'])
    print(f"[WARN] ISCO Group ID {group_id} not found in isco_groups.csv")
    return f"iscogroup::{group_id}"

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
        # Ajouter l'arête skill -> occupation (flipped)
        G.add_edge(skill, occ, type=row['RELATIONTYPE'].lower())
        # Ajouter l'arête inverse occupation -> skill avec type "produces"
        G.add_edge(occ, skill, type="produces")

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
    save_all_labeled_triplets(G, "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data/esco_all_triplets.jsonl")

    end_time = time.time()
    duration = end_time - start_time
    log_progress(f"Finished building graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges in {duration:.2f} seconds.")
    return G


def export_graph_for_gnn(G, out_dir="/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/data"):
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
            # S'assurer que chaque arête a un type, utiliser "unknown" par défaut
            edge_type_name = data.get("type", "unknown")
            edge_type_id = relation_types.get(edge_type_name, relation_types["unknown"])
            edge_type.append(edge_type_id)

    features = []
    node_metadata = {}  # Store node metadata
    missing_nodes = []

    for n in G.nodes():
        if 'embedding' in G.nodes[n]:
            features.append(G.nodes[n]['embedding'])
            # Save all node attributes except embedding
            node_metadata[n] = {
                k: v for k, v in G.nodes[n].items() 
                if k != 'embedding' and not k.startswith('_')
            }
        else:
            missing_nodes.append(n)

    if missing_nodes:
        print(f"[WARN] {len(missing_nodes)} nodes missing embeddings (e.g. {missing_nodes[:3]}).")
        print("They will be excluded from the feature matrix. Ensure this is acceptable for your GNN model.")

    # Save all data files
    torch.save(torch.tensor(edge_index).t().long(), os.path.join(out_dir, "edge_index.pt"))
    torch.save(torch.tensor(features).float(), os.path.join(out_dir, "node_features.pt"))

    # Convertir les types de relations en indices numériques pour RGAT
    edge_type_indices = [relation_types.get(t, relation_types["unknown"]) for t in edge_type]

    with open(os.path.join(out_dir, "edge_type.json"), "w") as f:
        json.dump(edge_type, f)
    
    with open(os.path.join(out_dir, "edge_type_indices.json"), "w") as f:
        json.dump(edge_type_indices, f)
    
    # Sauvegarder le mapping des types de relations
    with open(os.path.join(out_dir, "relation_types.json"), "w") as f:
        json.dump(relation_types, f)
        
    # Sauvegarder le dictionnaire de types de relations dans un fichier séparé
    with open(os.path.join(out_dir, "edge_type_dict.json"), "w") as f:
        json.dump(relation_types, f)

    with open(os.path.join(out_dir, "node2idx.json"), "w") as f:
        json.dump(node2idx, f)

    with open(os.path.join(out_dir, "idx2node.json"), "w") as f:
        json.dump(idx2node, f)
        
    # Save node metadata
    with open(os.path.join(out_dir, "node_metadata.json"), "w") as f:
        json.dump(node_metadata, f, indent=2)
  
    end_time = time.time()
    duration = end_time - start_time
    log_progress(f"Exported {len(G.nodes())} nodes and {len(G.edges())} edges to '{out_dir}' in {duration:.2f} seconds")


def build_occupation_subgraph(esco_data, occupation_id, depth=1, include_groups=True, include_isco=True):
    print(f"[LOG] Building filtered graph for occupation: {occupation_id} with depth={depth}, groups={include_groups}, isco={include_isco}")
    G = nx.DiGraph()

    occ_key = f"occupation::{occupation_id}"
    occ_row = esco_data['occupations'].query("ID == @occupation_id")
    if occ_row.empty:
        print("[WARN] Occupation ID not found.")
        return G
    label = clean_label(occ_row.iloc[0]['PREFERREDLABEL'])
    G.add_node(occ_key, label=label, type='occupation')

    if include_isco and 'occupation_hierarchy' in esco_data:
        visited = set()
        to_process = [(occupation_id, occ_key)]

        while to_process:
            current_id, current_key = to_process.pop()
            for _, row in esco_data['occupation_hierarchy'].iterrows():
                if row['CHILDID'] == current_id:
                    parent_id = row['PARENTID']
                    parent_type = row['PARENTOBJECTTYPE']
                    parent_key = f"{parent_type}::{parent_id}"
                    if parent_key in visited:
                        continue
                    visited.add(parent_key)

                    if parent_type == 'iscogroup':
                        label = get_isco_group_label(esco_data, parent_id)
                    elif parent_type == 'occupation':
                        occ_row = esco_data['occupations'].query("ID == @parent_id")
                        label = clean_label(occ_row.iloc[0]['PREFERREDLABEL']) if not occ_row.empty else parent_id
                    else:
                        label = clean_label(parent_id)

                    print(f"[LOG] Adding parent node: {parent_key} ({label})")
                    ensure_node(G, parent_key, parent_type, label)
                    G.add_edge(parent_key, current_key, type='is_parent_of')
                    to_process.append((parent_id, parent_key))

                    siblings = esco_data['occupation_hierarchy'][
                        (esco_data['occupation_hierarchy']['PARENTID'] == parent_id) &
                        (esco_data['occupation_hierarchy']['CHILDOBJECTTYPE'] == 'occupation')
                    ]
                    for _, sib_row in siblings.iterrows():
                        sib_occ_id = sib_row['CHILDID']
                        sib_key = f"occupation::{sib_occ_id}"
                        occ_row = esco_data['occupations'].query("ID == @sib_occ_id")
                        if not occ_row.empty:
                            label = clean_label(occ_row.iloc[0]['PREFERREDLABEL'])
                            print(f"[LOG] Adding sibling occupation: {sib_key} ({label})")
                            ensure_node(G, sib_key, 'occupation', label)
                            G.add_edge(parent_key, sib_key, type='is_parent_of')

    # Link all visible occupations to their skills
    relations = esco_data['occupation_to_skill_relations']
    all_occ_ids = {node.split('::')[1] for node, data in G.nodes(data=True) if data['type'] == 'occupation'}
    print(f"[LOG] Linking skills for {len(all_occ_ids)} occupations...")
    related_skills = relations[relations['OCCUPATIONID'].isin(all_occ_ids)]

    for _, row in related_skills.iterrows():
        occ = f"occupation::{row['OCCUPATIONID']}"
        skill_key = f"skill::{row['SKILLID']}"
        label = get_skill_label(esco_data, row['SKILLID'])
        ensure_node(G, skill_key, 'skill', label)
        G.add_edge(occ, skill_key, type=row['RELATIONTYPE'].lower())
        # print(f"[LOG] Linked {occ} → {skill_key} ({label})")

    if depth > 0:
        queue = list(related_skills['SKILLID'])
        visited = set(queue)
        for d in range(depth):
            next_level = []
            for skill_id in queue:
                deps = esco_data['skill_to_skill_relations']
                deps = deps[deps['REQUIRINGID'] == skill_id]
                for _, row in deps.iterrows():
                    source = f"skill::{row['REQUIRINGID']}"
                    target = f"skill::{row['REQUIREDID']}"
                    if row['REQUIREDID'] not in visited:
                        next_level.append(row['REQUIREDID'])
                        visited.add(row['REQUIREDID'])
                    ensure_node(G, source, 'skill', get_skill_label(esco_data, row['REQUIRINGID']))
                    ensure_node(G, target, 'skill', get_skill_label(esco_data, row['REQUIREDID']))
                    G.add_edge(source, target, type=row['RELATIONTYPE'].lower())
            queue = next_level

    if include_groups:
        for _, row in esco_data['skill_hierarchy'].iterrows():
            parent = f"{row['PARENTOBJECTTYPE']}::{row['PARENTID']}"
            child = f"{row['CHILDOBJECTTYPE']}::{row['CHILDID']}"
            if child in G:
                ensure_node(G, parent, row['PARENTOBJECTTYPE'], get_skill_group_label(esco_data, row['PARENTID']))
                G.add_edge(parent, child, type='is_parent_of')

    print(f"[LOG] Subgraph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G