"""Data Preparation Script for an Azure Cognitive Search Index.


"""
import argparse
import dataclasses
import json
import os
import subprocess
import time

import requests
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from tqdm import tqdm

from data_utils import chunk_directory, chunk_blob_container

# Configure environment variables  
load_dotenv() # take environment variables from .env.

# Dictionary mapping language codes to language names
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


def check_if_search_service_exists(search_service_name: str,
    subscription_id: str,
    resource_group: str,
    credential = None):
    """Checks if an Azure Cognitive Search service instance exists.

    Args:
        search_service_name (str): _description_
        subscription_id (str): _description_
        resource_group (str): _description_
        credential: Azure credential to use for getting acs instance
    """
    if credential is None:
        raise ValueError("credential cannot be None")
     # Construct the API URL and headers for checking if the service exists
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Search/searchServices"
        f"/{search_service_name}?api-version=2024-03-01-Preview"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credential.get_token('https://management.azure.com/.default').token}",
    }

    # Send GET request to check service existence
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def create_search_service(
    search_service_name: str,
    subscription_id: str,
    resource_group: str,
    location: str,
    sku: str = "standard",
    credential = None,
):
    """Creates an Azure Cognitive Search service if it does not already exist.

    Args:
        search_service_name (str): _description_
        subscription_id (str): _description_
        resource_group (str): _description_
        location (str): _description_
        credential: Azure credential to use for creating acs instance

    Raises:
        Exception: _description_
    """
    if credential is None:
        raise ValueError("credential cannot be None")
    
    # Prepare the API request URL and payload
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Search/searchServices"
        f"/{search_service_name}?api-version=2024-03-01-Preview"
    )

    payload = {
        "location": f"{location}",
        "sku": {"name": sku},
        "properties": {
            "replicaCount": 1,
            "partitionCount": 1,
            "hostingMode": "default",
            "semanticSearch": "free",
        },
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credential.get_token('https://management.azure.com/.default').token}",
    }

    # Send PUT request to create the search service
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(
            f"Failed to create search service. Error: {response.text}")

