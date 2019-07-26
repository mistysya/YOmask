from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from mainWindow import Ui_MainWindow

import utils

import sys
import cv2
import numpy as np


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        # component signal & slot connect
        self.btnUpload.clicked.connect(self.upload_image)
        self.btnDetect.clicked.connect(self.detect_image)
        self.btnRemove.clicked.connect(self.complete_image)
        self.listResult.itemSelectionChanged.connect(self.select_objects)
        # component style setting
        self.lblImg.setCursor(Qt.CrossCursor)
        # init using variable
        self.origin_img = None
        self.modify_img = None
        self.mask = None
        self.detect_result = []
        self.select_boxes = []

    def update_image(self, image):
        h, w, _ = image.shape
        bytesPerLine = 3 * w
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qImg = QImage(img, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.lblImg.setPixmap(pixmap)

    def generate_mask(self, image):
        self.mask = np.zeros(shape=image.shape, dtype=np.uint8)
        for box in self.select_boxes:
            if not np.any(box):
                # Skip this instance. Has no bbox. Likely lost in image cropping.
                continue
            y1, x1, y2, x2 = box
            cv2.rectangle(self.mask, (x1, y1), (x2, y2), (255, 255, 255), -1)
            cv2.rectangle(self.modify_img, (x1, y1), (x2, y2), (255, 255, 255), -1)
        self.update_image(self.modify_img)

    def upload_image(self):
        # Upload image by using QFileDialog
        # display on lblImg
        try:
            file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                              'C:\\',
                                                              'Image files (*.jpg *.gif *.png)')[0]
            print(file_name)
            img = cv2.imread(file_name)
            self.origin_img = img.copy()
            self.modify_img = img.copy()
            h, w, _ = img.shape
            bytesPerLine = 3 * w
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qImg = QImage(img, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.lblImg.setPixmap(pixmap)
        except Exception as e:
            print("Get Error when read image.")
            print("Error message:", e)
            self.lblImg.setText("Can't read this image!")

    def detect_image(self):
        # Use Mask-RCNN detect image in lblImg
        # show result in listResult
        try:
            result = utils.detect(self.origin_img)
            print(result['class_names'])
            print(result['scores'])
            self.detect_result = result
            self.listResult.addItems(result['class_names'])
        except Exception as e:
            print("Get Error when detect image.")
            print("Error message:", e)

    def complete_image(self):
        # Use Mask-RCNN detect image in lblImg
        # update on lblImg
        try:
            self.generate_mask(self.origin_img)
            # mask = cv2.imread('models\\generative_inpainting\\center_mask_256.png')
            mask = self.mask
            # result = utils.complete(self.origin_img, mask)
            result = utils.complete(self.modify_img, mask)
            h, w, bytes = result.shape
            bytesPerLine = 3 * w
            QImg = QImage(result.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg)
            print("Display")
            self.lblImg.setPixmap(pixmap)
        except Exception as e:
            print("Get Error when complete image.")
            print("Error message:", e)

    def select_objects(self):
        select_items = [item.text() for item in self.listResult.selectedItems()]
        boxes = [self.detect_result['rois'][self.detect_result['class_names'].index(name)] for name in select_items]
        self.select_boxes = boxes
        image = self.modify_img.copy()
        for box in boxes:
            if not np.any(box):
                # Skip this instance. Has no bbox. Likely lost in image cropping.
                continue
            y1, x1, y2, x2 = box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        self.update_image(image)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
