# MongoExport JSON Processor 

A Python script to **stream-process large MongoDB JSON exports**, replacing `"af:"` and `"af_"` prefixes with `"true:"` and `"true_"`.

---

## 🚀 Features
✅ **Handles large JSON files** using streaming (low memory usage).  
✅ **Efficient field renaming** (`af:` → `true:`).  
✅ **Fast processing** using `ujson` and `ijson`.  
✅ **Batch writing** to optimize disk I/O.  
✅ **Automated unit tests with real files**.

---

## 📌 Installation
```pip install -r requirements.txt```

## Usage

```python src/json_processor.py tests/data/test_input.ndjson tests/output/test_output.ndjson --policy-parent POLICY_PARENT_ID --policy-ancestors anc1,anc2 --billing-parent BILLING_PARENT_ID --billing-ancestors anc3,anc4 --payments-parent PAYMENTS_PARENT_ID --payments-ancestors anc5,anc6```


## Usage multi-line
```
python src/json_processor.py tests/data/test_input.ndjson tests/output/test_output.ndjson \
    --policy-parent POLICY_PARENT_ID --policy-ancestors anc1,anc2 \
    --billing-parent BILLING_PARENT_ID --billing-ancestors anc3,anc4 \
    --payment-parent PAYMENTS_PARENT_ID --payments-ancestors anc5,anc6
```

## Testing
```python -m unittest discover tests```
