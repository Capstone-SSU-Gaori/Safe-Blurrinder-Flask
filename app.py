# import os
# import pathlib
#
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# from flask import Flask, jsonify, request, render_template
# from mod_dbconn import mod_dbconn
# from tqdm import tqdm_notebook as tqdm
# from mtcnn import MTCNN
# import matplotlib.pyplot as pp
# import cv2
# from faceRecognition import faceRecognition
#
# app = Flask(__name__)
# dbClass = mod_dbconn.Database()
# global videoPath
#
# # processedVideoId = 0  # 전역 변수로 선언
#
# # app.py 실행하고 일단 localhost:5000/createTable 로 접속해서 table 부터 생성해주세요!
# @app.route('/createTable')
# def createTable():
#     # 완성된 영상을 저장할 database table 생성
#     sql = "CREATE TABLE processed_video( \
#              _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
#              processed_video_name VARCHAR(256) NOT NULL, \
#              saved_video_name VARCHAR(256) NOT NULL, \
#              video_path VARCHAR(256) NOT NULL \
#              )"
#
#     dbClass.executeOne(sql)
#     dbClass.commit()
#     return "Success!"
#
# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'
#
# # 스프링으로 데이터 보내는 테스트 코드
# @app.route("/tospring")
# def spring():
#     return "test"
#
# # 스프링에서 데이터 받는 테스트 코드
# @app.route('/getVideoId', methods=['GET', 'POST'])
# def getVideoId():
#     if request.method == 'POST':
#         print('JSON확인 : ', request.is_json)
#         content = request.get_json()
#         videoId = int(content['videoId'])  # Spring 에서 전달받은 비디오 아이디 받기
#         sql = "SELECT * \
#                         FROM uploaded_video \
#                         WHERE _id=%s"
#         row = dbClass.executeOne(sql,videoId)
#         dbClass.commit()
#         print(row['video_path']) # 로컬에서 비디오가 어디에 저장되어 있는지
#         # print(row['origin_video_name'])
#         videoPath = row['video_path']
#         images = processVideo(str(videoPath))
#         return jsonify({'cropImages': images})
#         # print(processVideo(row['origin_video_name']))
#         # return processVideo(row['origin_video_name']) # 영상처리함수 호출하기
#
#         # # fileUpload(row)
#         # # pathlib.Path.home: 사용자의 홈 디렉토리(~) ex) C:\Users\Windows10
#         # path = str(pathlib.Path.home()) + "\GaoriProcessedVideos"  # 새로 저장할 폴더
#         # if not os.path.exists(path):  # 폴더가 없는 경우 생성하기
#         #     os.makedirs(path)
#         #     return "false"
#         # else:  # 폴더가 있는 경우 폴더에 동영상 업로드
#         #     processed_video_name = row['origin_video_name']  # '방구석 수련회 장기자랑 - YouTube - Chrome 2021-11-05 04-18-36.mp4'
#         #     # 구현 완료 후 : 동영상 이름을 지정
#         #
#         #     saved_video_name = row['saved_video_name']
#         #     # 'af4d1f8d24169c2a8988625d4f2e3455.mp4' ( 완성영상도 같은 이름으로 저장한다고 가정)
#         #
#         #     video_path = row['video_path']  # 'C:\\Users\\Windows10\\GaoriVideos\\af4d1f8d24169c2a8988625d4f2e3455.mp4'
#         #     # 구현 완료 후에는 이게 필요없을 듯
#         #
#         #     shutil.copy(video_path, path)  # 일단은 기존 영상을 새로운 폴더에 복사하는 형태로 해둠
#         #
#         #     new_video_path = "{}\{}".format(path, saved_video_name)  # 완성 영상이 저장될 새로운 경로
#         #
#         #     sql = "INSERT INTO processed_video(processed_video_name, saved_video_name, video_path) \
#         #                         VALUES(%s, %s, %s)"  # 완료된 영상을
#         #     val = (processed_video_name, saved_video_name, new_video_path)
#         #     row = dbClass.executeOne(sql, val)
#         #     dbClass.commit()
#         #     find_sql = "SELECT * \
#         #                                         FROM processed_video \
#         #                                         WHERE saved_video_name=%s"
#         #     row = dbClass.executeOne(find_sql, saved_video_name)  # 일단은 저장한 애를 saved_video_name으로 찾아옴
#         #     dbClass.commit()
#         #     # return "test"
#         #     global processedVideoId
#         #     processedVideoId = str(row['_id'])
#         #     return processedVideoId  # 방금 저장한 videoId를 리턴
#     else:
#         return "Test"# 완성 영상비디오 번호를 리턴하도록 바꾸기
#
# def processVideo(videoPath):
#     face = faceRecognition() # Class의 선언 없이 해당 클래스의 함수를 사용하려 했기 때문에 발생하는 오류
#
#     # pathlib.Path.home: 사용자의 홈 디렉토리(~) ex) C:\Users\Windows10
#     # path = str(pathlib.Path.home()) + "\GaoriVideos"
#     # filePath = os.path.join(path, videoName) # 비디오 이름으로 디비에서 찾아오기
#     print("processVideo 함수 :" +videoPath)
#
#     if os.path.isfile(videoPath):  # 해당 파일이 있는지 확인
#         # 영상 객체(파일) 가져오기
#         cap = cv2.VideoCapture(videoPath)
#     else:
#         print("파일이 존재하지 않습니다.")
#     detector = MTCNN()
#     width = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fourcc = cv2.VideoWriter_fourcc(*'DIVX')
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     out = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))
#     tem = []
#
#     # tracker 부분
#     trackers = []  # [tracker,id],[tracker,id],[],[],,, 형태 -> tracker를 update하거나 접근: tracker[0]으로 접근
#     all_lists = []  # [x,y,w,h,obj_id,frame_id],[],[],,, 형태로 저장
#     all_crops = []  # [id,img],[id,img] 형태로 저장 (트래커별로 저장)
#     id_=1
#
#     face.setPath(videoPath)
#     ### model 바꿀거면 여기서 바꾸면 됨!!!!!!!!! ###
#     model_name = "Dlib"  # facenet은 FaceNet
#
#     for i in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
#         retval, frame = cap.read()
#         if i == 0:  # 첫 번째 프레임이라면?
#             result = detector.detect_faces(frame)
#             if result != []:  # 감지된 얼굴이 존재한다면
#                 for person in result:
#                     if person['confidence'] < 0.8:
#                         continue
#                     bounding_box = person['box']
#                     bounding_box.append(id_)  # x,y,w,h,obj_id,frame_id
#                     bounding_box.append(i)
#                     all_lists.append(bounding_box)
#                     crop, found_id = face.get_cropimg(id_, i, bounding_box[0], bounding_box[1], bounding_box[2],
#                                                  bounding_box[3], True, model_name)
#                     all_crops.append([found_id, crop])
#                     tem.append(bounding_box)  # tem에 탐지한 모든 얼굴들의 좌표를 저장
#                     cv2.rectangle(frame, (bounding_box[0], bounding_box[1]),
#                                   (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]), (0, 155, 255),
#                                   2)
#                     cv2.putText(frame, "id: " + str(id_), (int(bounding_box[0]), int(bounding_box[1])),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#                     id_ += 1
#
#             for t in range(len(result)):
#                 trackers.append([cv2.TrackerCSRT_create(), tem[t][4]])  # trackers에 [트래커, id]
#                 trackers[t][0].init(frame, (tem[t][0], tem[t][1], tem[t][2], tem[t][3]))
#
#         else:  # 첫 번째 프레임이 아니라면? -> 기존에 존재하던 tracker를 업데이트 (현재 프레임의 정보를 넣어서)
#
#             this_box = []  # 이번 프레임에서 탐지한 객체들의 (x,y,w,h)를 저장
#             result = detector.detect_faces(frame)
#             if result != []:  # 감지된 얼굴이 존재한다면
#                 for person in result:
#                     if person['confidence'] < 0.8:
#                         continue
#                     bounding_box = person['box']
#                     this_box.append(bounding_box)
#
#             # 만약 감지된 얼굴 수가 트래커의 수보다 많으면 트래커 다 초기화 하고 다시 추적
#             if (len(this_box) > len(trackers)):
#                 print("change")
#                 trackers = []
#                 for t in range(len(this_box)):
#                     crop, found_id = face.get_cropimg(id_, i, this_box[t][0], this_box[t][1], this_box[t][2], this_box[t][3],
#                                                  False, model_name)
#                     if found_id == id_:  # 현재 id랑 같다, 즉 이전에 동일한 얼굴이 탐지된 적이 없었다 else라면 found_id는 이전에 탐지한 객체의 id
#                         id_ += 1
#                     trackers.append(
#                         [cv2.TrackerCSRT_create(), found_id])  # trackers 0번에 tracker, 1번에 그 트래커가 탐지하는 객체의 id가 저장됨
#                     trackers[t][0].init(frame, (this_box[t][0], this_box[t][1], this_box[t][2], this_box[t][3]))
#                     all_crops.append([found_id, crop])  # 어떤 경우에든 id랑 crop image둘 다 저장 (인식 실패 가능성)
#                     all_lists.append([this_box[t][0], this_box[t][1], this_box[t][2], this_box[t][3], found_id, i])
#                     cv2.rectangle(frame, (this_box[t][0], this_box[t][1]),
#                                   (this_box[t][0] + this_box[t][2], this_box[t][1] + this_box[t][3]), (0, 255, 0), 2, 1)
#                     cv2.putText(frame, "id: " + str(found_id), (int(this_box[t][0]), int(this_box[t][1])),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#
#             else:
#                 # 트래커가 하나라도 객체를 놓치면(여러 이유로 인해) 그렇다면 트래커 배열 싹다 비운다.그리고 mtcnn으로 출력후 다시 초기설정
#                 judge = True
#                 tempor = []
#                 for track in trackers:
#                     res, box = track[0].update(frame)
#                     if res:
#                         x1 = int(box[0])
#                         y1 = int(box[1])
#                         x2 = int(box[0] + box[2])
#                         y2 = int(box[1] + box[3])
#                         tempor.append([x1, y1, x2, y2, track[1]])
#
#                         # cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2,1)
#                     else:
#                         judge = False
#                         print(False)
#
#                 if (judge == True):  # 트래커가 모든 객체를 탐지했을 때
#                     for t in range(len(tempor)):  # tempor (새롭게 탐지한 객체의 좌표를 추가함) -> 현재 프레임의 update 정보 반영
#                         cv2.rectangle(frame, (tempor[t][0], tempor[t][1]), (tempor[t][2], tempor[t][3]), (0, 255, 0), 2,
#                                       1)
#                         cv2.putText(frame, "id: " + str(tempor[t][4]), (int(tempor[t][0]), int(tempor[t][1])),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#                         all_lists.append(
#                             [tempor[t][0], tempor[t][1], tempor[t][2] - tempor[t][0], tempor[t][3] - tempor[t][1],
#                              tempor[t][4], i])
#                 else:  # 트래커가 객체를 하나라도 놓쳤을 때 -> 새롭게 트래커 시작
#                     trackers = []  # trackers를 초기화
#                     for t in range(len(this_box)):
#                         crop, found_id = face.get_cropimg(id_, i, this_box[t][0], this_box[t][1], this_box[t][2],
#                                                      this_box[t][3], False, model_name)
#                         if found_id == id_:  # 현재 id랑 같다, 즉 이전에 동일한 얼굴이 탐지된 적이 없었다 else라면 found_id는 이전에 탐지한 객체의 id
#                             id_ += 1
#                         trackers.append([cv2.TrackerCSRT_create(), found_id])
#                         trackers[t][0].init(frame, (this_box[t][0], this_box[t][1], this_box[t][2], this_box[t][3]))
#                         all_crops.append([found_id, crop])  # 어떤 경우에든 id랑 crop image둘 다 저장 (인식 실패 가능성)
#                         all_lists.append([this_box[t][0], this_box[t][1], this_box[t][2], this_box[t][3], found_id, i])
#
#                         cv2.rectangle(frame, (this_box[t][0], this_box[t][1]),
#                                       (this_box[t][0] + this_box[t][2], this_box[t][1] + this_box[t][3]), (0, 255, 0),
#                                       2, 1)
#                         cv2.putText(frame, "id: " + str(found_id), (int(this_box[t][0]), int(this_box[t][1])),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#
#         out.write(frame)
#         pp.imshow(frame)
#         pp.show()
#
#     print("all_Crops")
#
#     result=[]
#     for c in all_crops:
#         # print("id: " + str(c[0]))
#         result.append({
#             c[0]: c[1]
#         })
#         # pp.imshow(c[1])
#         # pp.show()
#
#     print(result)
#     return jsonify({'cropImages':result})
# # 스프링으로 데이터 보내는 테스트 코드
# # @app.route("/sendVideoId", methods=['GET'])
# # def sendVideoId():
# #
# #     return "test"
#
#
# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000, debug=True)
#

