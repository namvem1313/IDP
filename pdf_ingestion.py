import os
import json
import uuid
import base64

def convert_bytes(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # or .hex() if you prefer
    if isinstance(obj, dict):
        return {k: convert_bytes(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_bytes(i) for i in obj]
    return obj

def save_to_json(structured_data, original_filename=None, out_dir="data/papers"):
    os.makedirs(out_dir, exist_ok=True)
    clean_data = convert_bytes(structured_data)

    if original_filename:
        base_name = os.path.splitext(os.path.basename(original_filename))[0]
        file_name = f"{base_name}.json"
    else:
        file_name = f"{uuid.uuid4().hex}.json"

    file_path = os.path.join(out_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    return file_path