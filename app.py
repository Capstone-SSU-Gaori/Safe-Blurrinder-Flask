from flask_restful import reqparse
from flask import Flask, jsonify, request, render_template
# from sqlalchemy import create_engine, text
from mod_dbconn import mod_dbconn

import pymysql
import numpy as np
import pickle as p
import json
import os

app = Flask(__name__)

# app.py 실행하고 일단 localhost:5000/createTable 로 접속해서 table 부터 생성해주세요!
@app.route('/createTable')
def createTable():
    # 완성된 영상을 저장할 database table 생성
    sql = "CREATE TABLE processed_video( \
             _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
             processed_video_name VARCHAR(256) NOT NULL, \
             saved_video_name VARCHAR(256) NOT NULL, \
             video_path VARCHAR(256) NOT NULL \
             )"

    db_class = mod_dbconn.Database()
    db_class.executeOne(sql)
    db_class.commit()
    return "Success!"

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
        row = db_class.executeOne(sql,videoId)
        db_class.commit()
        print(row)
        print(row['video_path']) # 로컬에서 비디오가 어디에 저장되어 있는지

        # fileUpload()  함수로 빼고 싶긴 함

        directory = "C:/Users/Windows10/GaoriProcessedVideos"
        if not os.path.exists(): # 폴더가 없는 경우 생성하기
            os.makedirs(directory)
        else: # 폴더가 있는 경우 폴더에 동영상 업로드
            processed_video_name = '바꾼 이름'
            saved_video_name = row['saved_video_name']
            video_path = row['video_path']

            # 기존 영상을 가져와서 폴더에 저장한 다음에 db에 그 경로 저장해줘야 함

            sql = "INSERT INTO processed_video(processed_video_name, saved_video_name, video_path) \
                    VALUES(%s, %s, %s)"
            val = (processed_video_name, saved_video_name, video_path)
            row = db_class.executeOne(sql, val)
            db_class.commit()
            print(row)

        return jsonify({'result': 'send completely'})
    else:
        return jsonify({'result': 'send completely'})

# def fileUpload():

# 스프링으로 데이터 보내는 테스트 코드
@app.route("/sendVideoId", methods=['GET'])
def sendVideoId():

    return "test"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

