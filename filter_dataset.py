import os
import shutil

# paths
label_dir = "opg_dataset/labels/train"
image_dir = "opg_dataset/images/train"

new_label_dir = "filtered_dataset/labels/train"
new_image_dir = "filtered_dataset/images/train"

os.makedirs(new_label_dir, exist_ok=True)
os.makedirs(new_image_dir, exist_ok=True)

# ✅ best classes
KEEP_CLASSES = [0, 1, 4, 6, 7, 9, 10, 11, 13]

# remap class ids
class_map = {old: new for new, old in enumerate(KEEP_CLASSES)}

for file in os.listdir(label_dir):
    label_path = os.path.join(label_dir, file)
    new_label_path = os.path.join(new_label_dir, file)

    new_lines = []

    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            cls = int(parts[0])

            if cls in KEEP_CLASSES:
                new_cls = class_map[cls]
                new_line = " ".join([str(new_cls)] + parts[1:])
                new_lines.append(new_line)

    # save only if valid objects exist
    if new_lines:
        with open(new_label_path, "w") as f:
            f.write("\n".join(new_lines))

        # copy corresponding image
        img_name = file.replace(".txt", ".jpg")  # change to .png if needed
        src_img = os.path.join(image_dir, img_name)
        dst_img = os.path.join(new_image_dir, img_name)

        if os.path.exists(src_img):
            shutil.copy(src_img, dst_img)