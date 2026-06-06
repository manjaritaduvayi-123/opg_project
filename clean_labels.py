import os
import shutil

label_dir = "all_labels"
backup_dir = "removed_images"

os.makedirs(backup_dir, exist_ok=True)

for file in os.listdir(label_dir):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        shutil.move(os.path.join(label_dir, file), os.path.join(backup_dir, file))
        print(f"Moved: {file}")

print("✅ Labels folder cleaned")