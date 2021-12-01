from flask_restful import reqparse
from flask import Flask, jsonify, request, render_template
# from sqlalchemy import create_engine, text
from mod_dbconn import mod_dbconn

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
@app.route('/getVideoId', methods=['POST'])
def getVideoId():
    if request.method == 'POST':
        print('JSON확인 : ', request.is_json)
        content = request.get_json()
        videoId = int(content['videoId'])  # Spring 에서 전달받은 비디오 아이디 받기
        db_class = mod_dbconn.Database()
        sql = "SELECT * \
                        FROM uploaded_video \
                        WHERE _id=%s"
        row = db_class.executeAll(sql,videoId)
        print(row)
        print(row[0]['video_path']) # 로컬에서 비디오가 어디에 저장되어 있는지
        return jsonify({'result': 'send completely'})
    else:
        return jsonify({'result': 'send completely'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