def create_or_update_search_index(
        service_name, 
        subscription_id=None, 
        resource_group=None, 
        index_name="default-index", 
        semantic_config_name="default", 
        credential=None, 
        language=None,
        vector_config_name=None,
        admin_key=None):
    """Creates or updates a search index with a specified schema and configuration.
    
    This function configures the index schema based on the specified parameters, including
    support for semantic search and vector-based search if enabled.
    
    Args:
        service_name (str): Name of the Azure Search service.
        subscription_id (str): Azure subscription ID.
        resource_group (str): Resource group name.
        index_name (str): Name of the index to create or update.
        semantic_config_name (str): Semantic search configuration name.
        credential: Azure credential object for authentication.
        language (str): Language code for indexing.
        vector_config_name (str): Name of the vector search configuration.
        admin_key (str): Admin API key for the search service.

    Raises:
        Exception: If index creation or update fails.
    
    Returns:
        bool: True if the index is created or updated successfully, False otherwise.
    """
    # Fetch admin key if it's not provided
    if credential is None and admin_key is None:
        raise ValueError("credential and admin key cannot be None")
    
    if not admin_key:
        admin_key = json.loads(
            subprocess.run(
                f"az search admin-key show --subscription {subscription_id} --resource-group {resource_group} --service-name {service_name}",
                shell=True,
                capture_output=True,
            ).stdout
        )["primaryKey"]

    # API endpoint for creating or updating the index
    url = f"https://{service_name}.search.windows.net/indexes/{index_name}?api-version=2024-03-01-Preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": admin_key,
    }

    # Define index schema based on function parameters
    body = {
        "fields": [
            {
                "name": "id",
                "type": "Edm.String",
                "searchable": True,
                "key": True,
            },
            {
                "name": "content",
                "type": "Edm.String",
                "searchable": True,
                "sortable": False,
                "facetable": False,
                "filterable": False,
                "analyzer": f"{language}.lucene" if language else None,
            },
            {
                "name": "title",
                "type": "Edm.String",
                "searchable": True,
                "sortable": False,
                "facetable": False,
                "filterable": False,
                "analyzer": f"{language}.lucene" if language else None,
            },
            {
                "name": "filepath",
                "type": "Edm.String",
                "searchable": True,
                "sortable": False,
                "facetable": False,
                "filterable": False,
            },
            {
                "name": "url",
                "type": "Edm.String",
                "searchable": True,
            },
            {
                "name": "metadata",
                "type": "Edm.String",
                "searchable": True,
            },
            {
                "name": "image_mapping",
                "type": "Edm.String",
                "searchable": False,
                "sortable": False,
                "facetable": False,
                "filterable": False
            }
        ],
        "suggesters": [],
        "scoringProfiles": [],
        "semantic": {
            "configurations": [
                {
                    "name": semantic_config_name,
                    "prioritizedFields": {
                        "titleField": {"fieldName": "title"},
                        "prioritizedContentFields": [{"fieldName": "content"}],
                        "prioritizedKeywordsFields": [],
                    },
                }
            ]
        },
    }

    # Add vector search configuration if specified
    if vector_config_name:
        body["fields"].append({
            "name": "contentVector",
            "type": "Collection(Edm.Single)",
            "searchable": True,
            "retrievable": True,
            "stored": True,
            "dimensions": int(os.getenv("VECTOR_DIMENSION", 1536)),
            "vectorSearchProfile": vector_config_name
        })

        body["vectorSearch"] = {
        "algorithms": [
            {
                "name": "my-hnsw-config-1",
                "kind": "hnsw",
                "hnswParameters": {
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            }
        ],
        "profiles": [
            {
                "name": vector_config_name,
                "algorithm": "my-hnsw-config-1"
            }
        ]
        }

    # Execute the API request to create or update the index
    response = requests.put(url, json=body, headers=headers)
    if response.status_code == 201:
        print(f"Created search index {index_name}")
    elif response.status_code == 204:
        print(f"Updated existing search index {index_name}")
    else:
        raise Exception(f"Failed to create search index. Error: {response.text}")
    
    return True


def upload_documents_to_index(service_name, subscription_id, resource_group, index_name, docs, credential=None, upload_batch_size = 50, admin_key=None):
    """Uploads a list of documents to the specified Azure Cognitive Search index in batches.

    Args:
        service_name (str): The name of the Azure Search service.
        subscription_id (str): Azure subscription ID.
        resource_group (str): Name of the resource group.
        index_name (str): Name of the target search index.
        docs (list): List of documents to be uploaded.
        credential: Azure credential object for authentication (optional).
        upload_batch_size (int): Number of documents to upload per batch (default is 50).
        admin_key (str): Admin API key for the search service (optional).

    Raises:
        Exception: Raises an error if uploading fails for some documents.
    """
    # Ensure either a credential or admin key is provided
    if credential is None and admin_key is None:
        raise ValueError("credential and admin_key cannot be None")
    
    to_upload_dicts = []

    # Add document IDs and prepare documents for upload
    id = 0
    for d in docs:
        if type(d) is not dict:
            d = dataclasses.asdict(d) # Convert dataclass to dictionary if necessary
        # add id to documents
        d.update({"@search.action": "upload", "id": str(id)})
        if "contentVector" in d and d["contentVector"] is None:
            del d["contentVector"]
        to_upload_dicts.append(d)
        id += 1
    
    # Get the endpoint URL for the search service
    endpoint = "https://{}.search.windows.net/".format(service_name)
    # Fetch admin key if it's not provided
    if not admin_key:
        admin_key = json.loads(
            subprocess.run(
                f"az search admin-key show --subscription {subscription_id} --resource-group {resource_group} --service-name {service_name}",
                shell=True,
                capture_output=True,
            ).stdout
        )["primaryKey"]

    # Initialize SearchClient for interacting with the index
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(admin_key),
    )
    # Upload the documents in batches of upload_batch_size
    for i in tqdm(range(0, len(to_upload_dicts), upload_batch_size), desc="Indexing Chunks..."):
        batch = to_upload_dicts[i: i + upload_batch_size]
        results = search_client.upload_documents(documents=batch)
        num_failures = 0
        errors = set()
        # Check for failed uploads
        for result in results:
            if not result.succeeded:
                print(f"Indexing Failed for {result.key} with ERROR: {result.error_message}")
                num_failures += 1
                errors.add(result.error_message)
        if num_failures > 0:
            raise Exception(f"INDEXING FAILED for {num_failures} documents. Please recreate the index."
                            f"To Debug: PLEASE CHECK chunk_size and upload_batch_size. \n Error Messages: {list(errors)}")

