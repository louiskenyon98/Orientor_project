import pandas as pd
import numpy as np
import os
from pinecone import Pinecone

def build_user_vector(user_df_row, pca, encoder, scaler, ohe, embedder_model):
    # 1. Embed text
    text_fields = ['Story', 'Interests', 'Hobbies', 'Unique Quality', 'Learning Style',
                   'Favourite movie', 'Favourite Book', 'Role Model']
    text_input = " ".join(str(user_df_row[col]) for col in text_fields if pd.notnull(user_df_row[col]))
    text_vec = embedder_model.encode([text_input])[0]

    # 2. Structured vector
    struct_cat = ohe.transform([user_df_row[['Sex', 'Major', 'Country', 'Learning Style']].fillna("missing")])
    struct_num = scaler.transform([user_df_row[['Age', 'GPA', 'Year']].fillna(0)])
    struct_vec = np.hstack([struct_cat, struct_num])

    # 3. Combine + reduce
    combined = np.hstack([text_vec, struct_vec])
    reduced = pca.transform([combined])[0]
    
    return reduced


def query_oasis_index(user_vector, top_k=5, namespace=None):
    from pinecone import Pinecone

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    # index = pc.Index("oasis-minilm-index-9xr744g")
    index = pc.Index("oasis-1024-custom")

    response = index.query(vector=user_vector.tolist(), top_k=top_k, namespace=namespace, include_metadata=True)
    return response


# # Load models
# pca = joblib.load("pca_384.pkl")
# scaler = joblib.load("scaler.pkl")
# ohe = joblib.load("ohe.pkl")
# embedder = SentenceTransformer("all-MiniLM-L6-v2")

# # New user input
# user_row = users_df.iloc[0]
# user_vec = build_user_vector(user_row, pca, encoder=ohe, scaler=scaler, ohe=ohe, embedder_model=embedder)

# # Query
# results = query_oasis_index(user_vec, top_k=5)

# # Display
# for match in results["matches"]:
#     print(f"Job: {match['metadata']['job_title']} - Score: {match['score']:.2f}")
