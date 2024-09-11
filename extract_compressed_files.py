import os
import shutil
import tarfile
import zipfile
from tqdm import tqdm

def extract_tar(tar_file, extract_to):
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(extract_to)
    os.remove(tar_file)  # delete the tar file after extracting its contents

def extract_zip(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_file)  # delete the zip file after extracting its contents

def copy_files(src_dir, dest_dir):
    for root, dirs, files in tqdm(os.walk(src_dir), desc="Copying TIF files..."):
        for file in files:
            if file.endswith("SPECTRAL_IMAGE.TIF"):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                if not os.path.isfile(dest_file):
                    shutil.copy(src_file, dest_dir)
    print('Done copying files...')

if __name__ == '__main__':
    # Placeholder paths for external use
    src_dir = r'<your/source/directory>'
    dest_dir = r'<your/destination/directory>'

    print('Walking and extracting tar files...')
    for root, dirs, files in tqdm(os.walk(src_dir), desc="Extracting tar files..."):
        for file in files:
            if file.endswith(".tar.gz"):
                extract_tar(os.path.join(root, file), root)
            elif file.endswith(".ZIP"):
                extract_zip(os.path.join(root, file), root)

    print('Walking and extracting zip files...')
    for root, dirs, files in tqdm(os.walk(src_dir), desc="Extracting zip files..."):
        for file in files:
            if file.endswith(".tar.gz"):
                extract_tar(os.path.join(root, file), root)
            elif file.endswith(".ZIP"):
                extract_zip(os.path.join(root, file), root)

    print('Done extracting files...')
    
    # Copy files
    copy_files(src_dir, dest_dir)
