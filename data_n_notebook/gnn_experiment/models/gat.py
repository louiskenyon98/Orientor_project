import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv

class RelationalGAT(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, heads=4, dropout=0.3):
        super().__init__()
        self.gat1 = GATConv(input_dim, hidden_dim, heads=heads, dropout=dropout)
        self.gat2 = GATConv(hidden_dim * heads, output_dim, heads=1, dropout=dropout)
        
    def forward(self, x, edge_index):
        # Get node embeddings
        x = self.gat1(x, edge_index)
        x = F.elu(x)
        x = self.gat2(x, edge_index)
        return x

class EdgeRegHead(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(dim * 2, dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(dim, dim // 2),
            torch.nn.ReLU(),
            torch.nn.Linear(dim // 2, 1),
            torch.nn.Sigmoid()
        )
    
    def forward(self, zi, zj):
        return self.mlp(torch.cat([zi, zj], dim=-1))

class CareerTreeModel(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, heads=4, dropout=0.3):
        super().__init__()
        self.gat = RelationalGAT(input_dim, hidden_dim, output_dim, heads, dropout)
        self.edge_reg = EdgeRegHead(output_dim)
        
    def forward(self, x, edge_index, edge_pairs=None):
        # Get node embeddings
        node_embeddings = self.gat(x, edge_index)
        
        if edge_pairs is not None:
            # Get embeddings for edge pairs
            zi = node_embeddings[edge_pairs[0]]
            zj = node_embeddings[edge_pairs[1]]
            # Predict edge scores
            edge_scores = self.edge_reg(zi, zj)
            return edge_scores
        
        return node_embeddings
