import json
import argparse

VALID_TYPES = {"Policy", "Billing", "Payments"}


def replace_prefix(obj, new_parent_id=None, new_ancestor_ids=None):
    """
    Recursively replace 'af:' and 'af_' prefixes with 'true:' and 'true_' in dictionary keys.
    Also replaces 'ecm:parentId' and 'ecm:ancestorIds' values if provided.
    """
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            new_key = key.replace("af:", "true:").replace("af_", "true_")

            # Replace specific values
            if new_key == "ecm:parentId" and new_parent_id is not None:
                value = new_parent_id
            elif new_key == "ecm:ancestorIds" and new_ancestor_ids is not None:
                value = new_ancestor_ids

            new_obj[new_key] = replace_prefix(value, new_parent_id, new_ancestor_ids)
        return new_obj

    elif isinstance(obj, list):
        return [replace_prefix(item, new_parent_id, new_ancestor_ids) for item in obj]

    return obj


def process_ndjson(input_path, output_path, replacements):
    """
    Processes an NDJSON file, replacing prefixes and updating IDs based on type.
    """
    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            if not line.strip():
                continue

            obj = json.loads(line)
            primary_type = obj.get("ecm:primaryType")

            if primary_type not in VALID_TYPES:
                continue

            parent_id = replacements[primary_type]["parentId"]
            ancestor_ids = replacements[primary_type]["ancestorIds"]

            transformed = replace_prefix(obj, parent_id, ancestor_ids)
            outfile.write(json.dumps(transformed, ensure_ascii=False) + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Process and transform NDJSON with dynamic replacements.")

    parser.add_argument("input_file", help="Input NDJSON file")
    parser.add_argument("output_file", help="Output NDJSON file")

    parser.add_argument("--policy-parent", required=True)
    parser.add_argument("--policy-ancestors", required=True)
    parser.add_argument("--billing-parent", required=True)
    parser.add_argument("--billing-ancestors", required=True)
    parser.add_argument("--payments-parent", required=True)
    parser.add_argument("--payments-ancestors", required=True)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    replacements = {
        "Policy": {
            "parentId": args.policy_parent,
            "ancestorIds": args.policy_ancestors.split(","),
        },
        "Billing": {
            "parentId": args.billing_parent,
            "ancestorIds": args.billing_ancestors.split(","),
        },
        "Payments": {
            "parentId": args.payments_parent,
            "ancestorIds": args.payments_ancestors.split(","),
        },
    }

    print(f"📂 Input: {args.input_file}")
    print(f"📁 Output: {args.output_file}")
    for k, v in replacements.items():
        print(f"🔁 {k} → parentId: {v['parentId']}, ancestorIds: {v['ancestorIds']}")

    process_ndjson(args.input_file, args.output_file, replacements)