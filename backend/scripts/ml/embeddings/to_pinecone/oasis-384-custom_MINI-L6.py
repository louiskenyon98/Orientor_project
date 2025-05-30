import os
import csv
import hashlib
import textwrap
from dotenv import load_dotenv
from typing import Dict, List
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import numpy as np

# === Load environment variables ===
load_dotenv()

# === Configuration ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "oasis-384-custom"
CSV_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/KnowlegdeBase/KnowledgeBase.csv"
BATCH_SIZE = 5
MAX_TOKENS = 512
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# === Init Pinecone and model ===
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
model = SentenceTransformer(EMBEDDING_MODEL)
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)

# === Helper Functions ===
def combine_row_text(row: Dict[str, str]) -> str:
    """Combine row data into a single text string, prioritizing important fields."""
    # Define priority order for fields
    priority_fields = [
        'oasis_code',
        'OaSIS Label - Final_x',  # Ensure this is included
        'Job title text',
        'Main duties',
        'Employment requirement',
        'top_3_code'  # Add any other fields you want to prioritize
    ]
    
    text_parts = []
    
    # First add priority fields
    for field in priority_fields:
        if field in row and row[field] and str(row[field]).strip() not in {"", "nan"}:
            text_parts.append(f"{field}: {row[field]}")
    
    # Then add remaining fields
    for key, value in row.items():
        if key not in priority_fields and value and str(value).strip() not in {"", "nan"}:
            text_parts.append(f"{key}: {value}")

    return ". ".join(text_parts).strip()

def process_row(row: Dict[str, str], index_num: int, i: int) -> Dict:
    if not row.get("oasis_code"):
        return None

    full_text = combine_row_text(row)

    if i < 5:
        print(f"\n🧾 Row {i} preview:\n{textwrap.shorten(full_text, width=1500)}\n{'-'*80}")

    embedding = model.encode(
        f"passage: {full_text}", max_length=MAX_TOKENS, truncation=True
    ).tolist()

    raw_code = row.get("oasis_code", f"row{index_num}").strip()
    hash_id = hashlib.md5(raw_code.encode("utf-8")).hexdigest()[:12]
    doc_id = f"oasis-{hash_id}-{index_num}"

    # Ensure riasec is not null
    riasec = row.get("top_3_code", "N/A").strip()
    if not riasec:
        riasec = "N/A"  # Set a default value if riasec is empty or None

    return {
        "id": doc_id,
        "values": embedding,
        "metadata": {
            "label": str(row.get("OaSIS Label - Final_x") or "Unknown"),
            "job_title": str(row.get("Job title text") or ""),
            "riasec": riasec,  # Use the validated riasec value
            "source": "KnowledgeBase",
            "text": full_text
        }
    }

def main():
    print(f"\n🚀 Uploading careers to Pinecone with structured embeddings ({EMBEDDING_MODEL})")
    total_processed = 0
    failed = 0
    batch: List[Dict] = []

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"📊 Found {len(rows)} rows")

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
