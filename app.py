import os
import pathlib
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from flask import Flask, request, jsonify
from mod_dbconn import mod_dbconn
import cv2
from faceTracker import start_tracker, get_all_crops, get_all_lists
from faceBlurring import blurr_apply
from utils import generate_hash

app = Flask(__name__)
dbClass = mod_dbconn.Database()
global videoPath
allLists=[]

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
@app.route('/getVideoId', methods=['GET','POST'])
def getVideoId():
    print("요청옴")
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
        global images
        images = processVideo(str(videoPath))
        # return jsonify({'cropImages': images})
        # finishProcess(images)
        return images
    else:
        return "Test"  # 완성 영상비디오 번호를 리턴하도록 바꾸기


# @app.route('/finishProcess',methods=['GET']) #쪼개다가 실패한,,, 부분
# def finishProcess():
#     return images


# 아래 부분 일단 GET으로 바꿈 + id임의 지정으로 제대로 로컬에 저장되는지, DB에 저장되는지 까지만 확인했음
@app.route('/applyBlur',methods=['POST'])
def applyBlur():
    print('JSON확인 : ', request.is_json) # ㅎ.ㅎ 은주언니 코드는 제가 훔쳐갑니다 ^~^
    content = request.get_json()
    videoId = int(content['videoId'])  # getVideoID와 마찬가지로 블러 적용해야할 영상을 uploaded_video에서 꺼내옴
    sql = "SELECT * \
                    FROM uploaded_video \
                    WHERE _id=%s"
    row = dbClass.executeOne(sql, videoId)
    dbClass.commit()

    # 고민되는게 좌표담긴 list를 DB에 저장해야할지 아니면 전역변수로 그냥 둬도 괜찮을지,,, 를 모르겠네요
    # DB에 저장해야 한다면 그냥 varchar로 저장해서 , 단위로 자르고 -> 6칸씩 나눠서 다시 2차원 배열로 만들어 넘겨야할지
    videoPath = row['video_path']
    videoName=row['origin_video_name']

    blurAppliedId=process_blur(str(videoPath),str(videoName))
    return str(blurAppliedId) # 블러 적용하고 processedVideo2 DB에 저장된 영상의 id를 return


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
    global allLists
    allLists=positions_with_obj_id_frame_id_list # global 변수 allLists에 [[x1,y1,x2,y2,frame_id,obj_id],[]] 저장 
    crop_img_with_obj_id_list = get_all_crops()
    images = saveImage(crop_img_with_obj_id_list)
    print(images)
    # print(allLists)
    return jsonify({'cropImages': images})

def saveImage(crop_img_with_obj_id_list):
    path = str(pathlib.Path.home()) + "\GaoriCropImages"  # 새로 저장할 폴더
    if not os.path.exists(path):  # 폴더가 없는 경우 생성하기
        os.makedirs(path)
        return "false"
    else:  # 폴더가 있는 경우 폴더에 이미지 저장
        # tempResult = {}
        # i = 0
        # c = 0
        # for i, c in enumerate(crop_img_with_obj_id_list):
        #     cv2.imwrite(path + "\\" + str(i) + ".png", c[1])  # 이렇게 하면 id.png 로 대표 얼굴 저장됨니다
        #     # json 형식으로 변환   ex) 객체 번호 : 이미지 저장된 경로
        #     fileNum = "frame"+str(c[0])+"_"+str(i)
        #     tempResult[fileNum] = path + "\\" + str(i) + ".png"
        tempResult = []
        i = 0
        c = 0
        for i, c in enumerate(crop_img_with_obj_id_list):
            cv2.imwrite(path + "\\" + str(i) + ".png", c[1])  # 이렇게 하면 id.png 로 대표 얼굴 저장됨니다
            # json 형식으로 변환   ex) 객체 번호 : 이미지 저장된 경로
            fileNum = "frame" + str(c[0])
            tempResult.append({
                fileNum: str(i) + ".png"
            })
        print(tempResult)
    return tempResult


def process_blur(videoPath,videoName):
    if os.path.isfile(videoPath):  # 해당 파일이 있는지 확인
        # 영상 객체(파일) 가져오기
        cap = cv2.VideoCapture(videoPath)
    else:
        print("파일이 존재하지 않습니다.")
        return -1

    path = str(pathlib.Path.home()) + "\GaoriProcessedVideos"  # 새로 저장할 폴더
    if not os.path.exists(path):  # 폴더가 없는 경우 생성하기
        os.makedirs(path)

    getOnlyName=videoName.split('.') # 뒤의 .mp4나 .avi를 잘라서 이름만 가져옴
    processedName=getOnlyName[0]+'_output' # 원래비디오이름_output
    hashedName=generate_hash(processedName) # 위의 이름의 hash값
    savePathandName=path+"\\"+hashedName # ~\GaoriProcessedVideos\hash값
    # print("save path and name: "+savePathandName)
    savePath=blurr_apply(allLists,[1,2],cap,savePathandName)  # [1,2]는 사용자가 선택한 블러 제외 대상이 들어와야함
    # savePath: ~\GaoriProcessedVides\hash값.avi
    
    _id=saveBlurredVideo(savePath,processedName)

    return _id


def saveBlurredVideo(savePath,processedName):
    splitForName=savePath.split("\\")
    hashedVidName=splitForName[-1] #hashedVidName: hash값.avi
    savedVidName=processedName+'.'+hashedVidName.split('.')[1] # 원본영상_output.avi


    # 데이터베이스에 영상 저장 후 ID 가져옴
    sql = "INSERT INTO processed_video2 (processed_video_name, saved_video_name, video_path) VALUES (%s, %s, %s)"
    val = (savedVidName, hashedVidName, savePath) # saved_video_name 나중에 hash값으로 변경해야함

    dbClass.executeOne(sql,val)
    dbClass.commit()

    sql = "SELECT * \
                    FROM processed_video2 \
                    WHERE saved_video_name=%s"
    row = dbClass.executeOne(sql, hashedVidName)
    dbClass.commit()

    _id=int(row['_id'])

    return _id
    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
