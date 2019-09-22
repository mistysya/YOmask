from flask import Flask,request,Response, make_response
from flask import jsonify,abort,redirect,render_template
import os
import json
import requests
import utils
import base64
import cv2
import numpy as np
app = Flask(__name__,static_url_path='',root_path=os.getcwd())


def img_base64_decode(img):
    sp = img.split(';base64,')
    imgType = sp[0].split('image/')[1] 
    img = sp[1]
    lenx = len(img)%4
    if lenx == 1:
        img += '==='
    if lenx == 2:
        img += '=='
    if lenx == 3:
        img += '='
    img = base64.decodebytes(img.encode())
    return img,imgType



@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/set_cookie')
def set_cookie():
    #res = Response('add cookies')
    #res.set_cookie('Name','Hyman')  
    response = make_response(redirect('/'))
    response.set_cookie('id', "123")
    return response

@app.route('/detect_image',methods=['POST'])
def detect_image():
    img = request.values['img']
    img,imgType = img_base64_decode(img)

    '''
    print(imgType)
    with open("img."+imgType, "wb") as fh:
        fh.write(img)
    '''    
    image = np.asarray(bytearray(img))
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    #print(image.shape)
    result = utils.detect(image)
    #print(result['class_names'])
    #print(result['scores'])
    rois = result['rois']
    dic = {}
    dic['index']=rois.tolist()
    r = {'rois': dic['index'],'class_names':result['class_names']}
    return jsonify(r) 

@app.route('/complete_image',methods=['POST'])
def complete_image():
    count = request.values['count']
    img = request.values['img']
    img,imgType = img_base64_decode(img)
    image = np.asarray(bytearray(img))
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    print('count: ' + count)
    width = image.shape[0]
    height = image.shape[1]
    print('width:' + str(width) + '  height:' + str(height))
    mask = np.zeros(shape=image.shape, dtype=np.uint8)
    for i in range (0,int(count)):
        removeArr = request.form.getlist('remove['+ str(i) +'][]') 
        
        if removeArr[2] =='0' or removeArr[3]  == '0':
            continue
        
        top =  int(removeArr[0])
        left =  int(removeArr[1])
        height = int(removeArr[2])
        width =  int(removeArr[3])
        y1, x1 = top , left
        y2, x2 = top + height , left + width
        print(x1,y1,x2,y2) 
        cv2.rectangle(mask, (x1, y1), (x2, y2), (255, 255, 255), -1)
    

    image_inpainting = utils.complete(image, mask)
    image_inpainting = cv2.cvtColor(image_inpainting , cv2.COLOR_BGR2RGB)
    retval, buffer = cv2.imencode('.'+imgType, image_inpainting)
    img_str = base64.b64encode(buffer)
    img_str = img_str.decode()
    img_str = 'data:image/'+imgType+';base64,' + img_str
    #print(img_str)

    ''' 
    print('imgType: ' + imgType)
    with open("img."+imgType, "wb") as fh:
        fh.write(img)
    '''    
    r = {'img':img_str}
    return jsonify(r) 


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=False, threaded=False)

