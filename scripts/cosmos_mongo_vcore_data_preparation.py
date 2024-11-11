"""Data Preparation Script for an Azure Cognitive Search Index.
This script connects to a Cosmos DB with MongoDB API, validates existing database/collection, 
and sets up a vector search index if needed. It processes documents using Azure Form Recognizer 
and populates the search index with document embeddings.
"""
import argparse
import json
import os
import uuid

import requests
from data_utils import Document
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureCliCredential
from pymongo.mongo_client import MongoClient
from typing import List

from data_utils import chunk_directory

SUPPORTED_LANGUAGE_CODES = {
    "ar": "Arabic",
    "hy": "Armenian",
    "eu": "Basque",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "zh-Hans": "Chinese Simplified",
    "zh-Hant": "Chinese Traditional",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "fi": "Finnish",
    "fr": "French",
    "gl": "Galician",
    "de": "German",
    "el": "Greek",
    "hi": "Hindi",
    "hu": "Hungarian",
    "id": "Indonesian (Bahasa)",
    "ga": "Irish",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lv": "Latvian",
    "no": "Norwegian",
    "fa": "Persian",
    "pl": "Polish",
    "pt-Br": "Portuguese (Brazil)",
    "pt-Pt": "Portuguese (Portugal)",
    "ro": "Romanian",
    "ru": "Russian",
    "es": "Spanish",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish"
}

def check_if_cosmos_mongo_db_exists(
    account_name: str,
    subscription_id: str,
    resource_group: str,
    credential = None):
    """
    Checks if a Cosmos MongoDB database exists.

    Args:
        account_name (str): _description_
        database_name (str): _description_
        subscription_id (str): _description_
        resource_group (str): _description_
        credential: Azure credential to use for getting acs instance
    """
    # Raise an error if no credential is provided
    if credential is None:
        raise ValueError("credential cannot be None")
    # Construct the API endpoint URL for Cosmos DB account existence check
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.DocumentDB"
        f"/mongoClusters/{account_name}?api-version=2023-03-01-preview"
    )   
    # Define headers, including authentication token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credential.get_token('https://management.azure.com/.default').token}",
    }
    # Send GET request to Azure management API to check if the Cosmos DB account exists
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def create_or_update_vector_search_index(
        mongo_client: MongoClient,
        database_name: str,
        collection_name: str,
        index_name,
        vector_field, 
        credential, 
        language):
    """
    Creates or updates a vector search index in Cosmos MongoDB.

    Args:
        mongo_client (MongoClient): MongoDB client instance.
        database_name (str): Database name.
        collection_name (str): Collection name.
        index_name (str): Index name for vector search.
        vector_field (str): Field for vector indexing.
    """
    
     # Ensure a credential is provided, otherwise raise an error
    if credential is None:
        raise ValueError("credential cannot be None")

    try: 
        # Check if the specified database and collection exist
        dbs=mongo_client.list_database_names()
        if (database_name in dbs):
            print(f"database {database_name} exist")
            collections=mongo_client[database_name].list_collection_names()
            if (collection_name in collections):
                print(f"collection {collection_name} exist")

         # Retrieve collection and check for existing index with specified name
        mongo_collection = mongo_client[database_name][collection_name]  
        indexes = mongo_collection.index_information()
        if (indexes.get(index_name) == None):
            # Ensure the vector index exists.
            indexDefs:List[any] = [
                { "name": index_name, "key": { vector_field: "cosmosSearch" }, "cosmosSearchOptions": { "kind": "vector-ivf", "similarity": "COS", "dimensions": 1536 } }
            ]
            mongo_client[database_name].command("createIndexes", collection_name, indexes = indexDefs)
    except Exception as e:
        raise Exception(
            f"Failed to create vector index {index_name} for collection {collection_name} under database {database_name}. Error: {str(e)}")
    return True

def initialize_mongo_client(
        connection_string: str) -> MongoClient:
    """
    Initializes a MongoDB client using the specified connection string.

    Args:
        connection_string (str): Connection string for MongoDB.

    Returns:
        MongoClient: A MongoDB client instance.
    """
    return MongoClient(connection_string)
     
