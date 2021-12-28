import cv2
from tqdm import tqdm_notebook as tqdm
import numpy as np

# lst_all = [x,y,w,h,obj_id,frame_id] / lst_remove = 블러처리 제외할 객체 리스트[obj_di, obj_id,,,,,,,]
def blurr_apply(lst_all, lst_remove,cap,pathandName):
    # cap = cv2.VideoCapture('test.mp4')
    w = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fps = cap.get(cv2.CAP_PROP_FPS)

    saveVidPath=pathandName+".mp4"
    print("save Name and path: "+str(saveVidPath))  # ~\GaoriProcessedVideos\원본비디오이름_output.avi => 해당 경로에 원본이름_output.avi 가 저장됨
    out = cv2.VideoWriter(saveVidPath, fourcc, fps, (w, h))

    for i in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
        retval, frame = cap.read()
        # 일단 같은 프레임인지 찾는다. 근데 lst_all 엄청 길텐데 그럼 효율이 쓰레기가 되지 않을까
        for t in range(0, len(lst_all)):
            # 프레임의 번호가 같을때
            if lst_all[t][4] == i:

                # 이 부분은 리스트에 remove 리스트에 있는 객체만 제외시키려고!
                check = True
                for a in range(0, len(lst_remove)):
                    if lst_all[t][5] == lst_remove[a]:
                        check = False

                # 블러처리하는 부분 입니다,
                if check == True:
                    height = abs(int(lst_all[t][1]) - int(lst_all[t][3]))
                    width = abs(int(lst_all[t][0]) - int(lst_all[t][2]))
                    yPos = min(int(lst_all[t][1]), int(lst_all[t][3]))
                    xPos = min(int(lst_all[t][0]), int(lst_all[t][2]))

                    # 좌표가 음수인 경우 0 으로 처리
                    if xPos < 0:
                        xPos = 0

                    if yPos < 0:
                        yPos = 0

                    face_img = frame[yPos:yPos + height, xPos:xPos + width]  # 탐지된 얼굴 크롭

                    htemp, wtemp, size = face_img.shape
                    face_temp_img = frame[yPos:yPos + htemp, xPos:xPos + wtemp]
                    c_mask = np.zeros((htemp, wtemp), np.uint8)
                    img = cv2.circle(c_mask, (wtemp // 2, htemp // 2), min(wtemp, htemp) // 2, 1, thickness=-1)

                    mask = cv2.bitwise_and(face_temp_img, face_temp_img, mask=c_mask)

                    img_mask = face_temp_img - mask
                    blur = cv2.blur(face_temp_img, (11, 11))
                    mask2 = cv2.bitwise_and(blur, blur, mask=c_mask)  # mask
                    final_img = img_mask + mask2
                    frame[yPos:yPos + htemp, xPos:xPos + wtemp] = final_img

            # 이 부분이 있는 이유는 조금이라도 효율을 높이고자 프레임 값이 현재 프레임보다 1 크면 걍 뒤에있는 모든 배열 값을 넘겨버린다! 이겁니다!
            elif lst_all[t][5] == i + 1:
                t = len(lst_all)

        out.write(frame)

    return saveVidPath

