from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
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
        self.btnOriginImg.pressed.connect(self.display_origin)
        self.btnOriginImg.released.connect(self.display_modify)
        # component style setting
        self.frame.setCursor(Qt.ArrowCursor)
        self.img_area = ImageArea()
        self.verticalLayout.addWidget(self.img_area)
        # init using variable
        self.origin_img = None
        self.modify_img = None
        self.mask = None
        self.detect_result = []
        self.select_boxes = []
        self.free_select_mode = False
        # self.lblImg_center_point = (0, 0)

    def update_image(self, image):
        h, w, _ = image.shape
        bytesPerLine = 3 * w
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qImg = QImage(img, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.img_area.update_image(pixmap)
        # self.lblImg.setPixmap(pixmap)

    def display_origin(self):
        self.update_image(self.origin_img)

    def display_modify(self):
        self.update_image(self.modify_img)

    def generate_mask(self, image):
        self.mask = np.zeros(shape=image.shape, dtype=np.uint8)
        image = self.modify_img.copy()
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
            self.img_area.update_image(pixmap)
            # self.lblImg.setPixmap(pixmap)
        except Exception as e:
            print("Get Error when read image.")
            print("Error message:", e)
            # self.lblImg.setText("Can't read this image!")

    def detect_image(self):
        # Use Mask-RCNN detect image in lblImg
        # show result in listResult
        try:
            result = utils.detect(self.modify_img)
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
            cv2.imshow("res", result[:, :, ::-1])
            self.modify_img = result[:, :, ::-1]
            h, w, bytes = result.shape
            bytesPerLine = 3 * w
            QImg = QImage(result.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg)
            print("Display")
            self.img_area.update_image(pixmap)
            # self.lblImg.setPixmap(pixmap)
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

    def free_select_mode_change(self):
        if self.free_select_mode:
            self.frame.setCursor(Qt.ArrowCursor)
            # self.lblImg.setCursor(Qt.ArrowCursor)
            self.free_select_mode = False
        else:
            self.frame.setCursor(Qt.CrossCursor)
            # self.lblImg.setCursor(Qt.CrossCursor)
            self.free_select_mode = True


class ImageArea(QWidget):  # 不可用QMainWindow,因为QLabel继承自QWidget
    def __init__(self):
        super(ImageArea, self).__init__()
        self.resize(500, 500)  # 设定窗口大小(根据自己显示图片的大小，可更改)
        self.setMinimumSize(500, 500)
        #self.setWindowTitle("图片操作")  # 设定窗口名称

        self.imgPixmap = QPixmap('models\\mask_rcnn\\DSC_0026 - 36028966554.jpg')  # 载入图片
        self.scaledImg = self.imgPixmap.scaled(self.size())  # 初始化缩放图
        self.singleOffset = QPoint(0, 0)  # 初始化偏移值

        self.isLeftPressed = bool(False)  # 图片被点住(鼠标左键)标志位
        self.isImgLabelArea = bool(True)  # 鼠标进入label图片显示区域

    def update_image(self, pixmap):
        self.imgPixmap = pixmap
        # self.scaledImg = self.imgPixmap.scaled(self.size())
        self.scaledImg = self.imgPixmap.copy()
        self.singleOffset = QPoint(0, 0)
        self.update()

    '''重载绘图: 动态绘图'''

    def paintEvent(self, event):
        self.imgPainter = QPainter()  # 用于动态绘制图片
        self.imgFramePainter = QPainter()  # 用于动态绘制图片外线框
        self.imgPainter.begin(self)  # 无begin和end,则将一直循环更新
        self.imgPainter.drawPixmap(self.singleOffset, self.scaledImg)  # 从图像文件提取Pixmap并显示在指定位置
        self.imgFramePainter.setPen(QColor(168, 34, 3))  # 不设置则为默认黑色   # 设置绘图颜色/大小/样式
        self.imgFramePainter.drawRect(10, 10, 480, 480)  # 为图片绘外线狂(向外延展1)
        self.imgPainter.end()  # 无begin和end,则将一直循环更新

    # =============================================================================
    # 图片移动: 首先,确定图片被点选(鼠标左键按下)且未左键释放;
    #          其次,确定鼠标移动;
    #          最后,更新偏移值,移动图片.
    # =============================================================================
    '''重载一下鼠标按下事件(单击)'''

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键按下
            print("鼠标左键单击")  # 响应测试语句
            self.isLeftPressed = True  # 左键按下(图片被点住),置Ture
            self.preMousePosition = event.pos()  # 获取鼠标当前位置
        elif event.buttons() == QtCore.Qt.RightButton:  # 右键按下
            print("鼠标右键单击")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.MidButton:  # 中键按下
            print("鼠标中键单击")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.RightButton:  # 左右键同时按下
            print("鼠标左右键同时单击")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.MidButton:  # 左中键同时按下
            print("鼠标左中键同时单击")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.MidButton | QtCore.Qt.RightButton:  # 右中键同时按下
            print("鼠标右中键同时单击")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.MidButton \
                | QtCore.Qt.RightButton:  # 左中右键同时按下
            print("鼠标左中右键同时单击")  # 响应测试语句

    '''重载一下滚轮滚动事件'''

    def wheelEvent(self, event):
        #        if event.delta() > 0:                                                 # 滚轮上滚,PyQt4
        # This function has been deprecated, use pixelDelta() or angleDelta() instead.
        angle = event.angleDelta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
        angleX = angle.x()  # 水平滚过的距离(此处用不上)
        angleY = angle.y()  # 竖直滚过的距离
        if angleY > 0:  # 滚轮上滚
            print("鼠标中键上滚")  # 响应测试语句
            self.scaledImg = self.imgPixmap.scaled(self.scaledImg.width() + 5,
                                                   self.scaledImg.height() + 5)
            newWidth = event.x() - (self.scaledImg.width() * (event.x() - self.singleOffset.x())) \
                       / (self.scaledImg.width() - 5)
            newHeight = event.y() - (self.scaledImg.height() * (event.y() - self.singleOffset.y())) \
                        / (self.scaledImg.height() - 5)
            self.singleOffset = QPoint(newWidth, newHeight)  # 更新偏移量
            self.repaint()  # 重绘
        else:  # 滚轮下滚
            print("鼠标中键下滚")  # 响应测试语句
            self.scaledImg = self.imgPixmap.scaled(self.scaledImg.width() - 5,
                                                   self.scaledImg.height() - 5)
            newWidth = event.x() - (self.scaledImg.width() * (event.x() - self.singleOffset.x())) \
                       / (self.scaledImg.width() + 5)
            newHeight = event.y() - (self.scaledImg.height() * (event.y() - self.singleOffset.y())) \
                        / (self.scaledImg.height() + 5)
            self.singleOffset = QPoint(newWidth, newHeight)  # 更新偏移量
            self.repaint()  # 重绘

    '''重载一下鼠标键公开事件'''

    def mouseReleaseEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键释放
            self.isLeftPressed = False;  # 左键释放(图片被点住),置False
            print("鼠标左键松开")  # 响应测试语句
        elif event.button() == Qt.RightButton:  # 右键释放
            self.singleOffset = QPoint(0, 0)  # 置为初值
            self.scaledImg = self.imgPixmap.scaled(self.size())  # 置为初值
            self.repaint()  # 重绘
            print("鼠标右键松开")  # 响应测试语句

    '''重载一下鼠标移动事件'''

    def mouseMoveEvent(self, event):
        if self.isLeftPressed:  # 左键按下
            print("鼠标左键按下，移动鼠标")  # 响应测试语句
            self.endMousePosition = event.pos() - self.preMousePosition  # 鼠标当前位置-先前位置=单次偏移量
            self.singleOffset = self.singleOffset + self.endMousePosition  # 更新偏移量
            self.preMousePosition = event.pos()  # 更新当前鼠标在窗口上的位置，下次移动用
            self.repaint()  # 重绘



if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