def upsert_documents_to_index(
        mongo_client: MongoClient,
        database_name: str,
        collection_name: str,
        docs: List[Document]
        ):
    """
    Inserts or updates documents in the Cosmos MongoDB collection.

    Args:
        mongo_client (MongoClient): MongoDB client instance.
        docs (List[Document]): Documents to upsert.
    """
      # Loop over each document and insert into the collection
    for document in docs:
        finalDocChunk:dict = {}
        finalDocChunk["_id"] = f"doc:{uuid.uuid4()}"
        finalDocChunk['title'] = document.title
        finalDocChunk["filepath"] = document.filepath
        finalDocChunk["url"] = document.url
        finalDocChunk["content"] = document.content
        finalDocChunk["contentvector"] = document.contentVector
        finalDocChunk["metadata"] = document.metadata

        mongo_collection = mongo_client[database_name][collection_name]

        # Attempt to upsert the document
        try:
            mongo_collection.insert_one(finalDocChunk)
            print(f"Upsert doc chunk {document.id} successfully")
        
        except Exception as e:
            print(f"Failed to upsert doc chunk {document.id}")
            continue

def validate_index(
        mongo_client: MongoClient,
        database_name: str,
        collection_name: str,
        index_name):
    """
    Validates if the specified vector search index exists in the collection.

    Args:
        mongo_client (MongoClient): MongoDB client instance.
        database_name (str): Name of the database.
        collection_name (str): Name of the collection.
        index_name (str): Name of the index to validate.

    Raises:
        Exception: If the index does not exist or an error occurs during validation.
    """
    try:
         # Retrieve collection and check for specified index
        mongo_collection = mongo_client[database_name][collection_name]  
        indexes = mongo_collection.index_information()
        if (indexes.get(index_name) == None):
            raise Exception(
                f"Failed to create vector index {index_name} for collection {collection_name} under database {database_name}. Error: {str(e)}")

    except Exception as e:
        raise Exception(
            f"Failed to validate vector index {index_name} for collection {collection_name} under database {database_name}. Error: {str(e)}")  

def create_index(config, credential, form_recognizer_client=None, embedding_model_endpoint=None, use_layout=False, njobs=4):
    """
    Creates or updates a vector search index in a Cosmos MongoDB, processes data, and upserts documents.

    Args:
        config (dict): Configuration settings including database/collection details.
        credential: Azure credential for API authentication.
        form_recognizer_client (optional): Form Recognizer client instance for PDF processing.
        embedding_model_endpoint (str, optional): URL for embedding model endpoint.
        use_layout (bool): Use the Layout model in Form Recognizer if True; otherwise, use Read model.
        njobs (int): Number of parallel jobs for processing.

    Raises:
        Exception: If the Cosmos MongoDB account or index creation fails.
    """
     # Extract settings from the configuration
    account_name = config["account_name"]
    database_name = config["database_name"]
    collection_name = config["collection_name"]
    subscription_id = config["subscription_id"]
    resource_group = config["resource_group"]
    index_name = config["index_name"]
    vector_field = config["vector_field"]
    language = config.get("language", None)

    # Validate the language setting if provided
    if language and language not in SUPPORTED_LANGUAGE_CODES:
        raise Exception(f"ERROR: Ingestion does not support {language} documents. "
                        f"Please use one of {SUPPORTED_LANGUAGE_CODES}."
                        f"Language is set as two letter code for e.g. 'en' for English."
                        f"If you do not want to set a language just remove this prompt config or set as None")


    # check if cosmos mongo vcore database account exists
    if check_if_cosmos_mongo_db_exists(account_name, subscription_id, resource_group, credential):
        print(f"Using existing cosmos vcore database account {account_name}")
    else:
        # Won't create the database account automatically for user since it needs set admin password
        raise Exception(f"Database account {account_name} doesn't exist. Please follow this page https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/quickstart-portal to create the resource")

    # Initialize Cosmos Mongo Client
    mongo_client = initialize_mongo_client(config.get("connection_string"))

    # create or update vector search index with compatible schema
    if not create_or_update_vector_search_index(mongo_client, database_name, collection_name, index_name, vector_field, credential, language):
        raise Exception(f"Failed to create or update index {index_name}")
    
    # chunk directory
    print("Chunking directory...")
    add_embeddings = True

    # Process files to generate chunks
    result = chunk_directory(config["data_path"], num_tokens=config["chunk_size"], token_overlap=config.get("token_overlap",0),
                             azure_credential=credential, form_recognizer_client=form_recognizer_client, use_layout=use_layout, njobs=njobs,
                             add_embeddings=add_embeddings, embedding_endpoint=embedding_model_endpoint)

    # Check if any chunks were generated; if not, raise an error
    if len(result.chunks) == 0:
        raise Exception("No chunks found. Please check the data path and chunk size.")

    print(f"Processed {result.total_files} files")
    print(f"Unsupported formats: {result.num_unsupported_format_files} files")
    print(f"Files with errors: {result.num_files_with_errors} files")
    print(f"Found {len(result.chunks)} chunks")

    # upsert documents to index
    print("Upserting documents to index...")
    upsert_documents_to_index(mongo_client, database_name, collection_name, result.chunks)

    # check if index is ready/validate index
    print("Validating index...")
    validate_index(mongo_client, database_name, collection_name, index_name)
    print("Index validation completed")

