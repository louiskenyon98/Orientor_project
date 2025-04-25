import mlflow
import torch
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import pickle
import os
import numpy as np

# Config
EXPERIMENT_NAME = "JobUserSiameseMatching"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 16
EPOCHS = 2

# Load pairs
with open("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/data/siamese_pairs.pkl", "rb") as f:
    train_data = pickle.load(f)

train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
model = SentenceTransformer(MODEL_NAME)

loss = losses.CosineSimilarityLoss(model)

# MLflow setup
mlflow.set_experiment(EXPERIMENT_NAME)
with mlflow.start_run(run_name=f"{MODEL_NAME}-finetuned"):
    mlflow.log_param("base_model", MODEL_NAME)
    mlflow.log_param("batch_size", BATCH_SIZE)
    mlflow.log_param("epochs", EPOCHS)
    mlflow.log_param("train_pairs", len(train_data))

    # Train the model
    model.fit(
        train_objectives=[(train_loader, loss)],
        epochs=EPOCHS,
        show_progress_bar=True
    )

    # Compute cosine gap
    def cosine_gap(train_data, model):
        pos_scores = []
        neg_scores = []
        for ex in train_data:
            emb = model.encode(ex.texts)
            score = np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))
            if ex.label == 1.0:
                pos_scores.append(score)
            else:
                neg_scores.append(score)
        return np.mean(pos_scores) - np.mean(neg_scores)

    gap = cosine_gap(train_data, model)
    mlflow.log_metric("cosine_gap", gap)

    # Save and log the model
    model.save("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/finetuned_model")
    mlflow.log_artifacts("finetuned_model", artifact_path="model")

    print("✅ Model training complete and logged to MLflow.")
