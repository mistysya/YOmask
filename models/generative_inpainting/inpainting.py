import cv2
import threading
import numpy as np
import tensorflow as tf

from models.generative_inpainting.inpaint_model import InpaintCAModel


class ImageComplete(object):
    def __init__(self):
        self.model = InpaintCAModel()
        self.model_path = 'models\\generative_inpainting\\model_logs\\release_imagenet_256'
        self.model_path = 'C:\\Users\\Misty\\Documents\\GitHub\\YOmask\\models\\generative_inpainting\\model_logs\\release_imagenet_256'

    def prepare(self, image, mask):
        assert image.shape == mask.shape
        h, w, _ = image.shape
        grid = 8
        image = image[:h//grid*grid, :w//grid*grid, :]
        mask = mask[:h//grid*grid, :w//grid*grid, :]
        print('Shape of image: {}'.format(image.shape))
        image = np.expand_dims(image, 0)
        mask = np.expand_dims(mask, 0)
        self.input_image = np.concatenate([image, mask], axis=2)

    def complete(self):
        sess_config = tf.ConfigProto()
        sess_config.gpu_options.allow_growth = True
        print("start")
        tf.reset_default_graph()
        with tf.Session(config=sess_config) as sess:
            self.input_image = tf.constant(self.input_image, dtype=tf.float32)
            output = self.model.build_server_graph(self.input_image)
            output = (output + 1.) * 127.5
            output = tf.reverse(output, [-1])
            output = tf.saturate_cast(output, tf.uint8)
            # load pretrained model
            vars_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
            assign_ops = []
            for var in vars_list:
                vname = var.name
                from_name = vname
                var_value = tf.contrib.framework.load_variable(self.model_path, from_name)
                assign_ops.append(tf.assign(var, var_value))
            sess.run(assign_ops)
            print('Model loaded.')
            result = sess.run(output)
            # cv2.imwrite(args.output, result[0][:, :, ::-1])
            cv2.imshow("result", result[0][:, :, ::-1])
            cv2.waitKey()
            return result[0]

    def run(self, image, mask):
        self.prepare(image, mask)
        return self.complete()

'''
class ImageCompleteThred(threading.Thread):
    def __init__(self, image, mask):
        threading.Thread.__init__(self)
        self.image = image
        self.mask = mask
        self.imgComplete = ImageComplete()
    def run(self):
        self.imgComplete.run(self.image, self.mask)
'''

if __name__ == "__main__":
    image = cv2.imread('imagenet_patches_ILSVRC2012_val_00045643_input.png')
    mask = cv2.imread('center_mask_256.png')
    image_complete = ImageComplete()
    image_complete.prepare(image, mask)
    image_complete.complete()
