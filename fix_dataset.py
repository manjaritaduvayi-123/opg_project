import os

LABEL_PATH = "opg_dataset/labels"
VALID_CLASSES = set(range(5))  # classes 0–4

removed_labels = 0
files_processed = 0

print("🔧 Cleaning labels...\n")

# Step 1: Clean labels
for root, _, files in os.walk(LABEL_PATH):
    for file in files:
        if file.endswith(".txt"):
            files_processed += 1
            file_path = os.path.join(root, file)

            new_lines = []
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    cls = int(parts[0])

                    if cls in VALID_CLASSES:
                        new_lines.append(line)
                    else:
                        removed_labels += 1

            with open(file_path, "w") as f:
                f.writelines(new_lines)

print(f"✅ Cleaned {files_processed} files")
print(f"❌ Removed {removed_labels} invalid labels\n")


# Step 2: Delete cache files
print("🧹 Removing cache files...\n")

cache_files = ["train.cache", "val.cache"]

for cache in cache_files:
    cache_path = os.path.join(LABEL_PATH, cache)
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print(f"🗑 Deleted {cache}")
    else:
        print(f"⚠️ {cache} not found")

print()


# Step 3: Verify dataset
print("🔍 Verifying labels...\n")

invalid_classes = set()

for root, _, files in os.walk(LABEL_PATH):
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(root, file)) as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    cls = int(parts[0])
                    if cls not in VALID_CLASSES:
                        invalid_classes.add(cls)

if not invalid_classes:
    print("🎉 SUCCESS: Dataset is clean!")
else:
    print(f"❌ Still invalid classes found: {invalid_classes}")

print("\n🚀 You can now safely run: python evaluate.py")