import os
import csv
import hashlib
from dotenv import load_dotenv
from typing import Dict, List
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import numpy as np
from transformers import AutoTokenizer
import textwrap
# === Load environment variables ===
load_dotenv()

# === Configuration ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "oasis-1024-custom"
CSV_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/KnowlegdeBase/KnowledgeBase.csv"
BATCH_SIZE = 5
MAX_TOKENS = 512
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# === Init Pinecone and model ===
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
model = SentenceTransformer(EMBEDDING_MODEL)
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)

# === Functions ===
def estimate_token_length(text: str) -> int:
    return len(tokenizer.encode(text, truncation=False))

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

def combine_row_text(row: Dict[str, str]) -> str:
    text_parts = []
    for key, value in row.items():
        if value is not None:
            str_val = str(value).strip()
            if str_val.lower() not in {"", "nan"}:
                text_parts.append(f"{key.strip()}: {str_val}.")
    return " ".join(text_parts).strip()

def process_row(row: Dict[str, str], index: int, i: int) -> Dict:
    if not row.get("oasis_code"):
        return None

    full_text = combine_row_text(row)

    if i < 5:
        print(f"\n🧾 Row {i} full content preview:\n{textwrap.shorten(full_text, width=1500)}\n{'-'*80}")

    chunks = chunk_text(full_text)
    if not chunks:
        return None

    chunk_embeddings = [
        model.encode("passage: " + chunk, max_length=MAX_TOKENS, truncation=True)
        for chunk in chunks
    ]
    final_embedding = np.mean(chunk_embeddings, axis=0).tolist()

    raw_code = row.get("oasis_code", f"row{index}").strip()
    hash_id = hashlib.md5(raw_code.encode("utf-8")).hexdigest()[:12]
    doc_id = f"oasis-{hash_id}-{index}"

    full_text_combined = "\n".join(chunks)

    return {
        "id": doc_id,
        "values": final_embedding,
        "metadata": {
            "label": str(row.get("OaSIS Label - Final_x") or "Unknown"),
            "job_title": str(row.get("Job title text") or ""),
            "source": "KnowledgeBase",
            "text": full_text_combined
        }
    }

def main():
    print(f"\n🚀 Uploading careers to Pinecone with chunked+combined embeddings ({EMBEDDING_MODEL})")
    total_processed = 0
    failed = 0
    batch: List[Dict] = []

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"📊 Found {len(rows)} rows")

            # Optional: clear the index before inserting
            try:
                print("🧹 Clearing existing vectors from index...")
                index.delete(delete_all=True)
            except Exception as clear_err:
                print(f"⚠️ Could not clear index: {clear_err}")

            for i, row in enumerate(rows):
                try:
                    item = process_row(row, i, i)
                    if item:
                        batch.append(item)
                        if len(batch) >= BATCH_SIZE:
                            index.upsert(vectors=batch)
                            total_processed += len(batch)
                            print(f"✅ Upserted batch of {len(batch)}. Total: {total_processed}")
                            batch = []
                except Exception as e:
                    print(f"❌ Error processing row {i}: {e}")
                    failed += 1

        if batch:
            index.upsert(vectors=batch)
            total_processed += len(batch)
            print(f"✅ Final upsert of {len(batch)}. Total: {total_processed}")

        print("\n✅ Done.")
        print(f"Total processed: {total_processed}, Failed: {failed}")

    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    main()
