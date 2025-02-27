import sys

import ijson
import ujson as json  # Use UltraJSON for better performance


def replace_prefix(obj):
    """Iteratively replace 'af:' and 'af_' prefixes with 'true:' and 'true_' in dictionary keys."""
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            new_key = key.replace("af:", "true:").replace("af_", "true_")
            new_obj[new_key] = replace_prefix(value)  # Process nested structures
        return new_obj
    elif isinstance(obj, list):
        return [replace_prefix(item) for item in obj]  # Process lists
    return obj  # Return unchanged if not a dict or list


def process_large_json(input_path, output_path, batch_size=1000):
    """
    Optimized: Stream-processes large JSON files in batch mode, reducing disk I/O.
    Uses UltraJSON (`ujson`) with `escape_forward_slashes=False` to avoid unnecessary escaping.
    Opens files in binary mode (`rb`) to avoid `ijson` deprecation warnings.
    """
    with open(input_path, "rb") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("[\n")  # Start JSON array
        first = True
        buffer = []

        for obj in ijson.items(infile, "item"):  # Binary mode read
            transformed = replace_prefix(obj)
            buffer.append(transformed)

            if len(buffer) >= batch_size:
                if not first:
                    outfile.write(",\n")  # Add comma before new batch
                outfile.write(json.dumps(buffer, ensure_ascii=False, indent=4, escape_forward_slashes=False)[
                              1:-1])  # Prevent escaping `/`
                buffer.clear()
                first = False

        if buffer:  # Write remaining objects
            if not first:
                outfile.write(",\n")
            outfile.write(json.dumps(buffer, ensure_ascii=False, indent=4, escape_forward_slashes=False)[1:-1])

        outfile.write("\n]")  # Close JSON array

    print(f"✅ Processing complete. Output saved to {output_path}")


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"📂 Processing JSON from: {input_file}")
    print(f"📁 Saving output to: {output_file}")

    process_large_json(input_file, output_file)