def validate_index(service_name, subscription_id, resource_group, index_name):
    """Validates the status and content of the search index to ensure data integrity.

    Args:
        service_name (str): The name of the Azure Search service.
        subscription_id (str): Azure subscription ID.
        resource_group (str): Name of the resource group.
        index_name (str): Name of the target search index.

    Prints:
        Validation status and statistics of the index.
    """
    api_version = "2024-03-01-Preview"
    # Fetch admin key for authentication
    admin_key = json.loads(
        subprocess.run(
            f"az search admin-key show --subscription {subscription_id} --resource-group {resource_group} --service-name {service_name}",
            shell=True,
            capture_output=True,
        ).stdout
    )["primaryKey"]

    # Define headers and parameters for the API request
    headers = {
        "Content-Type": "application/json", 
        "api-key": admin_key}
    params = {"api-version": api_version}
    url = f"https://{service_name}.search.windows.net/indexes/{index_name}/stats"
    # Retry up to 5 times in case the index is initially empty
    for retry_count in range(5):
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            response = response.json()
            num_chunks = response['documentCount']
            # Check if index is empty and retry if necessary
            if num_chunks==0 and retry_count < 4:
                print("Index is empty. Waiting 60 seconds to check again...")
                time.sleep(60)
            elif num_chunks==0 and retry_count == 4:
                print("Index is empty. Please investigate and re-index.")
            else:
                print(f"The index contains {num_chunks} chunks.")
                average_chunk_size = response['storageSize']/num_chunks
                print(f"The average chunk size of the index is {average_chunk_size} bytes.")
                break
        else:
            if response.status_code==404:
                print(f"The index does not seem to exist. Please make sure the index was created correctly, and that you are using the correct service and index names")
            elif response.status_code==403:
                print(f"Authentication Failure: Make sure you are using the correct key")
            else:
                print(f"Request failed. Please investigate. Status code: {response.status_code}")
            break

