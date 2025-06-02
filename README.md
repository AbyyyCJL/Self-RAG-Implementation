# Self-RAG: A Self-Reflective Retrieval-Augmented Generation System with Streamlit UI

---

## 🧠 Introduction

**Self-RAG** is an advanced Retrieval-Augmented Generation (RAG) system that enhances standard pipelines with **self-reflection** to reduce hallucinations and improve factual accuracy. Users can upload PDFs, ask questions, and get refined answers generated through a two-step Gemini LLM process: initial generation and self-critique.

---

## 🎯 Objective

- Users can upload one or more PDF documents.
- Documents are parsed, chunked, embedded, and indexed in OpenSearch.
- User queries are matched against relevant chunks.
- Gemini LLM generates a first answer → critiques it → returns improved response.
- All interactions occur via a user-friendly **Streamlit UI**.

---

## 🛠️ Technologies Used

| Component          | Technology Used                                |
|--------------------|-------------------------------------------------|
| UI                 | Streamlit                                       |
| PDF Parsing        | PyMuPDF (`fitz`)                                |
| Embedding Model    | `sentence-transformers` (MiniLM-L6-v2)          |
| Vector Database    | Amazon OpenSearch (k-NN plugin)                 |
| LLM                | Gemini 1.5 Flash (Google Generative AI API)     |
| Self-Reflection    | Gemini + Critique Prompting                     |
| Cloud Auth         | Boto3, AWSV4SignerAuth                          |
| Env Configuration  | python-dotenv                                   |

---

## 🧱 Architecture

![alt text](https://github.com/AbyyyCJL/Self-RAG-Implementation/blob/main/img/Final_Self-RAG_Architecture.drawio.png)

---

## ✅ Features

- **Multi-PDF Upload & Indexing**: Upload and index multiple PDFs.
- **Duplicate Detection**: Uses SHA-256 hashes to prevent re-indexing same files.
- **Self-Reflective RAG Pipeline**: Generates → Critiques → Improves responses.
- **Reasoning & Verdict Tokens**: Adds self-evaluation logic to improve trustworthiness.
- **Streamlit Chat Interface**: Clean UI with session history and chat memory.
- **Index Management**: Delete specific files or clear entire index from sidebar.

---

## 🧩 Implementation Details

### 📄 `app.py`

- Streamlit frontend and UI control.
- File uploads, query submission, chat memory, and answer display.

### 🧠 `embedding_utils.py`

- Loads the MiniLM embedding model. 

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    return model.encode(text).tolist()
```

### 🔍 `opensearch_utils.py`

- Handles OpenSearch indexing and search operations. 
- Secure access via AWS credentials and AWSV4SignerAuth.

Key functions:

- ```create_index()```
- ```index_document()```
- ```search_similar_docs()```
- ```delete_documents_by_file_hash()```
- ```clear_index()```

### 🤖 `llm_utils.py`

- Uses Gemini 1.5 Flash in a 3-step refinement pipeline:

```python
# Step 1: Initial Answer
answer_prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
initial_answer = gemini.generate_content(answer_prompt)

# Step 2: Critique
critique_prompt = f"Reason whether the answer is accurate.\nContext: {context}\nAnswer: {initial_answer}"
critique = gemini.generate_content(critique_prompt)

# Step 3: Final Answer
final_prompt = f"Revise the answer based on the critique.\nCritique: {critique}\nAnswer: {initial_answer}"
final_answer = gemini.generate_content(final_prompt)
```

### 🔐 .env (Sample Variables)

```text
GEMINI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
OPENSEARCH_ENDPOINT=
```

### 🔄 Sample Workflow

1. Upload PDFs: e.g., terms.pdf, policy.pdf.
2. Indexing: Documents are parsed, chunked, and embedded.
3. Ask Question: "What is the refund process?"
4. Retrieve Chunks: Top-3 similar chunks fetched via OpenSearch.
5. Generate → Critique → Improve:
6.   Gemini generates initial answer.
7.   Gemini critiques it.
8.   Final revised answer is presented.
9. Display Answer: Response shown in Streamlit chat interface.

### 🔐 Security & Performance

🔒 **AWS Authentication**: Secure access with .env and AWS IAM roles. 

♻️ **Deduplication**: File hashes avoid unnecessary reprocessing. 

🚀 **Scalability**: Modular components enable horizontal scaling. 

⚙️ **Decoupled Architecture**: Embedding, retrieval, and LLM generation are loosely coupled for extensibility. 

### 🔗 Component Summary

| Component      | Technology                     | Role                                       |
| -------------- | ------------------------------ | ------------------------------------------ |
| UI             | Streamlit                      | Upload, Query, Answer Interface            |
| Embedding      | Sentence-Transformers (MiniLM) | Embed document chunks and user queries     |
| Vector Store   | Amazon OpenSearch              | Store and retrieve similar document chunks |
| LLM + Self-RAG | Gemini 1.5 Flash               | Generate → Critique → Improve answers      |

