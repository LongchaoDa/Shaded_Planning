# Returns Mask containing all shaded areas in an image. Returns in the form of a matrix.
import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor

masks = [];

from IPython.display import display, HTML
display(HTML(
"""
<a target="_blank" href="https://colab.research.google.com/github/facebookresearch/segment-anything/blob/main/notebooks/automatic_mask_generator_example.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
"""
))

# Function that displays the masks
def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)
    

# Getting mask generator
sam_checkpoint = "../Models/sam_vit_h_4b8939.pth"
model_type = "default"

# If on colab, device = "cuda";
device = "cpu"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(sam)
    
# Takes as input a mask and the corresponding original image.
# Segments out the image, and finds its mean pixel value.
# Also plots segmentImage and original image.
def findAverageSegmentColor(mask, image, plot = False):
    if(type(mask) == type({})):
        mask = mask['segmentation'];
    # Convert mask to same dimensions as that of image, i.e., d x d x 3
    mask = mask.reshape(400, 400, 1)
    # _3dMask is 400 x 400 x 3
    _3dMask = np.dstack((mask, np.dstack((mask, mask))))

    # Multiplying _3dMask and image to ge segment of the image
    segmentImage = np.multiply(_3dMask, image);

    # Average pixel RGB value for the entire segment
    numOfNonZeroElements = np.sum(segmentImage != 0)
    pixelMean = np.sum(segmentImage) / numOfNonZeroElements;
    
    segmentImage[380:, :] = 0;
    mask[380:, :] = 0;
    if(plot):
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(5,5))
        axes[0, 0].imshow(segmentImage)
        axes[0, 1].imshow(image)
        axes[1, 0].imshow(mask)
        axes[1, 1].imshow(image)
        show_anns(masks)
    return pixelMean;

# Takes input the array of masks, the original image.
# Plots Means of all segments.
def visualizeMaskForThreshold(masks, image):
    pixelMeanArr = np.array([]);
    for mask in masks:
        pixelMean = findAverageSegmentColor(mask, image, False);
        pixelMeanArr = np.append(pixelMeanArr, pixelMean)
#         print(pixelMean)
    plt.bar(np.arange(len(masks)), pixelMeanArr);
    return pixelMeanArr;

# Takes as input array of mean pixel values for segmentImages, threshold and the original image.
def combineShadedMasks(pixelMeanArr, image, threshold, masks):
    shadeSegmentIndex = np.where((pixelMeanArr <= threshold) == True)
    # Coz shadeSegmentIndex is a tuple, with only one element -> array of indices
    shadeSegmentIndex = shadeSegmentIndex[0];
    totalMask = np.full((image.shape[0], image.shape[0]), False)
    for i in shadeSegmentIndex:
        totalMask[masks[i]['segmentation']] = True;
    findAverageSegmentColor(totalMask, image)
    return totalMask

# Main function which returns the mask array
def calculateTotalMask(imagePath, threshold):
    # Reading the image
    image = cv2.imread(imagePath);
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB);
    
    # Calculating the masks
    masks = mask_generator.generate(image)
    
    # Calculating average pixel value for all masks
    pixelMeanArr = visualizeMaskForThreshold(masks, image);
    
    # Calculating the total shade mask
    totalMask = combineShadedMasks(pixelMeanArr, image, threshold, masks)
    
    return totalMask;
    