# Use this util file to create patches from a single HSI processing level (Level 1C, or Level 2A) and save them to an LMDB file.
import rasterio
import os
import time
import lmdb
import numpy as np
from skimage import io
from tqdm import tqdm
import pandas as pd
import traceback

def create_patches_batches(directory, patch_size, stride, lmdb_save_dir, lmdb_file_name, threshold=(0, -32768), 
                           skip_majority_black=True, majority_black_threshold=(0.05, 0.1), 
                           batch_size=10, map_size=1_099_511_627_776, extract_percentile=None, normalize=False):
    keys = []
    overlap = int((1 - (stride[0] / patch_size[0])) * 100)
    env = lmdb.open(os.path.join(lmdb_save_dir, lmdb_file_name), map_size=map_size, readonly=False, map_async=True, writemap=True)
    raised_error = False

    def _extract_percentile_range(data, lo, hi):
        plo = np.percentile(data, lo)
        phi = np.percentile(data, hi)
        data[data[:,:,:] < plo] = plo
        data[data[:,:,:] >= phi] = phi
        data = (data - plo) / (phi - plo) 
        return data

    def _normalize_image(image, low_percentile=2, high_percentile=98):
        dtype = image.dtype
        low, high = np.percentile(image, (low_percentile, high_percentile))
        image = np.clip(image, low, high)
        image = (image - low) / (high - low) * 255
        return image.astype(dtype)
    
    try:
        with env.begin(write=True) as txn:
            for file_name in tqdm(os.listdir(directory)):
                with rasterio.open(os.path.join(directory, file_name)) as src:
                    image = src.read()
                    channels, height, width = src.count, src.height, src.width
                patch_batch = []
                if image.dtype == 'uint16':
                    thold = threshold[0]
                    mbt = majority_black_threshold[0]
                else:
                    thold = threshold[1]
                    mbt = majority_black_threshold[1]
                    
                for y in range(0, height - patch_size[0], stride[0]):
                    for x in range(0, width - patch_size[1], stride[1]):
                        patch = image[:, y:y + patch_size[0], x:x + patch_size[1]]
                        if skip_majority_black:
                            patch_less_threshold = patch <= thold
                            black_pixel_count = np.count_nonzero(patch_less_threshold)
                            total_pixel_count = patch.shape[0] * patch.shape[1] * patch.shape[2]
                            black_pixel_ratio = black_pixel_count / total_pixel_count
                            if black_pixel_ratio >= mbt:
                                continue
                        
                        if extract_percentile:
                            patch = _extract_percentile_range(patch, extract_percentile[0], extract_percentile[1])

                        if normalize:
                            patch = _normalize_image(patch)

                        patch = np.ascontiguousarray(patch, dtype=np.float32)
                        key = f"{file_name.split('.')[0]}_{patch.dtype}_CHW_{x}_{y}_{overlap}_{channels}_{stride[0]}_{patch_size[0]}_{patch_size[1]}"
                        keys.append(key)
                        patch_batch.append((key, patch))
                        if len(patch_batch) == batch_size:
                            for i in range(batch_size):
                                txn.put(patch_batch[i][0].encode(), patch_batch[i][1].tobytes())
                            patch_batch = []
                        
                if len(patch_batch) > 0:
                    for i in range(len(patch_batch)):
                        txn.put(patch_batch[i][0].encode(), patch_batch[i][1])
        env.close()
    except Exception as e:
        print("An error occurred while saving patches to LMDB. Keys of successfully saved patches will be returned.")
        traceback.print_exc()
        return keys
    return keys

def save_keys_to_csv(save_path, keys, columns, csv_file_name):
    keys_df = pd.DataFrame(keys, columns=columns)
    keys_df.to_csv(os.path.join(save_path, csv_file_name), index=False)

def check_keys_in_lmdb(keys, lmdb_save_dir, lmdb_file_name):
    keys_in_lmdb = []
    env = lmdb.open(os.path.join(lmdb_save_dir, lmdb_file_name), map_size=1_099_511_627_776, readonly=True)
    with env.begin() as txn:
        cursor = txn.cursor()
        for key in cursor.iternkeys():
            key_str = key.decode('utf-8')
            if key_str in keys:
                keys_in_lmdb.append(key_str)
    env.close()
    return keys_in_lmdb


if __name__ == '__main__':
    
    start = time.time()
    
    # Placeholders for paths
    image_directory = r'<your/image/directory>'
    lmdb_save_dir = r'<your/lmdb/save/directory>'
    lmdb_file_name = 'your_lmdb_file_name.lmdb' 
    columns = ['enmap_patches_keys']
    csv_file_name = 'your_csv_file_name.csv'
    
    patch_size = (160, 160)
    stride = (160, 160) 
    threshold = (0, -32768)
    majority_black_threshold = (0.01, 0.1)
    batch_size = 24
    map_size = 1_155_627_776
    extract_percentile = None
    normalize = False
        
    print(f'{csv_file_name.split(".")[0]} Job started successfully...')
    
    keys = create_patches_batches(directory=image_directory, patch_size=patch_size, 
                                  stride=stride, lmdb_save_dir=lmdb_save_dir, 
                                  lmdb_file_name=lmdb_file_name, threshold=threshold,
                                  skip_majority_black=True, majority_black_threshold=majority_black_threshold, 
                                  batch_size=batch_size, map_size=map_size, extract_percentile=extract_percentile, normalize=normalize)
        
    print(f'Saving {len(keys)} key(s) to csv file...')
    save_keys_to_csv(lmdb_save_dir, keys, columns, csv_file_name)
    
    end = time.time()
    print(f'Elapsed time: {end - start}')
    print(f'{csv_file_name.split(".")[0]} Job completed successfully...')
