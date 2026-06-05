import os

image_path = "opg_dataset/images"
label_path = "opg_dataset/labels"

removed = 0

for split in ["train", "val"]:
    img_dir = os.path.join(image_path, split)
    lbl_dir = os.path.join(label_path, split)

    for file in os.listdir(lbl_dir):
        if file.endswith(".txt"):
            lbl_file = os.path.join(lbl_dir, file)

            # check if label file is empty
            if os.path.getsize(lbl_file) == 0:
                # remove label
                os.remove(lbl_file)

                # remove corresponding image
                img_file = os.path.join(img_dir, file.replace(".txt", ".jpg"))
                if os.path.exists(img_file):
                    os.remove(img_file)

                removed += 1

print(f"Removed {removed} empty images + labels")