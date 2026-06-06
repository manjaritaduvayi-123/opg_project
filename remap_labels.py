import os

label_path = "opg_dataset/labels"

CLASS_MAP = {
    0: 0,   # Caries
    1: 1,   # Crown
    6: 2,   # Missing teeth
    9: 3,   # Root Canal Treatment
    11: 4   # Impacted tooth
}

files_processed = 0
kept_labels = 0
removed_labels = 0

for root, _, files in os.walk(label_path):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            files_processed += 1

            new_lines = []
            with open(file_path) as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    old_cls = int(parts[0])

                    if old_cls in CLASS_MAP:
                        parts[0] = str(CLASS_MAP[old_cls])
                        new_lines.append(" ".join(parts) + "\n")
                        kept_labels += 1
                    else:
                        removed_labels += 1

            with open(file_path, "w") as f:
                f.writelines(new_lines)

print(f"Processed {files_processed} files")
print(f"Kept labels: {kept_labels}")
print(f"Removed labels: {removed_labels}")