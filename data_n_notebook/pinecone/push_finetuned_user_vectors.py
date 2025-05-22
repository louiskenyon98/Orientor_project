import os
import numpy as np
import pandas as pd
import joblib
from tqdm import tqdm
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv
load_dotenv()

# Load Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("recommendation-index")

path_to_data = '/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/Synthetic_user_data'

# read df_students.csv 
users_df = pd.read_csv(f'{path_to_data}/df_students.csv')

user_ids = users_df['user_id'].astype(str).tolist()

model = SentenceTransformer("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/finetuned_model")
pca = joblib.load("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/pca384_Siamese.pkl")
ohe = joblib.load("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/ohe_Siamese.pkl")
scaler = joblib.load("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/scaler_Siamese.pkl")

# Text fields for embedding
TEXT_FIELDS = ['Story', 'interests', 'Hobbies', 'Unique Quality',
               'Learning Style', 'Favourite movie', 'Favourite Book', 'Role Model']
CATEGORICAL_FIELDS = ['Sex', 'Major', 'Country', 'Learning Style', 'Year']
NUMERIC_FIELDS = ['Age', 'GPA']

import pandas as pd

def vectorize_user(row):
    text_input = " ".join(str(row[col]) for col in TEXT_FIELDS if pd.notnull(row[col]))
    text_vec = model.encode([text_input])[0]

    # Fix: wrap as single-row DataFrame with correct columns
    cat_input = pd.DataFrame([[
        row[col] if pd.notnull(row[col]) else "missing"
        for col in CATEGORICAL_FIELDS
    ]], columns=CATEGORICAL_FIELDS)

    num_input = pd.DataFrame([[
        row[col] if pd.notnull(row[col]) else 0
        for col in NUMERIC_FIELDS
    ]], columns=NUMERIC_FIELDS)

    cat_vec = ohe.transform(cat_input)[0]
    num_vec = scaler.transform(num_input)[0]

    full_vec = np.hstack([text_vec, cat_vec, num_vec])
    reduced_vec = pca.transform([full_vec])[0]
    return reduced_vec, text_input


# Prepare batch
to_upsert = []
for i, row in tqdm(users_df.iterrows(), total=len(users_df), desc="Encoding users"):
    vec, text = vectorize_user(row)
    to_upsert.append((user_ids[i], vec.tolist(), {"user_text": text}))

# Batch upload
def batch_upsert(index, vectors, batch_size=100):
    for i in tqdm(range(0, len(vectors), batch_size), desc="Upserting to Pinecone"):
        batch = vectors[i:i + batch_size]
        index.upsert(batch)

batch_upsert(index, to_upsert)
print("✅ Finished pushing fine-tuned vectors to Pinecone.")
