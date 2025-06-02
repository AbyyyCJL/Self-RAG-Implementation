# file_utils.py
import hashlib
import json
import os
from pathlib import Path
from opensearch_utils import delete_chunks_by_ids

from opensearch_utils import clear_index
# from file_utils import clear_file_tracking

from opensearch_utils import create_index

# from file_utils import compute_file_hash, is_duplicate_file, update_file_hash


TRACKING_FILE = "file_tracking.json"

# Ensure tracking file exists
def init_tracking():
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "w") as f:
            json.dump({}, f)

# Compute SHA256 hash of a file
def compute_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Load tracking data
def load_tracking():
    with open(TRACKING_FILE, "r") as f:
        return json.load(f)

# Save tracking data
def save_tracking(data):
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Check if file is duplicate or modified
def check_file_status(filepath):
    tracking = load_tracking()
    filename = Path(filepath).name
    current_hash = compute_file_hash(filepath)

    if filename in tracking:
        if tracking[filename]["hash"] == current_hash:
            return "duplicate"
        else:
            return "modified"
    return "new"

# Update file tracking metadata
def update_tracking(filepath, chunk_ids):
    tracking = load_tracking()
    filename = Path(filepath).name
    tracking[filename] = {
        "hash": compute_file_hash(filepath),
        "chunks": chunk_ids
    }
    save_tracking(tracking)

# Remove file from tracking
def delete_file_tracking(filename):
    tracking = load_tracking()
    if filename in tracking:
        del tracking[filename]
        save_tracking(tracking)

# Get list of tracked files
def get_all_tracked_files():
    return list(load_tracking().keys())

# Get chunks of a specific file
def get_chunks_by_file(filename):
    tracking = load_tracking()
    return tracking.get(filename, {}).get("chunks", [])

# Clear all tracking data
def clear_all_tracking():
    save_tracking({})


def delete_file(filename):
    tracking_data = load_tracking()
    if filename not in tracking_data:
        print(f"No record found for {filename}")
        return False

    chunk_ids = tracking_data[filename]["chunk_ids"]
    delete_chunks_by_ids(chunk_ids)

    # Remove from tracking file
    del tracking_data[filename]
    with open(TRACKING_FILE, "w") as f:
        json.dump(tracking_data, f, indent=2)

    print(f"Deleted file '{filename}' and its chunks.")
    return True


def clear_file_tracking():
    with open(TRACKING_FILE, "w") as f:
        json.dump({}, f)


def clear_entire_database():
    clear_index()
    clear_file_tracking()
    print("✔️ All files and chunks cleared.")


def compute_file_hash(file_path):
    """Generate a SHA256 hash of the file's content."""
    with open(file_path, "rb") as f:
        file_content = f.read()
    return hashlib.sha256(file_content).hexdigest()




def load_and_index_pdfs(pdf_folder="data"):
    create_index()
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            file_hash = compute_file_hash(file_path)

            if check_file_status(filename, file_hash):
                print(f"⏩ Skipping duplicate file: {filename}")
                continue

            # Process and chunk the file
            doc = fitz.open(file_path)
            for page in doc:
                text = page.get_text()
                vector = get_embedding(text)
                index_document(text, vector)

            # After successful processing, update hash
            update_file_hash(filename, file_hash)
            print(f"✅ Processed and indexed: {filename}")
