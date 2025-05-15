from siamese_pairs import generate_siamese_pairs_from_cross_indexes
import pickle
import os
import pandas as pd

path_to_data = '/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/Synthetic_user_data'

# read df_students.csv 
users_df = pd.read_csv(f'{path_to_data}/df_students.csv')


try:
    pairs = generate_siamese_pairs_from_cross_indexes(
        users_df=users_df,
        user_index_name="recommendation-index",
        # job_index_name="oasis-minilm-index",
        job_index_name="oasis-768-index",
        top_k=5,
        num_neg=5
    )

    os.makedirs("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/data", exist_ok=True)
    with open("data/siamese_pairs.pkl", "wb") as f:
        pickle.dump(pairs, f)

    print(f"✅ Saved {len(pairs)} training pairs.")
except Exception as e:
    print(f"❌ An error occurred: {e}")