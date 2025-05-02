# visualizer.py
from pyvis.network import Network
import json
def visualize_pyvis(G, output_html="esco_graph.html"):
    print(f"[LOG] Generating interactive graph visualization: {output_html}")
    net = Network(notebook=False, directed=True, cdn_resources='in_line', height='1000px', width='200%', bgcolor='#ffffff', font_color='black')

    for node, data in G.nodes(data=True):
        label = data.get('label', node)
        node_type = data.get('type', 'unknown')
        if node_type == 'skill':
            color = "skyblue"
        elif node_type == 'skillgroup':
            color = "lightgreen"
        elif node_type == 'iscogroup':
            color = "orange"
        else:
            color = "gray"
        net.add_node(node, label=label, title=node_type, color=color, size=10)

    for src, dst, data in G.edges(data=True):
        edge_type = data.get('type', '')
        if edge_type == 'aggregates':
            net.add_edge(src, dst, label=edge_type, dashes=True, color="gray", width=0.5, font={'size': 5})
        else:
            net.add_edge(src, dst, label=edge_type, font={'size': 5})

    net.force_atlas_2based()  # Use force-directed layout to spread nodes apart
    net.set_options("""
    {
        "layout": {
            "hierarchical": {
                "enabled": false,
                "levelSeparation": 150,
                "nodeSpacing": 200,
                "treeSpacing": 200,
                "direction": "UD",
                "sortMethod": "directed"
            }
        },
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravitationalConstant": 0.1,
                "springLength": 200,
                "springConstant": 0.1
            },
            "repulsion": {
                "centralGravity": 0.1,
                "springLength": 200,
                "springConstant": 0.1,
                "damping": 0.09
            }
        }
    }
    """)

    net.write_html(output_html)
    print("[LOG] Visualization complete.")

def export_to_json(G, path="graph.json"):
    print(f"[LOG] Exporting graph to JSON file: {path}")
    data = {
        "nodes": [{"id": n, "label": d.get('label', n), "type": d.get('type', 'unknown')} for n, d in G.nodes(data=True)],
        "edges": [{"source": u, "target": v, "type": d['type']} for u, v, d in G.edges(data=True)]
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print("[LOG] Export complete.")