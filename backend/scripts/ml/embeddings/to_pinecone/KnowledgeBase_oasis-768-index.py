import os
import csv
from dotenv import load_dotenv
from typing import Dict
from pinecone import Pinecone  # Pinecone v3+

load_dotenv()

# === Config ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "oasis-768-index"
CSV_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/KnowlegdeBase/KnowledgeBase.csv"
BATCH_SIZE = 5
MAX_TOKENS = 2048  # Adjust this based on your model's token limit

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def truncate_text(text: str, max_tokens: int = MAX_TOKENS) -> str:
    """Truncate text to fit within token limits while preserving important information."""
    # Rough estimate of tokens (4 chars ≈ 1 token)
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return text
        
    # Split into sentences
    sentences = text.split('. ')
    
    # Keep adding sentences until we hit the limit
    truncated_text = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) <= max_chars:
            truncated_text.append(sentence)
            current_length += len(sentence)
        else:
            break
    
    return '. '.join(truncated_text) + '.'

def combine_row_text(row: Dict[str, str]) -> str:
    """Combine row data into a single text string, prioritizing important fields."""
    # Define priority order for fields
    priority_fields = [
        'oasis_code',
        'Holland Code - 1',
        'Holland Code - 2',
        'Holland Code - 3'
        'OaSIS Label - Final_x',
        'Job title text',
        'Main duties',
        'Employment requirement',
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

def process_row(row: Dict[str, str], index: int) -> Dict:
    """Process a single row and return a vector object."""
    if not row or not row.get("oasis_code"):
        return None

    text = combine_row_text(row)
    if not text:
        return None

    # Truncate text if needed
    truncated_text = truncate_text(text)
    
    # Create a shorter ID
    doc_id = f"oasis-{row.get('oasis_code', '').strip()}-{index}"
    
    return {
        "id": doc_id,
        "text": truncated_text
    }

def main():
    print(f"🚀 Upserting raw text to Pinecone index: {INDEX_NAME} (using integrated embedding)")
    total_processed = 0
    failed_rows = 0
    batch_records = []
    total_rows = 0

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)  # Convert to list to count total rows
            total_rows = len(rows)
            print(f"📊 Total rows in CSV: {total_rows}")

            for i, row in enumerate(rows):
                try:
                    vector = process_row(row, i)
                    if vector:
                        batch_records.append(vector)
                        
                        if len(batch_records) >= BATCH_SIZE:
                            try:
                                index.upsert_records(namespace="", records=batch_records)
                                total_processed += len(batch_records)
                                print(f"✅ Upserted batch of {len(batch_records)}. Total so far: {total_processed}")
                            except Exception as e:
                                print(f"❌ Batch error: {e}")
                                print(f"First record in failed batch: {batch_records[0]}")
                                failed_rows += len(batch_records)
                            batch_records = []
                
                except Exception as e:
                    print(f"❌ Error processing row {i}: {e}")
                    failed_rows += 1
                    continue

            if batch_records:
                try:
                    index.upsert_records(namespace="", records=batch_records)
                    total_processed += len(batch_records)
                    print(f"✅ Final upsert of {len(batch_records)}. Total uploaded: {total_processed}")
                except Exception as e:
                    print(f"❌ Final batch error: {e}")
                    print(f"First record in failed batch: {batch_records[0]}")
                    failed_rows += len(batch_records)

        print(f"\n📊 Processing Statistics:")
        print(f"Total rows in CSV: {total_rows}")
        print(f"Total records processed: {total_processed}")
        print(f"Failed rows: {failed_rows}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
