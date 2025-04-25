import os
from tqdm import tqdm
from pinecone import Pinecone
from sentence_transformers import InputExample
import numpy as np
import random
from pinecone import FetchResponse
import os
import random

def build_job_text(meta):
    title = meta.get("Job title text", "")
    duties = meta.get("Main duties", "")
    return f"{title.strip()} — {duties.strip()}"

def generate_siamese_pairs_from_cross_indexes(users_df, user_index_name, job_index_name, top_k=5, num_neg=5):
    """
    The generate_siamese_pairs_from_cross_indexes() function creates training 
    data for a SiameseBERT-style model by generating positive and negative user-job
    pairs based on vector similarity from two Pinecone indexes:
    - user_index_name: The name of the Pinecone index containing user vectors
    - job_index_name: The name of the Pinecone index containing job vectors
    - top_k: The number of positive matches to retrieve for each user
    - num_neg: The number of negative matches to retrieve for each user
    """
    
    print("🚀 Starting pair generation...")

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("❌ PINECONE_API_KEY not found in environment variables")

    pc = Pinecone(api_key=api_key)
    user_index = pc.Index(user_index_name)
    job_index = pc.Index(job_index_name)

    user_ids = users_df["user_id"].astype(str).tolist()
    print(f"🔎 Loaded {len(user_ids)} user IDs from users_df")

    training_data = []
    total_skipped = 0
    total_users = 0
    total_pos = 0
    total_neg = 0

    for uid in tqdm(user_ids, desc="Generating pairs"):
        total_users += 1
        try:
            # Fetch user vector
            res = user_index.fetch(ids=[uid])
            if not hasattr(res, "vectors") or uid not in res.vectors:
                print(f"⚠️ User {uid} missing in Pinecone index — skipped")
                total_skipped += 1
                continue

            vec_data = res.vectors[uid]
            user_vec = vec_data.values
            user_text = vec_data.metadata.get("user_text", "") if vec_data.metadata else ""

            if not user_vec or not user_text.strip():
                print(f"⚠️ Missing vector or metadata for user {uid}")
                total_skipped += 1
                continue

            # Query jobs
            job_matches = job_index.query(vector=user_vec, top_k=top_k + num_neg, include_metadata=True)
            matches = job_matches.get("matches", [])

            if not matches:
                print(f"⚠️ No job matches for user {uid}")
                total_skipped += 1
                continue

            pos_added = 0
            for match in matches[:top_k]:
                job_text = build_job_text(match["metadata"])
                if job_text.strip():
                    training_data.append(InputExample(texts=[user_text, job_text], label=1.0))
                    pos_added += 1
                    total_pos += 1
            if pos_added == 0:
                print(f"⚠️ No valid positive pairs for user {uid}")

            neg_added = 0
            neg_pool = matches[top_k:]
            random.shuffle(neg_pool)
            for match in neg_pool[:num_neg]:
                job_text = build_job_text(match["metadata"])
                if job_text.strip():
                    training_data.append(InputExample(texts=[user_text, job_text], label=0.0))
                    neg_added += 1
                    total_neg += 1
            if neg_added == 0:
                print(f"⚠️ No valid negative pairs for user {uid}")

            # print(f"✅ User {uid}: +{pos_added} / -{neg_added}")

        except Exception as e:
            print(f"❌ Error processing user {uid}: {e}")
            total_skipped += 1
            continue

    print("\n🎯 Pair generation complete")
    print(f"👤 Total users processed: {total_users}")
    print(f"✅ Users matched: {total_users - total_skipped}")
    print(f"❌ Users skipped: {total_skipped}")
    print(f"📦 Positive pairs: {total_pos}")
    print(f"📦 Negative pairs: {total_neg}")
    print(f"🔢 Total training pairs: {len(training_data)}")

    return training_data
