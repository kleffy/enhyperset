import rasterio
import numpy as np
from skimage import exposure
import matplotlib.pyplot as plt

# Placeholder for file path
file_path = r'<your/tif/file/path>'

# Enhanced normalization with histogram equalization
with rasterio.open(file_path) as src:
    # Read the specified bands
    red = src.read(47)  # Band 47 as Red
    green = src.read(27)  # Band 27 as Green
    blue = src.read(10)  # Band 10 as Blue

    # Apply histogram equalization
    red_eq = exposure.equalize_hist(red)
    green_eq = exposure.equalize_hist(green)
    blue_eq = exposure.equalize_hist(blue)

    # Stack the bands
    enhanced_color = np.dstack((red_eq, green_eq, blue_eq))

# Display the enhanced composite
plt.figure(figsize=(10, 10))
plt.imshow(enhanced_color)
plt.title("Enhanced Color Composite (Bands 47, 27, 10)")

# Placeholder for saving the enhanced color composite
output_path = r'<your/output/file/path/enhanced_color.png>'
plt.imsave(output_path, enhanced_color)
