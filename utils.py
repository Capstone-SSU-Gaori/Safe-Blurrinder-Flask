import hashlib
import os

def iou(b1, b2):
    #x1,y1,x2,y2 순서로 값이 넘어옴 (순서대로 [0],[1],[2],[3])

    # 겹치는 영역 계산용 좌표
    max_x = max(b1[0], b2[0])
    max_y = max(b1[1], b2[1])
    min_x = min(b1[2], b2[2])
    min_y = min(b1[3], b2[3])

    # 겹치는 영역이 아예 없으면 확인 X, 바로 return
    if max_x-min_x >= 0 or max_y-min_y>= 0:
        return 0

    b1_w=b1[2]-b1[0]
    b1_h=b1[3]-b1[1]
    b2_w=b2[2]-b2[0]
    b2_h=b2[3]-b2[1]

    b1_size = b1_w*b1_h
    b2_size = b2_w*b2_h

    intersection = (min_x - max_x) * (min_y - max_y) # 교집합 영역  크기
    union = b1_size + b2_size - intersection # 합집합 영역 크기

    return intersection / union  # 교집합/합집합 비율 return -> 클 수록 동일 인물일 가능성이 높아진다.

def generate_hash(origin_text):
    md5_hash = hashlib.md5()
    origin_text=origin_text.encode('utf-8')

    salt=os.urandom(16) #랜덤성 추가
    md5_hash.update(origin_text+salt)
    hashed=md5_hash.hexdigest()

    return hashed