import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# === Config ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# INDEX_NAME = "oasis-minilm-index"
INDEX_NAME = "oasis-768-index"

def main():
    print(f"🗑️  Deleting all records from Pinecone index: {INDEX_NAME}")
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    
    try:
        # Delete all records from the index
        index.delete(delete_all=True)
        print("✅ Successfully deleted all records from the index")
    except Exception as e:
        print(f"❌ Error deleting records: {e}")

if __name__ == "__main__":
    main() 