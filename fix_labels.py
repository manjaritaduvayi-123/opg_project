import os

label_dir = "all_labels"

for file in os.listdir(label_dir):
    if file.endswith(".txt.txt"):
        old = os.path.join(label_dir, file)
        new = os.path.join(label_dir, file.replace(".txt.txt", ".txt"))
        os.rename(old, new)
        print(f"Renamed: {file}")

print("✅ Fixed label names")