
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

    print("[LOG] Adding ISCO groups...")
    if 'isco_groups' in esco_data:
        for _, row in esco_data['isco_groups'].iterrows():
            label = clean_label(row['PREFERREDLABEL'])
            G.add_node(f"iscogroup::{row['ID']}", label=label, type='iscogroup')

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