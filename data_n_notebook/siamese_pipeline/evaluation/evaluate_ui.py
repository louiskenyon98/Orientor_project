import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from pinecone import Pinecone
import os

# to run: streamlit run evaluate_ui.py

# Load models
ft_model = SentenceTransformer("/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/siamese_pipeline/mlruns/models/finetuned_model")
base_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Pinecone index
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# index = pc.Index("oasis-minilm-index")
index = pc.Index("oasis-768-index")

# User input
st.title("🧠 Job Matching Evaluation")
story = st.text_area("User Story", "I enjoy solving problems with design and technology.")
interests = st.text_input("Interests", "UX design, storytelling, software engineering")
submit = st.button("Evaluate Matches")

def build_vector(model, text):
    return model.encode([text])[0]

def get_matches(vec, top_k=5):
    return index.query(vector=vec.tolist(), top_k=top_k, include_metadata=True)["matches"]

def build_job_text(meta):
    if not meta:
        return "❓ No metadata"

    # If packed inside 'text', parse manually
    if "text" in meta:
        full_text = meta["text"]

        # Try to extract "Job title text"
        title_part = full_text.split("Job title text:")[-1]
        title = title_part.split(". Main duties:")[0].strip() if "Main duties:" in title_part else title_part.strip()

        # Try to extract "Main duties"
        if "Main duties:" in full_text:
            duties_part = full_text.split("Main duties:")[-1]
            duties = duties_part.split(". OaSIS Label - Final_y:")[0].strip() if "OaSIS Label - Final_y:" in duties_part else duties_part.strip()
        else:
            duties = ""

        # Return clean
        if not title and not duties:
            return "❓ No job title available"
        elif title and duties:
            return f"{title} — {duties}"
        else:
            return title or duties

    else:
        # fallback if 'text' not found
        return "❓ No text field found"


def display_jobs(title, matches):
    st.subheader(title)
    for i, match in enumerate(matches):
        raw_metadata = match.get("metadata", {})
        job_text = build_job_text(raw_metadata)
        # st.write(match["metadata"])

        st.markdown(f"**{i+1}. {job_text}**")
        rating = st.slider(f"Relevance score for match #{i+1} (1=bad, 5=great)", 1, 5, key=f"{title}-{i}")
        feedback.append({
            "model": title,
            "job_text": job_text,
            "score": match["score"],
            "rating": rating
        })

if submit:
    full_text = f"{story} {interests}"
    ft_vec = build_vector(ft_model, full_text)
    base_vec = build_vector(base_model, full_text)

    feedback = []

    ft_matches = get_matches(ft_vec)
    base_matches = get_matches(base_vec)

    display_jobs("Fine-Tuned Model", ft_matches)
    display_jobs("Pretrained Model", base_matches)

    if st.button("✅ Submit Ratings"):
        df = pd.DataFrame(feedback)
        df.to_csv("annotations.csv", mode="a", index=False, header=not os.path.exists("annotations.csv"))
        st.success("Thank you! Ratings saved.")