def valid_range(n):
    """
    Validates if the input integer n is within the range 1-32.

    Args:
        n (int): Input number to validate.

    Returns:
        int: The validated integer.

    Raises:
        argparse.ArgumentTypeError: If n is outside the range 1-32.
    """
    n = int(n)
    if n < 1 or n > 32:
        raise argparse.ArgumentTypeError("njobs must be an Integer between 1 and 32.")
    return n

if __name__ == "__main__": 
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--cosmos-config", type=str, help="Path to config file containing settings for data preparation")
    parser.add_argument("--form-rec-resource", type=str, help="Name of your Form Recognizer resource to use for PDF cracking.")
    parser.add_argument("--form-rec-key", type=str, help="Key for your Form Recognizer resource to use for PDF cracking.")
    parser.add_argument("--form-rec-use-layout", default=False, action='store_true', help="Whether to use Layout model for PDF cracking, if False will use Read model.")
    parser.add_argument("--njobs", type=valid_range, default=4, help="Number of jobs to run (between 1 and 32). Default=4")
    parser.add_argument("--embedding-model-endpoint", type=str, help="Endpoint for the embedding model to use for vector search. Format: 'https://<AOAI resource name>.openai.azure.com/openai/deployments/<Ada deployment name>/embeddings?api-version=2023-03-15-preview'")
    parser.add_argument("--embedding-model-key", type=str, help="Key for the embedding model to use for vector search.")
    args = parser.parse_args()

    # Load Cosmos configuration from file
    with open(args.cosmos_config) as f:
        config = json.load(f)

    # Set up Azure credential and Form Recognizer client
    credential = AzureCliCredential()
    form_recognizer_client = None

    print("Data preparation script started")
    if args.form_rec_resource and args.form_rec_key:
        os.environ["FORM_RECOGNIZER_ENDPOINT"] = f"https://{args.form_rec_resource}.cognitiveservices.azure.com/"
        os.environ["FORM_RECOGNIZER_KEY"] = args.form_rec_key
        if args.njobs==1:
            form_recognizer_client = DocumentAnalysisClient(endpoint=f"https://{args.form_rec_resource}.cognitiveservices.azure.com/", credential=AzureKeyCredential(args.form_rec_key))
        print(f"Using Form Recognizer resource {args.form_rec_resource} for PDF cracking, with the {'Layout' if args.form_rec_use_layout else 'Read'} model.")

    # Process each index configuration in the config file
    for index_config in config:        
        if index_config.get("index_name") and not args.embedding_model_endpoint:
            raise Exception("ERROR: Vector search is enabled in the config, but no embedding model endpoint and key were provided. Please provide these values or disable vector search.")
        print("Preparing data for index:", index_config["index_name"])
        os.environ["EMBEDDING_MODEL_KEY"] = args.embedding_model_key
        create_index(index_config, credential, form_recognizer_client, embedding_model_endpoint=args.embedding_model_endpoint, use_layout=args.form_rec_use_layout, njobs=args.njobs)
        print("Data preparation for index", index_config["index_name"], "completed")

    print(f"Data preparation script completed. {len(config)} indexes updated.")