def create_index(config, credential, form_recognizer_client=None, embedding_model_endpoint=None, use_layout=False, njobs=4, captioning_model_endpoint=None, captioning_model_key=None):
    """Main function to set up an Azure Cognitive Search index and upload documents.

    Args:
        config (dict): Configuration dictionary containing search service details.
        credential: Azure credential for authentication.
        form_recognizer_client: Client for form recognition (optional).
        embedding_model_endpoint (str): Endpoint for embedding model (optional).
        use_layout (bool): Flag to use layout information for chunking (optional).
        njobs (int): Number of jobs for parallel processing (default is 4).
        captioning_model_endpoint (str): Captioning model endpoint (optional).
        captioning_model_key (str): Captioning model key (optional).
    """
     # Extract settings from config
    service_name = config["search_service_name"]
    subscription_id = config["subscription_id"]
    resource_group = config["resource_group"]
    location = config["location"]
    index_name = config["index_name"]
    language = config.get("language", None)

    # Verify language suppor
    if language and language not in SUPPORTED_LANGUAGE_CODES:
        raise Exception(f"ERROR: Ingestion does not support {language} documents. "
                        f"Please use one of {SUPPORTED_LANGUAGE_CODES}."
                        f"Language is set as two letter code for e.g. 'en' for English."
                        f"If you donot want to set a language just remove this prompt config or set as None")


    # check if search service exists, create if not
    try:
        if check_if_search_service_exists(service_name, subscription_id, resource_group, credential):
            print(f"Using existing search service {service_name}")
        else:
            print(f"Creating search service {service_name}")
            create_search_service(service_name, subscription_id, resource_group, location, credential=credential)
    except Exception as e:
        print(f"Unable to verify if search service exists. Error: {e}")
        print("Proceeding to attempt to create index.")

    # create or update search index with compatible schema
    admin_key = os.environ.get("AZURE_SEARCH_ADMIN_KEY", None)
    if not create_or_update_search_index(service_name, subscription_id, resource_group, index_name, config["semantic_config_name"], credential, language, vector_config_name=config.get("vector_config_name", None), admin_key=admin_key):
        raise Exception(f"Failed to create or update index {index_name}")
    
    # Initialize data configurations for uploading
    data_configs = []
    if "data_path" in config:
        data_configs.append({
            "path": config["data_path"],
            "url_prefix": config.get("url_prefix", None),
        })
    if "data_paths" in config:
        data_configs.extend(config["data_paths"])

     # Process each data source path
    for data_config in data_configs:
        # chunk directory
        print(f"Chunking path {data_config['path']}...")
        add_embeddings = False
        if config.get("vector_config_name") and embedding_model_endpoint:
            add_embeddings = True
        # Check if path is a blob URL or local path and chunk data accordingly
        if "blob.core" in data_config["path"]:
            result = chunk_blob_container(data_config["path"], credential=credential, num_tokens=config["chunk_size"], token_overlap=config.get("token_overlap",0),
                                azure_credential=credential, form_recognizer_client=form_recognizer_client, use_layout=use_layout, njobs=njobs,
                                add_embeddings=add_embeddings, embedding_endpoint=embedding_model_endpoint, url_prefix=data_config["url_prefix"])
        elif os.path.exists(data_config["path"]):
            result = chunk_directory(data_config["path"], num_tokens=config["chunk_size"], token_overlap=config.get("token_overlap",0),
                                    azure_credential=credential, form_recognizer_client=form_recognizer_client, use_layout=use_layout, njobs=njobs,
                                    add_embeddings=add_embeddings, embedding_endpoint=embedding_model_endpoint, url_prefix=data_config["url_prefix"],
                                    captioning_model_endpoint=captioning_model_endpoint, captioning_model_key=captioning_model_key)
        else:
            raise Exception(f"Path {data_config['path']} does not exist and is not a blob URL. Please check the path and try again.")

        if len(result.chunks) == 0:
            raise Exception("No chunks found. Please check the data path and chunk size.")

        print(f"Processed {result.total_files} files")
        print(f"Unsupported formats: {result.num_unsupported_format_files} files")
        print(f"Files with errors: {result.num_files_with_errors} files")
        print(f"Found {len(result.chunks)} chunks")

        # upload documents to index
        print("Uploading documents to index...")
        upload_documents_to_index(service_name, subscription_id, resource_group, index_name, result.chunks, credential)

    # check if index is ready/validate index
    print("Validating index...")
    validate_index(service_name, subscription_id, resource_group, index_name)
    print("Index validation completed")


def valid_range(n):
    n = int(n)
    if n < 1 or n > 32:
        raise argparse.ArgumentTypeError("njobs must be an Integer between 1 and 32.")
    return n

