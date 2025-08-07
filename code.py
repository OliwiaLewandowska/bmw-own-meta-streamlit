import pandas as pd
import os
import shutil
import ast

# Load CSV
csv_path = 'bmw_models.csv'
df = pd.read_csv(csv_path)

# Prepare list of files to copy
files_to_copy = set()

for idx, row in df.iterrows():
    # Handle image_names: take only the first if multiple
    img_names = row['image_names']
    if isinstance(img_names, str) and img_names.strip() and img_names != '[]':
        try:
            img_list = ast.literal_eval(img_names)
            if isinstance(img_list, list) and len(img_list) > 0:
                files_to_copy.add(img_list[0])
        except Exception:
            pass
    # Handle video_names: add all if not 'no_videos_found'
    vid_names = row['video_names']
    if isinstance(vid_names, str) and vid_names.strip() and vid_names != '[]':
        try:
            vid_list = ast.literal_eval(vid_names)
            for v in vid_list:
                if v != 'no_videos_found':
                    files_to_copy.add(v)
        except Exception:
            pass

src_dir = 'data'
dst_dir = 'data_models'
os.makedirs(dst_dir, exist_ok=True)

for fname in files_to_copy:
    src = os.path.join(src_dir, fname)
    dst = os.path.join(dst_dir, fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)
    else:
        print(f"File not found: {src}")
