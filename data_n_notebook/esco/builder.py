
# builder.py
import networkx as nx
import pandas as pd

def clean_label(value):
    return str(value).strip() if pd.notna(value) and value != "" else "unknown"

def ensure_node(G, node_id, node_type, label=None):
    if node_id not in G:
        G.add_node(node_id, label=label or node_id, type=node_type)

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

def build_graph(esco_data):
    print("[LOG] Building graph from ESCO data...")
    G = nx.DiGraph()

    print("[LOG] Adding skills...")
    for _, row in esco_data['skills'].iterrows():
        label = clean_label(row['PREFERREDLABEL'])
        G.add_node(f"skill::{row['ID']}", label=label, type='skill')

    print("[LOG] Adding skill groups...")
    for _, row in esco_data['skill_groups'].iterrows():
        label = clean_label(row['PREFERREDLABEL'])
        G.add_node(f"skillgroup::{row['ID']}", label=label, type='skillgroup')

    print("[LOG] Adding occupations...")
    for _, row in esco_data['occupations'].iterrows():
        label = clean_label(row['PREFERREDLABEL'])
        G.add_node(f"occupation::{row['ID']}", label=label, type='occupation')

    print("[LOG] Linking skills to other skills...")
    for _, row in esco_data['skill_to_skill_relations'].iterrows():
        source = f"skill::{row['REQUIRINGID']}"
        target = f"skill::{row['REQUIREDID']}"
        ensure_node(G, source, 'skill')
        ensure_node(G, target, 'skill')
        G.add_edge(source, target, type=row['RELATIONTYPE'].lower())

    print("[LOG] Linking occupations to skills...")
    for _, row in esco_data['occupation_to_skill_relations'].iterrows():
        occ = f"occupation::{row['OCCUPATIONID']}"
        skill = f"skill::{row['SKILLID']}"
        ensure_node(G, occ, 'occupation')
        ensure_node(G, skill, 'skill')
        G.add_edge(occ, skill, type=row['RELATIONTYPE'].lower())

    print("[LOG] Adding skill hierarchy...")
    for _, row in esco_data['skill_hierarchy'].iterrows():
        parent = f"{row['PARENTOBJECTTYPE']}::{row['PARENTID']}"
        child = f"{row['CHILDOBJECTTYPE']}::{row['CHILDID']}"
        ensure_node(G, parent, row['PARENTOBJECTTYPE'])
        ensure_node(G, child, row['CHILDOBJECTTYPE'])
        G.add_edge(parent, child, type='is_parent_of')

    print("[LOG] Adding occupation hierarchy...")
    for _, row in esco_data['occupation_hierarchy'].iterrows():
        parent = f"{row['PARENTOBJECTTYPE']}::{row['PARENTID']}"
        child = f"{row['CHILDOBJECTTYPE']}::{row['CHILDID']}"
        ensure_node(G, parent, row['PARENTOBJECTTYPE'])
        ensure_node(G, child, row['CHILDOBJECTTYPE'])
        G.add_edge(parent, child, type='is_parent_of')

    print(f"[LOG] Finished building graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

def build_occupation_subgraph(esco_data, occupation_id):
    print(f"[LOG] Building filtered graph for occupation: {occupation_id}")
    G = nx.DiGraph()

    # Add occupation node
    occ_key = f"occupation::{occupation_id}"
    occ_row = esco_data['occupations'].query("ID == @occupation_id")
    if occ_row.empty:
        print("[WARN] Occupation ID not found.")
        return G
    label = clean_label(occ_row.iloc[0]['PREFERREDLABEL'])
    G.add_node(occ_key, label=label, type='occupation')

    # Add skills linked to that occupation
    relations = esco_data['occupation_to_skill_relations']
    print("[DEBUG] Sample skill label:", esco_data['skills'].iloc[0]['PREFERREDLABEL'])
    related_skills = relations[relations['OCCUPATIONID'] == occupation_id]

    for _, row in related_skills.iterrows():
        skill_key = f"skill::{row['SKILLID']}"
        skill_row = esco_data['skills'].query("ID == @row['SKILLID']")
        label = (
            clean_label(skill_row.iloc[0]['PREFERREDLABEL']) 
            if not skill_row.empty else f"skill::{row['SKILLID']}"
        )
        if skill_row.empty:
            print(f"[WARN] Skill ID {row['SKILLID']} not found in skills.csv")
        G.add_node(skill_key, label=label, type='skill')
        G.add_edge(occ_key, skill_key, type=row['RELATIONTYPE'].lower())

    # Add skill-to-skill dependencies (optional but useful for clarity)
    all_skills = set(related_skills['SKILLID'].unique())
    dependencies = esco_data['skill_to_skill_relations']
    for _, row in dependencies.iterrows():
        if row['REQUIRINGID'] in all_skills or row['REQUIREDID'] in all_skills:
            src = f"skill::{row['REQUIRINGID']}"
            tgt = f"skill::{row['REQUIREDID']}"
            ensure_node(G, src, 'skill')
            ensure_node(G, tgt, 'skill')
            G.add_edge(src, tgt, type=row['RELATIONTYPE'].lower())

    print(f"[LOG] Subgraph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G
