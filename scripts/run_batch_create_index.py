import copy
import json
import os
from pathlib import Path
import subprocess
import tqdm
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables (e.g., API keys)
load_dotenv()  

# Get the key for Azure Form Recognizer from environment variables
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")

# Load the configuration settings from the "config.json" file
with open("./config.json", "r") as f:
    config = json.loads(f.read())

# this is an example, 
# it address how to handle subfolders 
# it also provide option wether to use form recognizer
run_config_by_data_path_3_small_512_512 = {
    "aks": "aks_embed_003_small_512_512_index",
    "azure-docs": {
        "index": "azure_embed_003_small_512_512_index",
        "subfolder": "azure-docs",
    },
    "test_loranorm": {
        "index": "test_loranorm_embed_003_small_512_512_index",
        "form-rec-use-layout": False,
    },
    
}

# change path and embedding models
Path("logs").mkdir(exist_ok=True)
# Iterate over each configuration and process it
for key, cfg in tqdm.tqdm(run_config_by_data_path_3_small_512_512.items()):
    # Construct the folder path where data is stored
    folder = os.path.join("/index_data", key)
    
    # If the config is a string, it's a simple index configuration
    if isinstance(cfg, str):
        index = cfg
        form_rec_use_layout = True  # Default to using Form Recognizer layout
    else:
        # Otherwise, extract index name and Form Recognizer settings from the dictionary
        index = cfg["index"]
        form_rec_use_layout = cfg.get("form-rec-use-layout", True)
        if "subfolder" in cfg:
            folder = os.path.join(folder, cfg["subfolder"])

    # Deep copy the base config and update it with the current data path and index
    config_key = copy.deepcopy(config[0])
    config_key["data_path"] = os.path.abspath(folder)   # Absolute path to the data folder
    config_key["index_name"] = index    # Set the index name

    print(config_key["data_path"])
    # Write the modified config to a new JSON file specific to the current configuration
    with open(f"./config.{key}.json", "w") as f:
        f.write(json.dumps([config_key]))
    
    # Prepare the command to run the data preparation script
    command = [
        "python",
        "data_preparation.py",
        "--config",
        f"config.{key}.json",
        "--embedding-model-endpoint",
        '"EMBEDDING_MODEL_ENDPOINT"',
        "--form-rec-resource",
        "test-tprompt",
        "--form-rec-key",
        FORM_RECOGNIZER_KEY,
    ] + (["--form-rec-use-layout"] if form_rec_use_layout else []) + [
        "--njobs=8",
    ]
    # Convert the command list to a string for subprocess execution
    str_command = " ".join(command)
    # Run the command, redirecting stdout and stderr to log files
    with open(f"logs/stdout.{key}.txt", "w") as f_stdout, open(f"logs/stderr.{key}.txt", "w") as f_stderr:
        subprocess.run(str_command, stdout=f_stdout, stderr=f_stderr)
