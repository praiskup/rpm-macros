#! /usr/bin/python3

"""
Combine files in data/ into a single file.
"""

from collections import defaultdict
import os
import yaml


def merge_yaml_files(data_dir="./data"):
    """
    Reads all YAML files in a directory, merges their contents,
    and organizes the data with file basenames.

    Assumes all files and the directory already exist.
    """
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"The directory '{data_dir}' does not exist.")

    merged_data = defaultdict(list)

    # Get all .yaml files in the specified directory
    file_list = [f for f in os.listdir(data_dir) if f.endswith('.yaml')]

    if not file_list:
        print(f"No .yaml files found in '{data_dir}'.")
        return {}

    # Read each YAML file and store its content with the basename
    file_data = {}
    for filename in file_list:
        basename = os.path.splitext(filename)[0]
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding="utf8") as f:
            file_data[basename] = yaml.safe_load(f)

    # Process each key from each file
    all_keys = set()
    for data in file_data.values():
        if isinstance(data, dict):
            all_keys.update(data.keys())

    for key in all_keys:
        # Group values by their content
        values_by_content = defaultdict(list)
        for basename, data in file_data.items():
            if isinstance(data, dict) and key in data:
                value = data[key]
                values_by_content[yaml.dump(value)].append(basename)

        # Build the final merged structure
        for value_dump, basenames in values_by_content.items():
            merged_data[key].append({
                'distro': sorted(basenames),
                'value': yaml.safe_load(value_dump)
            })

    return dict(merged_data)

# Example of how to use the function
if __name__ == "__main__":
    try:
        merged_result = merge_yaml_files()

        # Check if the result is empty
        if merged_result:
            print("Successfully merged data:")
            # Use sort_keys=False to maintain the order of keys from the first file found
            print(yaml.dump(merged_result, sort_keys=True))
        else:
            print("No data to merge. Check if files exist and are correctly formatted.")

    except FileNotFoundError as e:
        print(e)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
