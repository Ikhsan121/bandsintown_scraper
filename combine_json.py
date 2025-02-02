import os
import json

if __name__ == "__main__":

    folder_path = "./events"  # Change this to your folder path
    output_file = "events.json"

    # List all JSON files in the folder
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    # Initialize an empty list to store merged data
    merged_data = []

    for json_file in json_files:
        with open(os.path.join(folder_path, json_file), "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):  # Ensure it's a list before merging
                merged_data.extend(data)  # Merge into one single list

    # Save the merged data into a new JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=4)

    print(f"Merged {len(json_files)} JSON files into one list in {output_file}")
    # Load JSON file
    with open("events.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Count the number of items
    count = len(data)

    print(f"Number of items in JSON file: {count}")
