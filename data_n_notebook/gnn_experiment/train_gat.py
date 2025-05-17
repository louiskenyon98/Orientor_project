import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from pathlib import Path
import mlflow
import json
from itertools import product
from models.gat import GAT

# === Load Data === #
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXPERIMENT_DIR = BASE_DIR / "experiment_results"
CHECKPOINT_DIR = Path("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/gnn_experiment/experiment_results/checkpoints")
RESULTS_DIR = EXPERIMENT_DIR / "results"

# Create directories if they don't exist
EXPERIMENT_DIR.mkdir(exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)  # Ensure all parent directories are created
RESULTS_DIR.mkdir(exist_ok=True)

# Load node features and edge index
try:
    x = torch.load(DATA_DIR / "node_features.pt")
    edge_index = torch.load(DATA_DIR / "edge_index.pt")
except FileNotFoundError as e:
    raise FileNotFoundError(f"Could not find data files in {DATA_DIR}. Please ensure node_features.pt and edge_index.pt exist.") from e

# Create dummy labels for testing (replace with real labels when available)
y = torch.randint(0, 5, (x.size(0),))
train_mask = torch.rand(x.size(0)) < 0.8

# Create PyTorch Geometric data object
data = Data(x=x, edge_index=edge_index, y=y)

# === Hyperparameter Search Space === #
search_space = {
    "hidden_dim": [64, 128],
    "heads": [2, 4],
    "lr": [0.01, 0.005],
    "dropout": [0.3, 0.6],
    "weight_decay": [5e-4, 1e-3]
}

combinations = list(product(*search_space.values()))

# === MLflow Setup === #
mlflow.set_experiment("GAT_ESO_GridSearch")

for combo in combinations:
    config = dict(zip(search_space.keys(), combo))

    with mlflow.start_run():
        for k, v in config.items():
            mlflow.log_param(k, v)

        mlflow.log_param("embedding_dim", x.size(1))
        mlflow.log_param("output_dim", 5)
        mlflow.log_param("epochs", 100)

        model = GAT(
            input_dim=x.size(1),
            hidden_dim=config["hidden_dim"],
            output_dim=5,
            heads=config["heads"]
        )

        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=config["lr"],
            weight_decay=config["weight_decay"]
        )

        for epoch in range(1, 101):
            model.train()
            optimizer.zero_grad()
            out = model(data.x, data.edge_index)
            loss = F.cross_entropy(out[train_mask], data.y[train_mask])
            loss.backward()
            optimizer.step()

            if epoch % 20 == 0 or epoch == 1:
                model.eval()
                pred = out.argmax(dim=1)
                acc = (pred[train_mask] == data.y[train_mask]).float().mean().item()
                mlflow.log_metric("loss", loss.item(), step=epoch)
                mlflow.log_metric("accuracy", acc, step=epoch)
                print(f"[Combo] {config} | Epoch {epoch:03d} | Loss: {loss:.4f} | Acc: {acc:.4f}")

        mlflow.pytorch.log_model(model, "model")