if __name__ == "__main__": 
    # Initialize the argument parser to handle command-line inputs
    parser = argparse.ArgumentParser()
    # Define the arguments that can be passed to the script
    parser.add_argument("--config", type=str, help="Path to config file containing settings for data preparation")
    parser.add_argument("--form-rec-resource", type=str, help="Name of your Form Recognizer resource to use for PDF cracking.")
    parser.add_argument("--form-rec-key", type=str, help="Key for your Form Recognizer resource to use for PDF cracking.")
    parser.add_argument("--form-rec-use-layout", default=True, action='store_true', help="Whether to use Layout model for PDF cracking, if False will use Read model.")
    parser.add_argument("--njobs", type=valid_range, default=4, help="Number of jobs to run (between 1 and 32). Default=4")
    parser.add_argument("--embedding-model-endpoint", type=str, help="Endpoint for the embedding model to use for vector search. Format: 'https://<AOAI resource name>.openai.azure.com/openai/deployments/<Ada deployment name>/embeddings?api-version=2024-03-01-Preview'")
    parser.add_argument("--embedding-model-key", type=str, help="Key for the embedding model to use for vector search.")
    parser.add_argument("--search-admin-key", type=str, help="Admin key for the search service. If not provided, will use Azure CLI to get the key.")
    parser.add_argument("--azure-openai-endpoint", type=str, help="Endpoint for the (Azure) OpenAI API. Format: 'https://<AOAI resource name>.openai.azure.com/openai/deployments/<vision model name>/chat/completions?api-version=2024-04-01-preview'")
    parser.add_argument("--azure-openai-key", type=str, help="Key for the (Azure) OpenAI API.")
    # Parse the arguments provided in the command line
    args = parser.parse_args()
    
    # Load the configuration from the specified JSON file
    with open(args.config) as f:
        config = json.load(f)
    
    # Initialize Azure CLI credential and Form Recognizer client (optional)
    credential = AzureCliCredential()
    form_recognizer_client = None

     # Inform the user that the data preparation script has started
    print("Data preparation script started")
     # If a search admin key is provided via arguments, set it as an environment variable
    if args.search_admin_key:
        os.environ["AZURE_SEARCH_ADMIN_KEY"] = args.search_admin_key

    # If Form Recognizer resource and key are provided, set them as environment variables
    if args.form_rec_resource and args.form_rec_key:
        os.environ["FORM_RECOGNIZER_ENDPOINT"] = f"https://{args.form_rec_resource}.cognitiveservices.azure.com/"
        os.environ["FORM_RECOGNIZER_KEY"] = args.form_rec_key
        # If njobs is set to 1, initialize the Form Recognizer client (only one job at a time)
        if args.njobs==1:
            form_recognizer_client = DocumentIntelligenceClient(endpoint=f"https://{args.form_rec_resource}.cognitiveservices.azure.com/", credential=AzureKeyCredential(args.form_rec_key))
        print(f"Using Form Recognizer resource {args.form_rec_resource} for PDF cracking, with the {'Layout' if args.form_rec_use_layout else 'Read'} model.")

    # Iterate through each index configuration provided in the config file
    for index_config in config:
        # Inform the user that data preparation for the index is starting
        print("Preparing data for index:", index_config["index_name"])
        # Ensure that if vector search is enabled, an embedding model endpoint is provided
        if index_config.get("vector_config_name") and not args.embedding_model_endpoint:
            raise Exception("ERROR: Vector search is enabled in the config, but no embedding model endpoint and key were provided. Please provide these values or disable vector search.")
        # Call the function to create the index using the provided configurations and arguments
        create_index(index_config, credential, form_recognizer_client, embedding_model_endpoint=args.embedding_model_endpoint, use_layout=args.form_rec_use_layout, njobs=args.njobs, captioning_model_endpoint=args.azure_openai_endpoint, captioning_model_key=args.azure_openai_key)
        print("Data preparation for index", index_config["index_name"], "completed")

    print(f"Data preparation script completed. {len(config)} indexes updated.")