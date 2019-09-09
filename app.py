from flask import Flask,request,Response, make_response
from flask import jsonify,abort,redirect,render_template
import os
import json
import requests
import utils
app = Flask(__name__,static_url_path='',root_path=os.getcwd())


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


@app.route('/detect_image')
def detect_image():
    # Use Mask-RCNN detect image in lblImg
    # show result in listResult
    try:
        img = request.args.get('img')
        result = utils.detect(img)
        print(result['class_names'])
        print(result['scores'])
        r = {'Result':result}
        return jsonify(r)
        
    except Exception as e:
            print("Get Error when detect image.")
            print("Error message:", e)

@app.route('/complete_image')
def complete_image():
    img = request.args.get('img')
    mask = request.args.get('mask')
    result = utils.complete(img, mask)
    r = {'Result':result}
    return jsonify(r)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=False)

