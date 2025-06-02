import fitz  # PyMuPDF
import os
from embedding_utils import get_embedding
from opensearch_utils import create_index, index_document, delete_chunks_by_ids
from llm_utils import ask_gemini
from file_utils import (
    compute_file_hash,
    is_duplicate,
    mark_file_uploaded,
    remove_file_chunks,
    load_file_tracking
)

DATA_DIR = "data"

def load_and_index_pdfs(pdf_folder=DATA_DIR):
    create_index()
    tracking_data = load_file_tracking()

    for filename in os.listdir(pdf_folder):
        if not filename.endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_folder, filename)
        file_hash = compute_file_hash(file_path)

        # Check if file was already uploaded with same hash
        if is_duplicate(filename, file_hash):
            print(f"Skipping duplicate file: {filename}")
            continue

        # If file exists but has changed, remove old chunks
        if filename in tracking_data:
            print(f"File {filename} modified. Removing previous chunks...")
            remove_file_chunks(filename)

        print(f"Indexing file: {filename}")
        doc = fitz.open(file_path)
        chunk_ids = []

        for page in doc:
            text = page.get_text()
            if not text.strip():
                continue

            vector = get_embedding(text)
            chunk_id = index_document(text, vector)
            chunk_ids.append(chunk_id)

        # Record the file tracking metadata
        mark_file_uploaded(filename, file_hash, chunk_ids)
        print(f"Finished indexing: {filename}")


def query_pipeline(query):
    from opensearch_utils import search_similar_docs

    q_vector = get_embedding(query)
    hits = search_similar_docs(q_vector)
    context = "\n\n".join([hit["_source"]["text"] for hit in hits])
    return ask_gemini(context, query)


if __name__ == "__main__":
    load_and_index_pdfs()

    while True:
        user_query = input("\nAsk a question (type 'exit' to quit): ")
        if user_query.lower() == "exit":
            break

        answer = query_pipeline(user_query)
        print("\nGemini:\n", answer)
