import json
import os
from datetime import datetime


# Function to save quiz results to a file
def save_results_to_file(results: list[dict], folder: str = "./quiz_results/"):
    # Create directory if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quiz_results_{timestamp}.json"
    file_path = os.path.join(folder, filename)

    # Write results to the file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


# Function to load historical results from the quiz_results folder
def load_historical_results(folder: str = "./quiz_results/") -> list[dict]:
    historical_results = []
    if os.path.exists(folder):
        # List all json files in the folder
        result_files = [f for f in os.listdir(folder) if f.endswith(".json")]
        for file_name in result_files:
            file_path = os.path.join(folder, file_name)
            # Load the results from each file and append to the historical results list
            with open(file_path, "r", encoding="utf-8") as f:
                file_results = json.load(f)
                historical_results.extend(file_results)
    return historical_results
