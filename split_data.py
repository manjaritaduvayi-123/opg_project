import os
import shutil
import random

image_dir = "all_images"
label_dir = "all_labels"

train_img = "opg_dataset/images/train"
val_img = "opg_dataset/images/val"
train_lbl = "opg_dataset/labels/train"
val_lbl = "opg_dataset/labels/val"

# Create folders
os.makedirs(train_img, exist_ok=True)
os.makedirs(val_img, exist_ok=True)
os.makedirs(train_lbl, exist_ok=True)
os.makedirs(val_lbl, exist_ok=True)

# Get files
images = os.listdir(image_dir)
labels = os.listdir(label_dir)

random.shuffle(images)

valid_pairs = []

# 🔍 Match images with labels (flexible matching)
for img in images:
    img_name = img.split('.')[0]

    for lbl in labels:
        lbl_name = lbl.replace(".txt", "")

        # Match if part of name is same
        if img_name in lbl_name or lbl_name in img_name:
            valid_pairs.append((img, lbl))
            break

print(f"✅ Found {len(valid_pairs)} valid pairs")

# Split
split = int(0.8 * len(valid_pairs))
train_pairs = valid_pairs[:split]
val_pairs = valid_pairs[split:]

# Copy function
def copy_data(pairs, img_dest, lbl_dest):
    for img, lbl in pairs:
        shutil.copy(os.path.join(image_dir, img), img_dest)
        shutil.copy(os.path.join(label_dir, lbl), lbl_dest)

# Copy
copy_data(train_pairs, train_img, train_lbl)
copy_data(val_pairs, val_img, val_lbl)

print("✅ Done splitting properly")