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
#
# @app.route('/db')
# def select():
#     db_class = mod_dbconn.Database()
#
#     sql = "SELECT origin_video_name \
#                 FROM uploaded_video"
#     row = db_class.executeAll(sql)
#
#     print(row)
#
#     # return render_template('db.html', resultData=row[0])


# 스프링에서 데이터 받는 테스트 코드
@app.route('/getVideoId', methods=['POST'])
def getVideoId():
    # Spring 에서 전달받은 비디오 아이디 받기
    if request.method == 'POST':
        print('                  ======작동======')
        print('JSON확인 : ', request.is_json)
        contents = request.get_json()
        print(contents['videoId'])
        if contents:
            print(contents)
        else:
            print("no json")
        print(json.dumps(contents))
        print(contents["videoId"])
        return '완료'

    content = request.json
    print(content['videoId'])
    videoId = int(content['videoId'])
    db_class = mod_dbconn.Database()
    sql = "SELECT origin_video_name \
                    FROM uploaded_video \
                    WHERE _id=%s"
    row = db_class.executeAll(sql,videoId)

    print(row)
    return jsonify({'result': 'send completely'})
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

