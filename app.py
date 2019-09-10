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


@app.route('/complete_image')
def complete_image():
    img = request.args.get('img')
    mask = request.args.get('mask')
    result = utils.complete(img, mask)
    r = {'Result':result}
    return jsonify(r)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=False, threaded=False)

