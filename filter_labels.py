import os

label_path = "opg_dataset/labels"

for root, _, files in os.walk(label_path):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)

            new_lines = []
            with open(file_path) as f:
                for line in f:
                    cls = int(line.split()[0])
                    if cls < 5:  # keep only valid classes
                        new_lines.append(line)

            with open(file_path, "w") as f:
                f.writelines(new_lines)

print("Labels cleaned successfully!")