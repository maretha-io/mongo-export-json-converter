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

```python src/json_processor.py tests/data/test_input.json tests/output/test_output.json```


## Testing
```python -m unittest discover tests```
