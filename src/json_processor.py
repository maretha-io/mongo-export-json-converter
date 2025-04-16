import sys
import json


def replace_prefix(obj):
    """Recursively replace 'af:' and 'af_' prefixes with 'true:' and 'true_' in dictionary keys."""
    if isinstance(obj, dict):
        return {
            key.replace("af:", "true:").replace("af_", "true_"): replace_prefix(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [replace_prefix(item) for item in obj]
    return obj


def process_ndjson(input_path, output_path):
    """
    Processes an NDJSON file by replacing prefix in each object.
    Writes the transformed data back as NDJSON.
    """
    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            if not line.strip():
                continue  # skip empty lines
            obj = json.loads(line)
            transformed = replace_prefix(obj)
            outfile.write(json.dumps(transformed, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"📂 Processing NDJSON from: {input_file}")
    print(f"📁 Saving output to: {output_file}")

    process_ndjson(input_file, output_file)