import os
import pathlib

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import pandas as pd
from flask import Flask, jsonify, request, render_template
from mod_dbconn import mod_dbconn
from tqdm import tqdm_notebook as tqdm
from mtcnn import MTCNN
import matplotlib.pyplot as pp
import cv2
from faceTracker import start_tracker, get_all_crops, get_all_lists, set_video_settings

app = Flask(__name__)
dbClass = mod_dbconn.Database()
global videoPath


# processedVideoId = 0  # 전역 변수로 선언

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
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
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
        print(images)
        return "hi"
        # print(processVideo(row['origin_video_name']))
        # return processVideo(row['origin_video_name']) # 영상처리함수 호출하기

        # # fileUpload(row)
        # # pathlib.Path.home: 사용자의 홈 디렉토리(~) ex) C:\Users\Windows10
        # path = str(pathlib.Path.home()) + "\GaoriProcessedVideos"  # 새로 저장할 폴더
        # if not os.path.exists(path):  # 폴더가 없는 경우 생성하기
        #     os.makedirs(path)
        #     return "false"
        # else:  # 폴더가 있는 경우 폴더에 동영상 업로드
        #     processed_video_name = row['origin_video_name']  # '방구석 수련회 장기자랑 - YouTube - Chrome 2021-11-05 04-18-36.mp4'
        #     # 구현 완료 후 : 동영상 이름을 지정
        #
        #     saved_video_name = row['saved_video_name']
        #     # 'af4d1f8d24169c2a8988625d4f2e3455.mp4' ( 완성영상도 같은 이름으로 저장한다고 가정)
        #
        #     video_path = row['video_path']  # 'C:\\Users\\Windows10\\GaoriVideos\\af4d1f8d24169c2a8988625d4f2e3455.mp4'
        #     # 구현 완료 후에는 이게 필요없을 듯
        #
        #     shutil.copy(video_path, path)  # 일단은 기존 영상을 새로운 폴더에 복사하는 형태로 해둠
        #
        #     new_video_path = "{}\{}".format(path, saved_video_name)  # 완성 영상이 저장될 새로운 경로
        #
        #     sql = "INSERT INTO processed_video(processed_video_name, saved_video_name, video_path) \
        #                         VALUES(%s, %s, %s)"  # 완료된 영상을
        #     val = (processed_video_name, saved_video_name, new_video_path)
        #     row = dbClass.executeOne(sql, val)
        #     dbClass.commit()
        #     find_sql = "SELECT * \
        #                                         FROM processed_video \
        #                                         WHERE saved_video_name=%s"
        #     row = dbClass.executeOne(find_sql, saved_video_name)  # 일단은 저장한 애를 saved_video_name으로 찾아옴
        #     dbClass.commit()
        #     # return "test"
        #     global processedVideoId
        #     processedVideoId = str(row['_id'])
        #     return processedVideoId  # 방금 저장한 videoId를 리턴
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
    print(positions_with_obj_id_frame_id_list)
    crop_img_with_obj_id_list = get_all_crops()
    print(crop_img_with_obj_id_list)

    df = pd.DataFrame(positions_with_obj_id_frame_id_list)
    # df.to_csv("좌표들.csv",header=None,index=None)

    for i, c in enumerate(crop_img_with_obj_id_list):
        cv2.imwrite(str(c[0]) + ".png", c[1])  # 이렇게 하면 id.png 로 대표 얼굴 저장됨니다

    # # fileUpload(row)
    # # pathlib.Path.home: 사용자의 홈 디렉토리(~) ex) C:\Users\Windows10
    # path = str(pathlib.Path.home()) + "\GaoriCropImages"  # 새로 저장할 폴더
    # if not os.path.exists(path):  # 폴더가 없는 경우 생성하기
    #     os.makedirs(path)
    #     return "false"
    # else:  # 폴더가 있는 경우 폴더에 크롭이미지 저장
    #     crop_image_name = row['origin_video_name']  # '방구석 수련회 장기자랑 - YouTube - Chrome 2021-11-05 04-18-36.mp4'
    #     # 구현 완료 후 : 동영상 이름을 지정
    #
    #     crop_image_path = row['saved_video_name']
    #
    #
    #     shutil.copy(video_path, path)  # 일단은 기존 영상을 새로운 폴더에 복사하는 형태로 해둠
    #
    #     new_video_path = "{}\{}".format(path, saved_video_name)  # 완성 영상이 저장될 새로운 경로
    #
    #     sql = "INSERT INTO processed_video(processed_video_name, saved_video_name, video_path) \
    #                         VALUES(%s, %s, %s)"  # 완료된 영상을
    #     val = (processed_video_name, saved_video_name, new_video_path)
    #     row = dbClass.executeOne(sql, val)
    #     dbClass.commit()

    # all_crops = []  # [id,img],[id,img] 형태로 저장 (트래커별로 저장)
    # id_=1
    #
    # result=[]
    # for c in all_crops:
    #     # print("id: " + str(c[0]))
    #     result.append({
    #         c[0]: c[1]
    #     })
    #     # pp.imshow(c[1])
    #     # pp.show()
    #
    # print(result)
    return jsonify({'cropImages': 'hi'})


# 스프링으로 데이터 보내는 테스트 코드
# @app.route("/sendVideoId", methods=['GET'])
# def sendVideoId():
#
#     return "test"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
