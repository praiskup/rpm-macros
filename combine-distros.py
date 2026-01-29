#! /usr/bin/python3

"""
Combine files in data/ into a single file.
"""

from collections import defaultdict
import os
import json

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

    # Process each macro name from each file
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
                tags = values_by_content[yaml.dump(value)]
                tags.append(basename)
                family, version = basename.rsplit("-", 1)
                if family == "rhel+epel" and int(version) > 7:
                    tags.append("epel-" + version)
                elif family == "centos+epel" and int(version) <= 7:
                    tags.append("epel-" + version)
                elif family == "fedora" and version == "eln":
                    tags.append("rhel-11")

        # Build the final merged structure
        for value_dump, basenames in values_by_content.items():
            merged_data[key].append({
                'tags': sorted(basenames),
                'definition': yaml.safe_load(value_dump)
            })

    return dict(merged_data)


if __name__ == "__main__":
    try:
        merged_result = merge_yaml_files()
        if merged_result:
            print(json.dumps(merged_result, sort_keys=True, indent=2))
        else:
            print("No data to merge. Check if files exist and are correctly formatted.")

    except FileNotFoundError as e:
        print(e)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
