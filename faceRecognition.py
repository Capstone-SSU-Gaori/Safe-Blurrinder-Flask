import numpy as np
from tensorflow.keras.models import load_model
import glob
from scipy.spatial.distance import cosine
import cv2
import dlib

# models for dlib landmark
sp = None
facerec = None

# modles for facenet keras
facenet_model = None

# 각 사람의 object_id, crop_img encoding value 담김
all_encodings = []  # saving face image encodings for facenet_keras
all_crops = []  # saving all crop faces
face_vectors = []  # saving face image vectors from 68 landmarks with id_ [vector,id_] format

cap = cv2.VideoCapture('short.mp4')

class faceRecognition:
    def find_by_euclidean(self, img, now_id):
        distance = float("inf")
        found_id = now_id
        for vec in face_vectors:
            dis = img - vec[0]
            dis = np.sum(np.multiply(dis, dis))
            dis = np.sqrt(dis)
            if dis < distance and dis < 0.6:
                found_id = vec[1]
                distance = dis

        return found_id

    #  # use facenet_keras model
    def check_existence(self, now_id, encode, firstFrame):
        distance = float("inf")
        isFinal = False
        found_id = now_id;  # 초기 found_id는 이 객체의 고유 id로 설정

        if firstFrame == True:
            all_encodings.append([now_id, encode])
        else:
            for e in all_encodings:
                dist = cosine(e[1], encode)  # 기존 encoding list 돌면서 현재 얼굴의 encoding과 비교 -> 비교 결과를 dist에 저장  -> 유클리드로 바꾸기

                if dist < 0.5 and dist < distance:  # dist가 해당 조건을 만족하면 update -> 가장 dist가 작은 얼굴을 찾음: 동일얼굴이라 인식
                    found_id = e[0]
                    distance = dist

        if found_id == now_id:  # found_id가 변화하지 않았다는 의미 => 동일한 얼굴이 없다 -> encoding list에 비교대상이 되어야할 새 얼굴로 추가
            all_encodings.append([now_id, encode])

        return found_id

    def get_cropimg(self, now_id, frame_id, x1, y1, w, h, firstFrame, model="Dlib"):  # model명 받는걸로 바꿔주기

        cap.set(1, frame_id);
        ret, frame = cap.read()

        x1, y1 = int(abs(x1) - 5), int(abs(y1) + 5)
        x2, y2 = x1 + int(w) + 10, y1 + int(h) + 10
        crop_face = frame[y1:y2, x1:x2]

        if model == "Dlib":
            sp = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
            rect = dlib.rectangle(x1, y1, x1 + w, y1 + h)
            img_shape = sp(frame, rect)
            img_aligned = dlib.get_face_chip(frame, img_shape)
            img_representation = facerec.compute_face_descriptor(img_aligned)
            img_representation = np.array(img_representation)
            if firstFrame == True:
                face_vectors.append([img_representation, now_id])
                return crop_face, now_id;
            found_id = self.find_by_euclidean(img_representation, now_id)
            if found_id == now_id:
                face_vectors.append([img_representation, found_id])

        if model == "FaceNet":
            facenet_model = load_model('facenet_keras.h5')
            face = cv2.resize(crop_face, (160, 160))
            face = np.expand_dims(face, axis=0)
            face = (face - face.mean()) / face.std()
            encode = facenet_model.predict(face)
            found_id = self.check_existence(now_id, encode, firstFrame)

        return crop_face, found_id


    # def find_by_cosine(self, img, now_id):
    #     distance = float("inf")
    #     found_id = now_id
    #     for vec in face_vectors:
    #         dis = cosine(vec[0], encode)
    #         if dis < distance and dis < 0.6:
    #             found_id = vec[1]
    #             distance = dis
    #
    #     return found_id
