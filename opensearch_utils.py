import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from dotenv import load_dotenv
import os

load_dotenv()

credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, os.getenv("AWS_REGION"))

client = OpenSearch(
    hosts=[{'host': os.getenv("OPENSEARCH_ENDPOINT").replace("https://", ""), 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

INDEX_NAME = "rag-index"

# def create_index():
#     if not client.indices.exists(INDEX_NAME):
#         index_body = {
#             "settings": {
#                 "index": {
#                     "number_of_shards": 1,
#                     "number_of_replicas": 0
#                 }
#             },
#             "mappings": {
#                 "properties": {   
#                     "text": {"type": "text"},
#                     "vector": {
#                         "type": "dense_vector",
#                         "dims": 384  # depends on embedding size
#                     }
#                 }
#             }
#         }
#         client.indices.create(index=INDEX_NAME, body=index_body)

# def create_index():
#     if not client.indices.exists(INDEX_NAME):
#         index_body = {
#             "settings": {
#                 "number_of_shards": 1,
#                 "number_of_replicas": 2
#             },
#             "mappings": {
#                 "properties": {
#                     "text": {"type": "text"},
#                     "vector": {
#                         "type": "knn_vector",
#                         "dims": 384  # adjust if your embedding size is different
#                     }
#                 }
#             }
#         }
#         client.indices.create(index=INDEX_NAME, body=index_body)

def create_index():
    if not client.indices.exists(INDEX_NAME):
        index_body = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 2,
                    "knn": True  # Enable k-NN plugin
                }
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "vector": {
                        "type": "knn_vector",
                        "dimension": 384  # Use 'dimension' instead of 'dims'
                    }
                }
            }
        }
        client.indices.create(index=INDEX_NAME, body=index_body)




# def index_document(text, vector):
#     doc = {
#         "text": text,
#         "vector": vector
#     }
#     client.index(index=INDEX_NAME, body=doc)

def index_document(text, vector):
    doc = {
        "text": text,
        "vector": vector
    }
    response = client.index(index=INDEX_NAME, body=doc)
    return response["_id"]



def search_similar_docs(query_vector, k=3):
    body = {
        "size": k,
        "query": {
            "knn": {
                "vector": {
                    "vector": query_vector,
                    "k": k
                }
            }
        }
    }
    return client.search(index=INDEX_NAME, body=body)["hits"]["hits"]


def delete_chunks_by_ids(ids):
    for _id in ids:
        try:
            client.delete(index=INDEX_NAME, id=_id)
        except Exception as e:
            print(f"Error deleting ID {_id}: {e}")


def clear_index():
    if client.indices.exists(INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
    create_index()  # Recreate a fresh empty index
