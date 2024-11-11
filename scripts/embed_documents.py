import argparse
from asyncio import sleep
import json

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Custom function for embedding documents
from data_utils import get_embedding

# Retry count for embedding generation in case of failures
RETRY_COUNT = 5

if __name__ == "__main__":
     # Argument parser to get file paths and config file
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data_path", type=str, required=True)
    parser.add_argument("--output_file_path", type=str, required=True)
    parser.add_argument("--config_file", type=str, required=True)

    args = parser.parse_args()
    
    # Load the configuration file
    with open(args.config_file) as f:
        config = json.load(f)

    # Set up Azure credentials (DefaultAzureCredential handles multiple auth methods)
    credential = DefaultAzureCredential()

    # Ensure config is a list to handle possible multiple configurations
    if type(config) is not list:
        config = [config]
    
    # Process each configuration (can support multiple configurations)
    for index_config in config:
        # Keyvault Secret Client
        keyvault_url = index_config.get("keyvault_url")
        if not keyvault_url:
            print("No keyvault url provided in config file. Secret client will not be set up.")
            secret_client = None
        else:
            secret_client = SecretClient(keyvault_url, credential)

        # Get Embedding key
        embedding_key_secret_name = index_config.get("embedding_key_secret_name")
        if not embedding_key_secret_name:
            raise ValueError("No embedding key secret name provided in config file. Embeddings will not be generated.")
        else:
            embedding_key_secret = secret_client.get_secret(embedding_key_secret_name)
            embedding_key = embedding_key_secret.value

        # Ensure embedding endpoint is specified in the config
        embedding_endpoint = index_config.get("embedding_endpoint")
        if not embedding_endpoint:
            raise ValueError("No embedding endpoint provided in config file. Embeddings will not be generated.")

        # Embed documents
        print("Generating embeddings...")
        with open(args.input_data_path) as input_file, open(args.output_file_path, "w") as output_file:
            for line in input_file:
                document = json.loads(line)
                # Sleep/Retry in case embedding model is rate limited.
                for _ in range(RETRY_COUNT):
                    try:
                        embedding = get_embedding(document["content"], embedding_endpoint,  embedding_key)
                        document["contentVector"] = embedding
                        break
                    except:
                        print("Error generating embedding. Retrying...")
                        sleep(30)
                
                 # Write document with embedding to output file
                output_file.write(json.dumps(document) + "\n")
        
        # Notify user when embedding generation is complete
        print("Embeddings generated and saved to {}.".format(args.output_file_path))

