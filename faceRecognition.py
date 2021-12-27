import tensorflow as tf
from scipy.spatial.distance import cosine
import cv2
import dlib
from imutils import face_utils
import dlib
import numpy as np
from utils import iou

# models for dlib landmark
sp = None  # shape predictor
facerec = None  # face recognition model -> feature vector 생성
dlib_detector = dlib.get_frontal_face_detector()  # 얼굴인식 위한 재탐지에 사용할 모델

# modles for facenet keras
facenet_model = None

# 각 사람의 object_id, crop_img encoding value 담김
all_encodings = []  # saving face image encodings for facenet_keras
face_vectors = []  # saving face image vectors from 68 landmarks with id_ [vector,id_] format

# vid = None
cap = 0

class faceRecognition:
    cap = 0
    def setCap(self,cap):
        self.cap = cap
        return

    ###   crop img와 object_id를 return 하는 함수 ###
    def get_cropimg(self, now_id, frame_id, x1, y1, w, h, firstFrame, model="Dlib"):  # default model: dlib

        self.cap.set(1, frame_id)
        ret, frame = self.cap.read()

        x1, y1 = int(abs(x1) - 5), int(abs(y1) + 5)  # padding 추가
        x2, y2 = x1 + int(w) + 10, y1 + int(h) + 10
        crop_face = frame[y1:y2, x1:x2]  # 현재 식별해야 하는 얼굴의 crop image

        if model == "Dlib":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            global sp
            global facerec
            if sp is None:
                sp = dlib.shape_predictor("./models/shape_predictor_68_face_landmarks.dat")
            if facerec is None:
                facerec = dlib.face_recognition_model_v1("./models/dlib_face_recognition_resnet_model_v1.dat")

            rects = dlib_detector(frame, 1)  # dlib_detector로 얼굴 재탐지 (얼굴 식별용)
            found_box = []
            best_match = 0
            found_rect = None

            for (i, rect) in enumerate(rects):
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                iou_res = iou([x, y, w + x, h + y], [x1, y1, x2, y2])
                if iou_res > best_match and iou_res >= 0.3:  # iou로 재탐지한 얼굴 중, 현재 얼굴에 맞는 얼굴 좌표를 찾는다
                    best_match = iou_res
                    found_box = [x, y, w + x, h + y]
                    found_rect = rect

            if found_rect is None:  # dlib detector가 현재 식별해야 하는 얼굴을 탐지를 못했을 때 -> 그냥 crop image를 넘겨줌: 정확도 떨어짐
                found_rect = dlib.rectangle(x1, y1, x2, y2)
                found_box = [x1, y1, x2, y2]

            img_encoding = self.get_dlib_encoding(found_rect, frame)

            if firstFrame == True:
                face_vectors.append([img_encoding, now_id])
                return crop_face, now_id

            found_id, valid = self.find_by_euclidean(img_encoding, now_id)
            if valid == False:  # 간혹 인식을 이상하게 하는 경우 발생 -> 다시 crop image 넣어줘서 재식별
                print("invalid")
                found_rect = dlib.rectangle(x1, y1, x2, y2)
                found_box = [x1, x2, y1, y2]
                img_encoding = self.get_dlib_encoding(found_rect, frame)
                found_id, valid = self.find_by_euclidean(img_encoding, now_id)

            if found_id == now_id:
                face_vectors.append([img_encoding, found_id])

        if model == "FaceNet":
            global facenet_model
            if facenet_model is None:
                facenet_model = tf.keras.models.load_model('./models/facenet_keras.h5')
            face = cv2.resize(crop_face, (160, 160))
            face = np.expand_dims(face, axis=0)
            face = (face - face.mean()) / face.std()
            encode = facenet_model.predict(face)
            found_id = self.check_existence(now_id, encode, firstFrame)

        return crop_face, found_id


    def get_dlib_encoding(self, found_rect, frame):
        shape = sp(frame, found_rect)  # 얼굴에서 68좌표 추출
        img_aligned = dlib.get_face_chip(frame, shape)
        img_encoding = facerec.compute_face_descriptor(img_aligned)
        img_encoding = np.array(img_encoding)
        return img_encoding


    ###   유클리드 거리 공식으로 식별 (threshold값을 무엇으로 설정하냐에 따라 결과 크게 달라짐)  ###
    def find_by_euclidean(self, img, now_id):
        valid = True
        distance = float("inf")
        found_id = now_id
        check_dis = 0
        for vec in face_vectors:
            dis = img - vec[0]
            dis = np.sum(np.multiply(dis, dis))
            dis = np.sqrt(dis)
            if dis < distance:
                check_dis = dis
            if dis < distance and dis < 0.42:
                found_id = vec[1]
                distance = dis
        print("distance: " + str(check_dis) + ",  found_id: " + str(found_id))
        if distance == 0.000000000:
            valid = False
        return found_id, valid


    ### 코사인으로 식별 ###
    def find_by_cosine(self, img, now_id):
        distance = float("inf")
        valid = True
        found_id = now_id
        for vec in face_vectors:
            dis = cosine(vec[0], img)
            if dis < distance and dis < 0.42:
                found_id = vec[1]
                distance = dis
        print("cosine distance: " + str(distance) + ",  found_id: " + str(found_id))
        if distance == 0.0000000000:
            valid = False
        return found_id, valid


    #  facenet_keras model 사용할 경우, 코사인으로 식별
    def check_existence(self, now_id, encode, firstFrame):
        distance = float("inf")
        found_id = now_id;  # 초기 found_id는 이 객체의 고유 id로 설정

        if firstFrame == True:
            all_encodings.append([now_id, encode])
            return found_id
        else:
            for e in all_encodings:
                dist = cosine(e[1], encode)  # 기존 encoding list 돌면서 현재 얼굴의 encoding과 비교 -> 비교 결과를 dist에 저장  -> 유클리드로 바꾸기

                if dist < 0.5 and dist < distance:  # dist가 해당 조건을 만족하면 update -> 가장 dist가 작은 얼굴을 찾음: 동일얼굴이라 인식
                    found_id = e[0]
                    distance = dist
        print("distance: " + str(distance) + ",  found_id: " + str(found_id))
        if found_id == now_id:  # found_id가 변화하지 않았다는 의미 => 동일한 얼굴이 없다 -> encoding list에 비교대상이 되어야할 새 얼굴로 추가
            all_encodings.append([now_id, encode])

        return found_id
