import os
import yaml
from collections import defaultdict

# --------- LOAD YAML ----------
with open("dataset.yaml", "r") as f:
    data = yaml.safe_load(f)

class_names = data["names"]   # 31 classes

# --------- PATH ----------
labels_path = "opg_dataset/labels/train"   # change if needed

# --------- COUNTERS ----------
object_counts = defaultdict(int)
image_counts = defaultdict(int)
total_images = 0

# --------- PROCESS ----------
for file in os.listdir(labels_path):
    if file.endswith(".txt"):
        total_images += 1
        file_path = os.path.join(labels_path, file)

        classes_in_image = set()

        with open(file_path, "r") as f:
            for line in f:
                class_id = int(line.split()[0])

                # ignore invalid class ids
                if class_id < len(class_names):
                    object_counts[class_id] += 1
                    classes_in_image.add(class_id)

        for cls in classes_in_image:
            image_counts[cls] += 1

# --------- PRINT ----------
print("\n📊 Image Count per Class:")
for i, name in enumerate(class_names):
    print(f"{name}: {image_counts[i]} images")

print("\n🔢 Object Count per Class:")
for i, name in enumerate(class_names):
    print(f"{name}: {object_counts[i]} objects")

print(f"\n📁 Total Images: {total_images}")