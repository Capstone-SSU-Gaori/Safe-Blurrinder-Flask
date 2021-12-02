from flask_restful import reqparse
from flask import Flask, jsonify, request, render_template
from mod_dbconn import mod_dbconn

import pymysql
import json
import os
import pathlib
import shutil


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
        print(row['video_path']) # 로컬에서 비디오가 어디에 저장되어 있는지
        # fileUpload()  함수로 빼고 싶긴 함

        # pathlib.Path.home: 사용자의 홈 디렉토리(~) ex) C:\Users\Windows10
        path = str(pathlib.Path.home())+"\GaoriProcessedVideos" # 새로 저장할 폴더
        if not os.path.exists(path): # 폴더가 없는 경우 생성하기
            os.makedirs(path)
        else: # 폴더가 있는 경우 폴더에 동영상 업로드
            processed_video_name = row['origin_video_name'] # '방구석 수련회 장기자랑 - YouTube - Chrome 2021-11-05 04-18-36.mp4'
            # 구현 완료 후 : 동영상 이름을 지정

            saved_video_name = row['saved_video_name']
            # 'af4d1f8d24169c2a8988625d4f2e3455.mp4' ( 완성영상도 같은 이름으로 저장한다고 가정)

            video_path = row['video_path'] # 'C:\\Users\\Windows10\\GaoriVideos\\af4d1f8d24169c2a8988625d4f2e3455.mp4'
            # 구현 완료 후에는 이게 필요없을 듯

            shutil.copy(video_path, path) # 일단은 기존 영상을 새로운 폴더에 복사하는 형태로 해둠

            new_video_path = "{}\{}".format(path, saved_video_name) # 완성 영상이 저장될 새로운 경로

            sql = "INSERT INTO processed_video(processed_video_name, saved_video_name, video_path) \
                    VALUES(%s, %s, %s)" # 완료된 영상을
            val = (processed_video_name, saved_video_name, new_video_path)
            row = db_class.executeOne(sql, val)
            db_class.commit()
            find_sql = "SELECT * \
                                    FROM processed_video \
                                    WHERE saved_video_name=%s"
            row = db_class.executeOne(find_sql, saved_video_name) # 일단은 저장한 애를 saved_video_name으로 찾아옴
            db_class.commit()

        return jsonify({'videoId':row['_id']}) # 방금 저장한 videoId를 리턴
    else:
        return jsonify({'result': 'send completely'})

# def fileUpload():

# 스프링으로 데이터 보내는 테스트 코드
@app.route("/sendVideoId", methods=['GET'])
def sendVideoId():

    return "test"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

