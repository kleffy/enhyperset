# Use this util file to create patches from different HSI processing level (Level 1C, or Level 2A) 
# of the same spatial region and save them to an LMDB file.
import os
import lmdb
import rasterio
import numpy as np
import pickle
import glob
from multiprocessing import Pool, cpu_count
from rasterio.windows import Window
from tqdm import tqdm

def extract_percentile_range(data, lo, hi):
    plo = np.percentile(data, lo, axis=(1, 2), keepdims=True).astype(np.float16)
    phi = np.percentile(data, hi, axis=(1, 2), keepdims=True).astype(np.float16)
    with np.errstate(divide='ignore', invalid='ignore'):
        data = np.where(phi - plo == 0, 0, (data - plo) / (phi - plo))
    return data

def process_files(file_pair):
    l1c_file, l2a_file = file_pair
    patches = []
    with rasterio.open(l1c_file) as l1c_src, rasterio.open(l2a_file) as l2a_src:
        width, height = l1c_src.meta['width'], l1c_src.meta['height']
        for top in range(0, height - patch_size + 1, stride):
            for left in range(0, width - patch_size + 1, stride):
                l1c_patch = l1c_src.read(window=Window(left, top, patch_size, patch_size))
                l2a_patch = l2a_src.read(window=Window(left, top, patch_size, patch_size))
                bpc = np.count_nonzero(l1c_patch)
                tpc = l1c_patch.size
                bpr = bpc / tpc
                if bpr > 0.99:
                    l1c_patch = extract_percentile_range(l1c_patch, 1, 99)
                    l2a_patch = extract_percentile_range(l2a_patch, 1, 99)
                    patches.append((l1c_patch[:channels], l2a_patch[:channels]))
    return patches

if __name__ == "__main__":
    # Placeholders for directories and file paths
    root_dir = r"<your/root/directory>"
    patch_size = 160
    stride = 160
    channels = 224
    lmdb_path = os.path.join(root_dir, "your_train_lmdb_file.lmdb")
    map_size = 135_555_627_776

    l1c_folder = os.path.join(root_dir, "L1C")
    l2a_folder = os.path.join(root_dir, "L2A")
    l1c_files = sorted(glob.glob(f"{l1c_folder}/*.TIF"))
    l2a_files = sorted(glob.glob(f"{l2a_folder}/*.TIF"))

    assert len(l1c_files) == len(l2a_files), "Number of L1C and L2A images should be the same."

    file_pairs = list(zip(l1c_files, l2a_files))

    env = lmdb.open(lmdb_path, map_size=map_size)

    with env.begin(write=True) as txn:
        total_patches_saved = 0
        with Pool(cpu_count() - 1) as p:
            with tqdm(total=len(file_pairs)) as pbar:
                for patches in p.imap_unordered(process_files, file_pairs):
                    for l1c_patch, l2a_patch in patches:
                        txn.put(f"anchor_{total_patches_saved}".encode(), pickle.dumps(l1c_patch))
                        txn.put(f"positive_{total_patches_saved}".encode(), pickle.dumps(l2a_patch))
                        total_patches_saved += 1
                    pbar.update()

        txn.put('num_samples'.encode(), str(total_patches_saved).encode())

    print(f"Total patches saved: {total_patches_saved}")
    print("Done.")
