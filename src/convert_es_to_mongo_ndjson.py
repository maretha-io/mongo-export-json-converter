import json
import argparse
from datetime import datetime

VALID_TYPES = {"Policy", "Billing", "Payments"}

# ---------- Date Conversion ----------
def is_iso_date(s):
    try:
        datetime.strptime(s.replace("Z", "+00:00"), "%Y-%m-%dT%H:%M:%S.%f%z")
        return True
    except ValueError:
        return False

def convert_dates(obj):
    if isinstance(obj, str) and is_iso_date(obj):
        return {"$date": obj}
    elif isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    return obj

# ---------- Utilities ----------
def insert_nested(doc, dotted_key, value):
    keys = dotted_key.split(".")
    current = doc
    for part in keys[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    current[keys[-1]] = value

def normalize_field_names(doc):
    field_mapping = {
        "file:content": "content",
        "common:icon": "icon",
        "ecm:mixinType": "ecm:mixinTypes",
        "ecm:acl": "ecm:racl",
        "ecm:changeToken": "ecm:systemChangeToken",
        "uid:major_version": "ecm:majorVersion",
        "uid:minor_version": "ecm:minorVersion",
        "ecm:currentLifeCycleState": "ecm:lifeCycleState"
    }

    for old, new in field_mapping.items():
        if old in doc:
            doc[new] = doc.pop(old)

    # Optional trimming of mixins
    expected_mixin_types = {"Thumbnail"}
    if "ecm:mixinTypes" in doc and isinstance(doc["ecm:mixinTypes"], list):
        doc["ecm:mixinTypes"] = [m for m in doc["ecm:mixinTypes"] if m in expected_mixin_types]

    return doc

def apply_post_processing(doc):
    # 🔁 Split "ecm:changeToken": "4-0" into two integers
    change_token_combined = doc.get("ecm:changeToken")
    print(change_token_combined)
    if isinstance(change_token_combined, str) and "-" in change_token_combined:
        try:
            system_token, change_token = change_token_combined.split("-")
            doc["ecm:systemChangeToken"] = int(system_token)
            doc["ecm:changeToken"] = int(change_token)
        except Exception:
            pass  # Leave as-is if malformed

    if "content" in doc and isinstance(doc["content"], dict):
        if "data" not in doc["content"] and "digest" in doc["content"]:
            doc["content"]["data"] = doc["content"]["digest"]

    if "thumb:thumbnail" in doc and isinstance(doc["thumb:thumbnail"], dict):
        thumb = doc["thumb:thumbnail"]
        if "data" not in thumb and "digest" in thumb:
            thumb["data"] = thumb["digest"]

    if "ecm:systemChangeToken" in doc:
        token = doc["ecm:systemChangeToken"]
        if isinstance(token, str) and "-" in token:
            try:
                doc["ecm:systemChangeToken"] = int(token.split("-")[0])
            except ValueError:
                pass

    blob_keys = []
    for key in ["content", "thumb:thumbnail"]:
        blob = doc.get(key)
        if isinstance(blob, dict) and "digest" in blob:
            blob_keys.append(blob["digest"])
    if blob_keys:
        doc["ecm:blobKeys"] = blob_keys

    return doc

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

def flatten_and_convert_matching_expected(es_doc, replacements=None):
    flat = es_doc.get("_source", {}).copy()
    output = {}

    uuid = flat.pop("ecm:uuid", None)
    if uuid:
        output["ecm:id"] = uuid

    for key, value in flat.items():
        if "." in key:
            parent = key.split(".")[0]
            if parent in flat and isinstance(flat[parent], dict):
                continue
            insert_nested(output, key, value)
        else:
            output[key] = value

    output = normalize_field_names(output)

    # Inject parentId and ancestorIds
    if replacements:
        primary_type = output.get("ecm:primaryType")
        if primary_type in VALID_TYPES:
            rep = replacements.get(primary_type, {})
            output["ecm:parentId"] = rep.get("parentId", output.get("ecm:parentId"))
            output["ecm:ancestorIds"] = rep.get("ancestorIds", output.get("ecm:ancestorIds"))

    output = replace_prefix(output)
    output = apply_post_processing(output)
    return convert_dates(output)

# ---------- File I/O ----------
def load_ndjson(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_ndjson(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for doc in data:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

# ---------- CLI ----------
def parse_args():
    parser = argparse.ArgumentParser(description="Convert Elasticdump NDJSON to Mongo-compatible NDJSON.")

    parser.add_argument("input_file", help="Elasticdump NDJSON file")
    parser.add_argument("output_file", help="Output NDJSON file")

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

# ---------- Main ----------
if __name__ == "__main__":
    args = parse_args()
    replacements = build_replacements(args)

    es_data = load_ndjson(args.input_file)
    converted = [flatten_and_convert_matching_expected(doc, replacements) for doc in es_data]
    save_ndjson(converted, args.output_file)

    print(f"✅ Converted {len(converted)} documents")
    print(f"📄 Output written to: {args.output_file}")
