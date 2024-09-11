# EnHyperSet-1 Utility Repository

This repository provides the tools and utilities required to recreate and utilize the **EnHyperSet-1** dataset, which was curated for deep learning applications in hyperspectral image analysis. The dataset is derived from the **EnMAP (Environmental Mapping and Analysis Program)** mission. This repository allows researchers to download, process, and create the hyperspectral image patches similar to what was done in the original EnHyperSet-1 dataset. 

## About EnHyperSet-1

EnHyperSet-1 is a hyperspectral dataset extracted from scenes captured by the EnMAP mission. It contains high-resolution hyperspectral data and was curated specifically for deep learning applications like hyperspectral image classification, regression, super-resolution, and pansharpening. Each image scene contains 224 spectral bands ranging from 420 nm to 2450 nm, offering rich spectral information for various analysis tasks. 

## Features

- **Download and Process EnMAP Data**: Researchers can use the utilities in this repository to download the original EnMAP scenes and process them into image patches for use in hyperspectral deep learning tasks.
- **Preprocessing Utilities**: Functions to preprocess hyperspectral images, including spectral normalization, patch extraction, and contrastive augmentation.
- **Configurable Parameters**: Easily configurable parameters such as patch size, stride, and channels for flexible patch extraction.

## Requirements

To use the utilities in this repository, ensure you have the following dependencies installed:

- Python 3.9+
- lmdb
- rasterio

You can install all dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Getting EnMAP Data

All EnMAP data used for EnHyperSet-1 are freely available through the EnMAP Data Access Portal at the following link:

[EnMAP Data Access Portal](https://www.enmap.org/data_access/)

You can access and download EnMAP scenes from this portal. After downloading the scenes, this repository provides the necessary scripts and tools to recreate the patches used in the EnHyperSet-1 dataset.

## Usage

  1. Download EnMAP Data: First, visit the EnMAP Data Access Portal and download the required scenes.
  2. Process the Data: Use the provided tools to convert these scenes into hyperspectral image patches as we did for EnHyperSet-1. Example command to run the patch extraction:
     ```bash
     python create_patches.py 
     ```
     This command will by default extract patches of size 160x160 with a stride of 160 and output the processed patches in the specified directory. You can change the parameters as you wish.

  3. Train Models: Once the patches are created, they can be used for training self-supervised models, classification, regression, or other deep learning tasks.

## Contributions

We welcome contributions to improve this repository! If you have any enhancements, bug fixes, or new features to propose, feel free to submit a pull request or open an issue.

