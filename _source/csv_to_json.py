import csv
import json
import os

def convert_csv_to_json(csv_file="villes.csv"):
    source_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(source_dir, csv_file)
    json_path = os.path.join(source_dir, "villes.json")

    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_file} not found in {source_dir}")
        return

    villes_data = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            villes_data.append(row)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(villes_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Success: Converted {len(villes_data)} cities to villes.json")

if __name__ == "__main__":
    convert_csv_to_json()
