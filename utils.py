from models.mask_rcnn.maskrcnn import ObjectDetect
from models.generative_inpainting.inpainting import ImageComplete


def detect(image):
    detector = ObjectDetect()
    result = detector.detect(image)
    return result


def complete(image, mask):
    '''
    image_complete.prepare(image, mask)
    print("prepare")
    result = image_complete.complete()
    print("complete")
    '''
    image_complete = ImageComplete()
    #import cv2
    #image = cv2.imread('models\\generative_inpainting\\imagenet_patches_ILSVRC2012_val_00045643_input.png')
    #mask = cv2.imread('models\\generative_inpainting\\center_mask_256.png')
    result = image_complete.run(image, mask)
    return result

if __name__ == "__main__":
    result = complete("abd", "123")
