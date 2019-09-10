from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QRect
from mainWindow import Ui_MainWindow

import utils

import os
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
        self.btnOriginImg.pressed.connect(self.display_origin)
        self.btnOriginImg.released.connect(self.display_modify)
        self.btnSelect.clicked.connect(self.select_mode_change)
        self.btnMove.clicked.connect(self.move_mode_change)
        self.btnCreateMask.clicked.connect(self.create_mask)
        # component style setting
        self.frame.setCursor(Qt.ArrowCursor)
        print(self.verticalLayoutWidget.geometry().width(), self.verticalLayoutWidget.geometry().height())
        self.img_area = ImageArea(self.verticalLayoutWidget.geometry().width(),
                                  self.verticalLayoutWidget.geometry().height())
        self.verticalLayout.addWidget(self.img_area)
        # init using variable
        self.origin_img = None
        self.modify_img = None
        self.mask = None
        self.detect_result = {'object_names': [], 'rois': []}
        self.select_boxes = []
        self.select_mode = False
        self.free_select_counter = 0

    def update_image(self, image):
        h, w, _ = image.shape
        bytesPerLine = 3 * w
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qImg = QImage(img, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.img_area.update_image(pixmap)

    def display_origin(self):
        self.update_image(self.origin_img)

    def display_modify(self):
        self.update_image(self.modify_img)

    def initialize(self):
        self.listResult.clear()
        self.select_mode = False
        self.select_boxes.clear()
        self.detect_result = {'object_names': [], 'rois': []}
        self.free_select_counter = 0

    def generate_mask(self, image):
        self.mask = np.zeros(shape=image.shape, dtype=np.uint8)
        image = self.modify_img
        for box in self.select_boxes:
            if not np.any(box):
                # Skip this instance. Has no bbox. Likely lost in image cropping.
                continue
            y1, x1, y2, x2 = box
            cv2.rectangle(self.mask, (x1, y1), (x2, y2), (255, 255, 255), -1)
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), -1)
        self.update_image(image)

    def upload_image(self):
        # Upload image by using QFileDialog
        try:
            file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                              os.getcwd(),
                                                              'Image files (*.jpg *.gif *.png)')[0]
            print(file_name)
            img = cv2.imread(file_name)
            self.origin_img = img.copy()
            self.modify_img = img.copy()
            # convert the format of image to display by openCV & Qt
            h, w, _ = img.shape
            bytesPerLine = 3 * w
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qImg = QImage(img, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.img_area.update_image(pixmap)
            self.initialize()
        except Exception as e:
            print("Get Error when read image.")
            print("Error message:", e)

    def detect_image(self):
        # Use Mask-RCNN detect image in lblImg
        # show result in listResult
        try:
            result = utils.detect(self.modify_img)
            print(result['class_names'])
            print(result['scores'])
            print(result['rois'])
            rois = [[item[0], item[1], item[2], item[3]] for item in result['rois']]
            self.detect_result = {'object_names': self.detect_result['object_names'] + result['class_names'],
                                  'rois': self.detect_result['rois'] + rois}
            self.listResult.clear()
            self.listResult.addItems(self.detect_result['object_names'])
        except Exception as e:
            print("Get Error when detect image.")
            print("Error message:", e)

    def complete_image(self):
        # Use Mask-RCNN detect image

        self.generate_mask(self.origin_img)
        mask = self.mask

        # because there is little different size after complete image (usually smaller)
        # fill the cropped area with origin image
        result = utils.complete(self.modify_img, mask)
        adjust_mask = np.zeros(self.origin_img.shape, dtype=np.bool)
        adjust_mask[:result.shape[0], :result.shape[1]] = True
        locs = np.where(adjust_mask != 0)
        adjust_result = self.origin_img.copy()
        adjust_result[locs[0], locs[1]] = result[locs[0], locs[1]]
        # convert the format of image to display by openCV & Qt
        cv2.imshow("res", adjust_result[:, :, ::-1])
        self.modify_img = adjust_result[:, :, ::-1]
        h, w, bytes = adjust_result.shape
        bytesPerLine = 3 * w
        QImg = QImage(adjust_result.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        print("Display")
        self.img_area.update_image(pixmap)

    def select_objects(self):
        select_items = [item.text() for item in self.listResult.selectedItems()]
        boxes = [self.detect_result['rois'][self.detect_result['object_names'].index(name)] for name in select_items]
        self.select_boxes = boxes
        image = self.modify_img.copy()
        for box in boxes:
            if not np.any(box):
                # Skip this instance. Has no bbox. Likely lost in image cropping.
                continue
            y1, x1, y2, x2 = box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        self.update_image(image)

    def select_mode_change(self):
        self.select_mode = True
        self.frame.setCursor(Qt.CrossCursor)
        self.img_area.select_mode_change(True)

    def move_mode_change(self):
        self.select_mode = False
        self.frame.setCursor(Qt.ArrowCursor)
        self.img_area.select_mode_change(False)

    def create_mask(self):
        image = self.modify_img.copy()
        # map the info of select area to origin image
        x_0 = self.img_area.select_begin_point.x() - self.img_area.img_offset.x()
        y_0 = self.img_area.select_begin_point.y() - self.img_area.img_offset.y()
        weight = self.img_area.select_offset.x() + self.img_area.select_begin_point.x() - self.img_area.img_offset.x()
        height = self.img_area.select_offset.y() + self.img_area.select_begin_point.y() - self.img_area.img_offset.y()
        cv2.rectangle(image,
                      (x_0, y_0),
                      (weight, height),
                      (0, 255, 0), 2)
        print("Create selectmMask")
        cv2.imshow("mask", image)
        self.free_select_counter += 1
        self.detect_result['object_names'].append('free_select_' + str(self.free_select_counter))
        roi = [y_0, x_0, height, weight]
        self.detect_result['rois'].append(roi)
        self.listResult.addItem('free_select_' + str(self.free_select_counter))  # update display list on right side
        self.update_image(image)


class ImageArea(QWidget):
    def __init__(self, width, height):
        super(ImageArea, self).__init__()
        self.imgPixmap = None
        self.scaledImg = None
        self.img_offset = QPoint(0, 0)  # initialize offset
        self.isLeftPressed = bool(False)
        self.isImgLabelArea = bool(True)  # mouse into the area of image
        self.layout_width = width  # the width of the windows can display image
        self.layout_height = height  # the height of the windows can display image
        self.select_mode = False  # select image by user
        self.select_rect = QRect(0, 0, 0, 0)  # the info of select area
        self.select_begin_point = QPoint(0, 0)

        # for show the info of the image
        self.lblTest = QtWidgets.QLabel(self)
        self.lblTest.setGeometry(10, 550, 300, 20)
        self.lblTest.setText("Offset: (0, 0)")

    def update_image(self, pixmap):
        self.imgPixmap = pixmap
        self.scaledImg = self.imgPixmap.copy()
        self.img_offset = QPoint(0, 0)
        self.update()  # repaint the image

    def paintEvent(self, event):
        self.imgPainter = QPainter()  # display image
        self.imgPainter.begin(self)
        self.lblTest.setText("Offset: ({0}, {1})".format(self.img_offset.x(), self.img_offset.y()))
        if self.scaledImg is not None:
            self.imgPainter.drawPixmap(self.img_offset, self.scaledImg)  # display image with offset
        if self.select_mode:  # display select frame
            self.rectPainter = QPainter()
            self.rectPainter.begin(self)
            self.rectPainter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            self.rectPainter.drawRect(self.select_rect)
            self.rectPainter.end()
        self.imgPainter.end()

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            print("Click left mouse")
            self.isLeftPressed = True
            self.preMousePosition = event.pos()  # get mouse position when click mouse
            if self.select_mode:
                self.select_begin_point = event.pos()

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8  # QPoint()  wheel scroll distance
        angle_x = angle.x()  # horizontal scroll distance
        angle_y = angle.y()  # vertical scroll distance
        if angle_y > 0:  # scroll up
            print("Scroll up")
            self.scaledImg = self.imgPixmap.scaled(self.scaledImg.width() + self.imgPixmap.width() // 20,
                                                   self.scaledImg.height() + self.imgPixmap.height() // 20,
                                                   Qt.KeepAspectRatio,
                                                   transformMode=Qt.SmoothTransformation)  # change the size of image
            # try to keep the mouse point to the same position after the size changed
            new_width = event.x() - (self.scaledImg.width() * (event.x() - self.img_offset.x())) \
                       / (self.scaledImg.width() - self.imgPixmap.width() // 20)
            new_height = event.y() - (self.scaledImg.height() * (event.y() - self.img_offset.y())) \
                        / (self.scaledImg.height() - self.imgPixmap.height() // 20)
            self.img_offset = QPoint(new_width, new_height)  # update offset
            self.update()
        else:  # scroll down
            print("Scroll down")
            self.scaledImg = self.imgPixmap.scaled(self.scaledImg.width() - self.imgPixmap.width() // 20,
                                                   self.scaledImg.height() - self.imgPixmap.height() // 20,
                                                   Qt.KeepAspectRatio,
                                                   transformMode=Qt.SmoothTransformation)  # change the size of image
            # try to keep the mouse point to the same position after the size changed
            new_width = event.x() - (self.scaledImg.width() * (event.x() - self.img_offset.x())) \
                       / (self.scaledImg.width() + self.imgPixmap.width() // 20)
            new_height = event.y() - (self.scaledImg.height() * (event.y() - self.img_offset.y())) \
                        / (self.scaledImg.height() + self.imgPixmap.height() // 20)
            self.img_offset = QPoint(new_width, new_height)  # update offset
            self.update()

    def mouseReleaseEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.isLeftPressed = False
            print("Release left mouse")
        elif event.button() == Qt.RightButton:
            self.img_offset = QPoint(0, 0)  # reset the offset
            self.scaledImg = self.imgPixmap.scaled(self.imgPixmap.width(), self.imgPixmap.height(),
                                                   Qt.KeepAspectRatio,
                                                   transformMode=Qt.SmoothTransformation)  # 置为初值
            self.update()
            print("Release right mouse")

    def mouseMoveEvent(self, event):
        if self.isLeftPressed:
            if self.select_mode:
                self.select_offset = event.pos() - self.select_begin_point  # total offset of mouse when selecting
                self.select_rect = QRect(self.select_begin_point.x(), self.select_begin_point.y(),
                                         abs(self.select_offset.x()), abs(self.select_offset.y()))
            else:
                print("Click left mouse & move")
                width_gap = self.layout_width - self.scaledImg.width()  # the gap between display window & image
                print(width_gap, self.layout_width, self.scaledImg.width())
                height_gap = self.layout_height - self.scaledImg.height()  # the gap between display window & image
                print(height_gap, self.layout_height, self.scaledImg.height())
                once_offset = event.pos() - self.preMousePosition  # the offset of this movement
                self.img_offset = self.img_offset + once_offset  # update offset
                # if width of image smaller than width of layout
                if width_gap > 0:
                    if self.img_offset.x() < 0:
                        self.img_offset.setX(0)
                    elif self.img_offset.x() > width_gap:
                        self.img_offset.setX(width_gap)
                # if width of image bigger than width of layout
                else:
                    if self.img_offset.x() > 0:
                        self.img_offset.setX(0)
                    elif self.img_offset.x() < width_gap:
                        self.img_offset.setX(width_gap)
                # if height of image smaller than height of layout
                if height_gap > 0:
                    if self.img_offset.y() < 0:
                        self.img_offset.setY(0)
                    elif self.img_offset.y() > height_gap:
                        self.img_offset.setY(height_gap)
                # if height of image bigger than height of layout
                else:
                    if self.img_offset.y() > 0:
                        self.img_offset.setY(0)
                    elif self.img_offset.y() < height_gap:
                        self.img_offset.setY(height_gap)
            self.preMousePosition = event.pos()  # update mouse position on the window
            self.update()

    def select_mode_change(self, is_select_mode):
        self.select_mode = is_select_mode


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
