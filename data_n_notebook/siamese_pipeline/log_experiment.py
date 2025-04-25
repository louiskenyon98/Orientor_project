import mlflow

mlflow.set_experiment("JobUserSiameseMatching")

with mlflow.start_run(run_name="manual_model_upload"):
    mlflow.log_artifacts(
        local_dir="/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/finetuned_model",
        artifact_path="model"
    )

print("✅ Model logged to MLflow. Your local model remains safe and unchanged.")
