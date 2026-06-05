import os

label_path = "opg_dataset/labels"

invalid = set()

for root, _, files in os.walk(label_path):
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(root, file)) as f:
                for line in f:
                    cls = int(line.split()[0])
                    if cls >= 5:
                        invalid.add(cls)

print("Invalid class IDs:", invalid)