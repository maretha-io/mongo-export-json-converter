import json
import argparse
import datetime

VALID_TYPES = {"Policy", "Billing", "Payments"}


def replace_prefix(obj, new_parent_id=None, new_ancestor_ids=None):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            new_key = key.replace("af:", "true:").replace("af_", "true_")

            if new_key == "ecm:parentId" and new_parent_id is not None:
                value = new_parent_id
            elif new_key == "ecm:ancestorIds" and new_ancestor_ids is not None:
                value = new_ancestor_ids

            new_obj[new_key] = replace_prefix(value, new_parent_id, new_ancestor_ids)
        return new_obj

    elif isinstance(obj, list):
        return [replace_prefix(item, new_parent_id, new_ancestor_ids) for item in obj]

    return obj


def process_ndjson(input_path, output_path, replacements, migration_date=None):
    with (open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile):
        for line in infile:
            if not line.strip():
                continue

            obj = json.loads(line)
            primary_type = obj.get("ecm:primaryType")

            if primary_type not in VALID_TYPES:
                continue

            replacement = replacements.get(primary_type, {})
            parent_id = replacement.get("parentId")
            ancestor_ids = replacement.get("ancestorIds")

            transformed = replace_prefix(obj, parent_id, ancestor_ids)

            # --- Add Migration facet ---
            mixins = transformed.get("ecm:mixinTypes", [])
            if "Migration" not in mixins:
                mixins.append("Migration")
                transformed["ecm:mixinTypes"] = mixins

            # --- Add migration:migrationDate field ---
            transformed["migration:migrationDate"] = {"$date": migration_date}

            outfile.write(json.dumps(transformed, ensure_ascii=False) + "\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process and transform NDJSON files with key prefix replacements and optional ID updates.")

    parser.add_argument("input_file", help="Path to input NDJSON file")
    parser.add_argument("output_file", help="Path to output NDJSON file")

    parser.add_argument("--policy-parent", help="Replacement for Policy ecm:parentId")
    parser.add_argument("--policy-ancestors", help="Comma-separated list for Policy ecm:ancestorIds")

    parser.add_argument("--billing-parent", help="Replacement for Billing ecm:parentId")
    parser.add_argument("--billing-ancestors", help="Comma-separated list for Billing ecm:ancestorIds")

    parser.add_argument("--payments-parent", help="Replacement for Payments ecm:parentId")
    parser.add_argument("--payments-ancestors", help="Comma-separated list for Payments ecm:ancestorIds")

    return parser.parse_args()


def build_replacements(args):
    def split_or_none(value):
        return value.split(",") if value else None

    return {
        "Policy": {
            "parentId": args.policy_parent,
            "ancestorIds": split_or_none(args.policy_ancestors),
        },
        "Billing": {
            "parentId": args.billing_parent,
            "ancestorIds": split_or_none(args.billing_ancestors),
        },
        "Payments": {
            "parentId": args.payments_parent,
            "ancestorIds": split_or_none(args.payments_ancestors),
        },
    }


if __name__ == "__main__":
    args = parse_args()
    replacements = build_replacements(args)

    print(f"📂 Input file: {args.input_file}")
    print(f"📁 Output file: {args.output_file}")

    for primary_type in VALID_TYPES:
        info = replacements[primary_type]
        print(f"🔁 {primary_type} → parentId: {info['parentId']}, ancestorIds: {info['ancestorIds']}")
        
    migration_date = (
        datetime.datetime
        .utcnow()                                           # naive UTC
        .replace(tzinfo=datetime.timezone.utc)              # make it UTC-aware
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    print(f"🕒 Migration Date -> {migration_date}")

    process_ndjson(args.input_file, args.output_file, replacements, migration_date)
