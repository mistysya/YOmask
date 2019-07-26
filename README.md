## Prepare
* install requirements of https://github.com/matterport/Mask_RCNN
* install requirements of https://github.com/JiahuiYu/generative_inpainting
* install PyQt5 (you can install it by anaconda)
    1. install reference https://blog.csdn.net/g96889/article/details/84400373
    2. install reference https://anaconda.org/anaconda/pyqt
* Download file **mask_rcnn_coco.h5**
* It should download it automatically but remembeer move it to the right folder. Or you can just run **models\mask_rcnn\maskrcnn.py** and then it will download the file in the correct place.
* check file **models\mask_rcnn\mask_rcnn_coco.h5**
* check folder **models\generative_inpainting\model_logs\release_imagenet_256**

## Run
* **python gui.py**

## How to use
* **Upload** button will upload file from your computer & display it on left side
* **Detect** button will use Mask-RCNN to detect object in the left side image &  show result on right side list window
* When you select items in right side list, there will be a green box on the left side image
* **Detect** button will use Generative Image Inpainting to remove the object you select on right side list
* Other buttons can't do anything right now.
* The features on the bottom from left to right are: Move image, Select a rectangle area of the image, Zoom in, Zoon out, Create a mask with the reactangle area you selecting
