import os
import sys
import skimage.io

from collections import Counter  # Counter counts the number of occurrences of each item
from itertools import tee, count

# Root directory of the project
ROOT_DIR = os.path.abspath("") + '/models/mask_rcnn'  # use in GUI
# ROOT_DIR = os.path.abspath("")  # use in test

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
from mrcnn.config import Config
import mrcnn.model as modellib


# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
print(COCO_MODEL_PATH)
# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)


class InferenceConfig(Config):
    """Configuration for training on MS COCO.
    Derives from the base Config class and overrides values specific
    to the COCO dataset.
    """

    # Give the configuration a recognizable name
    NAME = "coco"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1

    # Uncomment to train on 8 GPUs (default is 1)
    # GPU_COUNT = 8

    # Number of classes (including background)
    NUM_CLASSES = 1 + 80  # COCO has 80 classes

    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1


class ObjectDetect(object):
    def __init__(self):
        self.config = InferenceConfig()
        self.config.display()
        self.model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=self.config)
        self.model.load_weights(COCO_MODEL_PATH, by_name=True)
        self.class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                            'bus', 'train', 'truck', 'boat', 'traffic light',
                            'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
                            'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
                            'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                            'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                            'kite', 'baseball bat', 'baseball glove', 'skateboard',
                            'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                            'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                            'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
                            'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
                            'teddy bear', 'hair drier', 'toothbrush']

    def detect(self, image):
        results = self.model.detect([image], verbose=1)
        object_name = [self.class_names[class_id] for class_id in results[0]['class_ids']]
        self.uniquify(object_name)
        results[0]['class_names'] = object_name
        return results[0]

    def uniquify(self, seq, suffs=count(1)):
        """Make all the items unique by adding a suffix (1, 2, etc).

        `seq` is mutable sequence of strings.
        `suffs` is an optional alternative suffix iterable.
        """
        not_unique = [k for k, v in Counter(seq).items() if v > 1]  # so we have: ['name', 'zip']
        # suffix generator dict - e.g., {'name': <my_gen>, 'zip': <my_gen>}
        suff_gens = dict(zip(not_unique, tee(suffs, len(not_unique))))
        for idx, s in enumerate(seq):
            try:
                suffix = '_' + str(next(suff_gens[s]))
            except KeyError:
                # s was unique
                continue
            else:
                seq[idx] += suffix


if __name__ == "__main__":
    detector = ObjectDetect()
    image = skimage.io.imread('4782628554_668bc31826_z.jpg')
    r = detector.detect(image)
    print(r['rois'])
    print(r['class_names'])
    print(r['class_ids'])
    print(r['scores'])
    # print(r['masks'])
