import os
import pathlib
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from flask import Flask, jsonify, request, render_template
from mod_dbconn import mod_dbconn
import cv2
from faceTracker import start_tracker, get_all_crops, get_all_lists, set_video_settings
from collections import OrderedDict

app = Flask(__name__)
dbClass = mod_dbconn.Database()
global videoPath

# app.py 실행하고 일단 localhost:5000/createTable 로 접속해서 table 부터 생성해주세요!
@app.route('/createTable')
def createTable():
    # 완성된 영상을 저장할 database table 생성
    sql = "CREATE TABLE processed_video2( \
             _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
             processed_video_name VARCHAR(256) NOT NULL, \
             saved_video_name VARCHAR(256) NOT NULL, \
             video_path VARCHAR(256) NOT NULL \
             )"

    dbClass.executeOne(sql)
    dbClass.commit()
    return "Success!"

@app.route('/createImgTable')
def createImgTable():
    # 크롭이미지 저장할 database table 생성
    sql = "CREATE TABLE crop_image( \
            _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
            crop_image_name VARCHAR(256) NOT NULL, \
            crop_image_path VARCHAR(256) NOT NULL \
            )"

    dbClass.executeOne(sql)
    dbClass.commit()
    return "Success!"

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

# 스프링으로 데이터 보내는 테스트 코드
@app.route("/tospring")
def spring():
    return "test"

# 스프링에서 데이터 받는 테스트 코드
@app.route('/getVideoId', methods=['GET', 'POST'])
def getVideoId():
    if request.method == 'POST':
        print('JSON확인 : ', request.is_json)
        content = request.get_json()
        videoId = int(content['videoId'])  # Spring 에서 전달받은 비디오 아이디 받기
        sql = "SELECT * \
                        FROM uploaded_video \
                        WHERE _id=%s"
        row = dbClass.executeOne(sql, videoId)
        dbClass.commit()

        videoPath = row['video_path']
        images = processVideo(str(videoPath))
        # return jsonify({'cropImages': images})
        return images
    else:
        return "Test"  # 완성 영상비디오 번호를 리턴하도록 바꾸기


def processVideo(videoPath):
    # face = faceRecognition() # Class의 선언 없이 해당 클래스의 함수를 사용하려 했기 때문에 발생하는 오류
    print("processVideo 함수 :" + videoPath)
    if os.path.isfile(videoPath):  # 해당 파일이 있는지 확인
        # 영상 객체(파일) 가져오기
        cap = cv2.VideoCapture(videoPath)
    else:
        print("파일이 존재하지 않습니다.")

    start_tracker(cap)
    positions_with_obj_id_frame_id_list = get_all_lists()
    crop_img_with_obj_id_list = get_all_crops()
    images = saveImage(crop_img_with_obj_id_list)
    print(images)
    return images

def saveImage(crop_img_with_obj_id_list):
    path = str(pathlib.Path.home()) + "\GaoriCropImages"  # 새로 저장할 폴더
    if not os.path.exists(path):  # 폴더가 없는 경우 생성하기
        os.makedirs(path)
        return "false"
    else:  # 폴더가 있는 경우 폴더에 이미지 저장
        tempResult = {}
        i = 0
        c = 0
        for i, c in enumerate(crop_img_with_obj_id_list):
            cv2.imwrite(path + "\\" + str(i) + ".png", c[1])  # 이렇게 하면 id.png 로 대표 얼굴 저장됨니다
            # json 형식으로 변환   ex) 객체 번호 : 이미지 저장된 경로
            tempResult["frame" + str(c[0])] = path + "\\" + str(i) + ".png"
    return tempResult

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
