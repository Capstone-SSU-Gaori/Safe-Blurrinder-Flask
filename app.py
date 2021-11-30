from flask_restful import reqparse
from flask import Flask, jsonify, request, render_template
# from sqlalchemy import create_engine, text
import pymysql
import mod_dbconn

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
@app.route('/getVideoId/', methods=['GET'])
def getVideoId():
    # Spring 에서 전달받은 비디오 아이디 받기
    # videoId = int(request.form['videoId'])
    videoId=1
    db_class = mod_dbconn.Database()
    sql = "SELECT origin_video_name \
                    FROM uploaded_video \
                    WHERE _id=%s"
    row = db_class.executeAll(sql,videoId)

    print(row)
    return jsonify({'result': 'send completely'})


# mysql 연결하는 코드
# class mod_dbconn:
#     class Database:
#         def __init__(self):
#             self.db = pymysql.connect(host='localhost',
#                                       user='root',
#                                       password='thddmswn99',
#                                       db='demo_video',
#                                       charset='utf8')
#             self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
#
#         def execute(self, query, args={}):
#             self.cursor.execute(query, args)
#
#         def executeOne(self, query, args={}):
#             self.cursor.execute(query, args)
#             row = self.cursor.fetchone()
#             return row
#
#         def executeAll(self, query, args={}):
#             self.cursor.execute(query, args)
#             row = self.cursor.fetchall()
#             return row
#
#         def commit(self):
#             self.db.commit()

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

