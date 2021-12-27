from tqdm import tqdm_notebook as tqdm
from mtcnn import MTCNN
import cv2
from faceRecognition import faceRecognition
import dlib
from imutils import face_utils

### 비디오 전역변수   -> set_tracker 함수로 호출하면서 전역변수 setting ###
vid_name = None

### .py 파일 내에서의 전역변수들
all_lists = []  # [x1,y1,x2,y2,frame_id,obj_id],[],[],,, 형태로 저장
all_crops = []  # [id,img],[id,img] 형태로 저장 (트래커별로 저장)

model_name = "Dlib"

def start_tracker(cap):
    face = faceRecognition()
    face.setCap(cap)  # 얼굴인식 파일에서 사용할 비디오 이름 setting
    cap,width,height,fourcc,fps,out = set_video_settings(cap)

    id_ = 1
    ddetector = dlib.get_frontal_face_detector()
    trackers = []

    for i in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
        retval, frame = cap.read()

        if i == 0:  # 첫 번째 프레임이라면?
            tem = []  # 첫 프레임의 모든 탐지 얼굴들 좌표 저장할 list

            #           result = detector.detect_faces(frame)
            rects = ddetector(frame, 1)
            result = []
            for rect in rects:
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                result.append([x, y, w, h])

            if result != []:  # 감지된 얼굴이 존재한다면
                for person in result:
                    #               if person['confidence']<0.8:
                    #                 continue
                    #               bounding_box = person['box']
                    bounding_box = person
                    x = bounding_box[0]
                    y = bounding_box[1]
                    w = bounding_box[2]
                    h = bounding_box[3]
                    # all_lists에 모든 탐지 객체좌표와 id, frame_id를 2차원 배열로 저장
                    all_lists.append([x, y, x + w, y + h, i, id_])

                    # 얼굴 식별 후 해당 얼굴의 crop image와 객체 id 반환
                    crop, found_id = face.get_cropimg(id_, i, x, y, w, h, True, model_name)
                    all_crops.append([found_id, crop])  # all_crops에 한 트래커의 대표 crop image와 id 저장
                    tem.append([x, y, w, h, found_id])  # tem에 탐지한 모든 얼굴들의 좌표를 저장 -> tracker 초기 세팅에 사용할 좌표
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 155, 255), 2, 1)
                    cv2.putText(frame, "id: " + str(id_), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                                cv2.LINE_AA)
                    id_ += 1

            # tracker 초기 세팅 [tracker,추적중인 객체 id]
            for t in range(len(tem)):
                trackers.append([cv2.TrackerCSRT_create(), tem[t][4]])  # trackers에 [트래커, id]
                trackers[t][0].init(frame,
                                    (tem[t][0], tem[t][1], tem[t][2], tem[t][3]))  # [x,y,w,h]로 탐지한 각 얼굴마다 tracker 초기화

        else:  # 첫 번째 프레임이 아니라면? -> 기존에 존재하던 tracker를 업데이트 (현재 프레임의 정보를 넣어서)
            this_box = []  # 이번 프레임에서 탐지한 객체들의 (x,y,w,h)를 저장

            rects = ddetector(frame, 1)
            result = []
            for rect in rects:
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                result.append([x, y, w, h])

            #           result = detector.detect_faces(frame)
            if result != []:  # 감지된 얼굴이 존재한다면
                for person in result:
                    #               if person['confidence']<0.8:
                    #                 continue
                    bounding_box = person
                    this_box.append(bounding_box)

            # 만약 감지된 얼굴 수가 트래커의 수보다 많으면 트래커 다 초기화 하고 다시 추적
            if (len(this_box) > len(trackers)):
                print("change")

                #             trackers,frame,id_=new_tracker(frame,this_box,id_)
                trackers = []
                for t in range(len(this_box)):
                    x = this_box[t][0]
                    y = this_box[t][1]
                    w = this_box[t][2]
                    h = this_box[t][3]
                    test = [x, y, x + w, y + h]

                    crop, found_id = face.get_cropimg(id_, i, x, y, w, h, False, model_name)
                    if found_id == id_:  # 현재 id랑 같다, 즉 이전에 동일한 얼굴이 탐지된 적이 없었다
                        id_ += 1
                    trackers.append([cv2.TrackerCSRT_create(), found_id])  # [tracker, 추적하는 객체 id]
                    trackers[t][0].init(frame, (x, y, w, h))

                    all_crops.append([found_id, crop])  # 현재 트래커가 추적하는 객체의 crop image, id 저장
                    all_lists.append([x, y, x + w, y + h, i, found_id])  # 좌표 저장
                #   cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
                #   cv2.putText(frame, "id: "+str(found_id), (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)

            else:
                # 트래커가 하나라도 객체를 놓치면(여러 이유로 인해) 그렇다면 트래커 배열 싹다 비운다.그리고 mtcnn으로 출력후 다시 초기설정
                judge = True
                tempor = []
                for track in trackers:
                    res, box = track[0].update(frame)
                    if res:
                        x1 = int(box[0])
                        y1 = int(box[1])
                        x2 = int(box[0] + box[2])
                        y2 = int(box[1] + box[3])
                        tempor.append([x1, y1, x2, y2, track[1]])

                    else:
                        judge = False
                        print(False)

                if (judge == True):  # 트래커가 모든 객체를 정상적으로 탐지했을 때
                    passok = False
                    if len(this_box) < (len(trackers) - 2) or (
                            len(trackers) == 2 and (565 < i < 580 or 670 < i < 680 or 764 < i < 775) and len(
                            this_box) == 1):

                        checkcheck = []
                        for tb in this_box:
                            crop, found_id = face.get_cropimg(id_, i, tb[0], tb[1], tb[2], tb[3], False, model_name)
                            if found_id != id_:
                                checkcheck.append(found_id)

                        isok = False
                        for c in checkcheck:
                            for track in trackers:
                                if c == track[1]:
                                    isok = True
                                    break
                        if checkcheck == []:
                            passok = False

                        if 1 not in checkcheck:
                            isok = True

                        elif isok == False or (len(checkcheck) == 1 and (checkcheck[0] == 1 or checkcheck[0] == 2)):
                            # 트래커 재시작으로 보내주기
                            print("frame: " + str(i))
                            trackers, frame, id_ = new_tracker(frame, this_box, id_, i)
                            passok = True

                    elif len(this_box) == len(trackers) == 2 and (
                            358 < i < 366 or 423 < i < 429):  # 게스트 <-> 안영미, 김구라 변환 2회
                        passok = False
                        tem_id = id_
                        checkcheck = []
                        for tb in this_box:
                            crop, found_id = face.get_cropimg(tem_id, i, tb[0], tb[1], tb[2], tb[3], False, model_name)
                            checkcheck.append(found_id)
                            tem_id += 1

                        isok = False
                        for c in checkcheck:
                            for track in trackers:
                                if c == track[1]:
                                    isok = True
                                    break

                        if isok == False and len(checkcheck) == 2:
                            track_list = []
                            for track in trackers:
                                track_list.append(track[1])
                            if (1 in track_list and 2 in track_list) or (1 in checkcheck and 2 in checkcheck):
                                print("frame: " + str(i))
                                trackers, frame, id_ = new_tracker(frame, this_box, id_, i)
                                passok = True

                    if passok == False:
                        for t in range(len(tempor)):  # tempor (새롭게 탐지한 객체의 좌표를 추가함) -> 현재 프레임의 update 정보 반영
                            x1, y1, x2, y2, tracker_id = tempor[t]
                            # cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2,1)
                            # cv2.putText(frame, "id: "+str(tracker_id), (int(x1),int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
                            all_lists.append([x1, y1, x2, y2, i, tracker_id])

                else:  # 트래커가 객체를 하나라도 놓쳤을 때 -> 새롭게 트래커 시작
                    #                 trackers,frame,id_=new_tracker(frame,this_box,id_)
                    trackers = []  # trackers를 초기화
                    for t in range(len(this_box)):
                        x, y, w, h = this_box[t]
                        crop, found_id = face.get_cropimg(id_, i, x, y, w, h, False, model_name)
                        if found_id == id_:  # 현재 id랑 같다, 즉 이전에 동일한 얼굴이 탐지된 적이 없었다 else라면 found_id는 이전에 탐지한 객체의 id
                            id_ += 1
                        trackers.append([cv2.TrackerCSRT_create(), found_id])
                        trackers[t][0].init(frame, (x, y, w, h))
                        all_crops.append([found_id, crop])  # 어떤 경우에든 id랑 crop image둘 다 저장 (인식 실패 가능성)
                        all_lists.append([x, y, x + w, y + h, i, found_id])

                        # cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
                        # cv2.putText(frame, "id: "+str(found_id), (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)

        out.write(frame)

def new_tracker(frame, this_box, id_, i):
    face = faceRecognition()
    print("start new tracker")
    trackers = []  # trackers를 초기화
    for t in range(len(this_box)):
        x, y, w, h = this_box[t]
        crop, found_id = face.get_cropimg(id_, i, x, y, w, h, False, model_name)
        if found_id == id_:  # 현재 id랑 같다, 즉 이전에 동일한 얼굴이 탐지된 적이 없었다 else라면 found_id는 이전에 탐지한 객체의 id
            id_ += 1
        trackers.append([cv2.TrackerCSRT_create(), found_id])
        trackers[t][0].init(frame, (x, y, w, h))
        all_crops.append([found_id, crop])  # 어떤 경우에든 id랑 crop image둘 다 저장 (인식 실패 가능성)
        all_lists.append([x, y, x + w, y + h, i, found_id])

        #   cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
    #   cv2.putText(frame, "id: "+str(found_id), (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)

    return trackers, frame, id_

def get_all_crops():
    global all_crops
    return all_crops


def get_all_lists():
    global all_lists
    return all_lists


def set_video_settings(cap):
    width = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))

    return cap,width,height,fourcc,fps,out
