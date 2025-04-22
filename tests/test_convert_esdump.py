# test_convert_esdump.py

import json

from src.convert_es_to_mongo_ndjson import flatten_and_convert_matching_expected, load_ndjson, build_replacements

# 🔧 SET YOUR FILE PATHS HERE
ESDUMP_PATH = "./data/esdump.ndjson"
EXPECTED_PATH = "./data/expected_es_dump_to_mongo.ndjson"

# Simulate args
class DummyArgs:
    policy_parent = "1faa8665-3abd-4569-8ed3-17ae3b2b8525"
    policy_ancestors = "1faa8665-3abd-4569-8ed3-17ae3b2b8525,54b40dce-0173-4b50-a618-4719406b7cdb,00000000-0000-0000-0000-000000000000"
    billing_parent = None
    billing_ancestors = None
    payments_parent = None
    payments_ancestors = None

REPLACEMENTS = build_replacements(DummyArgs())

def unit_test_es_to_mongo_match(es_input, expected_output):
    converted_docs = [flatten_and_convert_matching_expected(doc, REPLACEMENTS) for doc in es_input]
    mismatches = []

    for converted, expected in zip(converted_docs, expected_output):
        expected_clean = {k: v for k, v in expected.items() if k != "_id"}

        # Only compare fields that exist in expected
        filtered_converted = {k: converted.get(k) for k in expected_clean.keys()}

        # Find mismatched keys
        diff = {
            k: {
                "converted": filtered_converted.get(k),
                "expected": expected_clean.get(k)
            }
            for k in expected_clean
            if filtered_converted.get(k) != expected_clean.get(k)
        }

        if diff:
            mismatches.append({
                "ecm:id": converted.get("ecm:id", "<no-id>"),
                "differences": diff
            })

    return mismatches

# 🧪 RUN TEST
if __name__ == "__main__":
    es_data = load_ndjson(ESDUMP_PATH)
    expected_data = load_ndjson(EXPECTED_PATH)

    mismatches = unit_test_es_to_mongo_match(es_data, expected_data)

    if mismatches:
        print(f"❌ Found {len(mismatches)} mismatched documents.")
        print("First mismatch example:")
        print(json.dumps(mismatches[0], indent=2))
    else:
        print("✅ All converted documents match expected Mongo format.")
