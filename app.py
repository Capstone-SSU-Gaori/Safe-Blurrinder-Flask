from flask_restful import reqparse
from flask import Flask, jsonify, request

import numpy as np
import pickle as p
import json

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

# 스프링으로 데이터 보내는 테스트 코드
@app.route("/tospring")
def spring():
    return "test"

# 스프링에서 데이터 받는 테스트 코드
@app.route('/getVideo/', methods=['POST'])
def getVideoName():
    img = request.files['video']

    return jsonify({'result': 'send completely'})

# @app.route('/predict/', methods=['POST'])
# def predict():
#     parser = reqparse.RequestParser()
#     parser.add_argument('petal_length')
#     parser.add_argument('petal_width')
#     parser.add_argument('sepal_length')
#     parser.add_argument('sepal_width')
#
#     # creates dict
#     args = parser.parse_args()
#     # convert input to array
#     X_new = np.fromiter(args.values(), dtype=float)
#
#     # predict - return ndarray
#     prediction = model.predict([X_new])
#
#     # result
#     out = {'Prediction': get_label(prediction[0])}
#
#     return out, 200
#
# def get_label(label_num):
#     labels = {'0' : 'iris-setosa',
#               '1' : 'iris-versicolor',
#               '2' : 'iris-virginica'}
#
#     return labels.get(str(label_num))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)