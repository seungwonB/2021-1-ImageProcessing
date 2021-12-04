import numpy as np, cv2
from Common.interpolation import contain, translate
from header.edit_utils import *
from header.edit_init import *
import dlib
from math import hypot

# 아이콘 눌러서 실행하기
def onMouse(event, x, y, flags, param):
    global pt1, pt2, mouse_mode, draw_mode

    if event == cv2.EVENT_LBUTTONUP:  # 왼쪽 버튼 떼기
        for i, (x0, y0, w, h) in enumerate(icons):  # 메뉴아이콘 사각형 조회
            if x0 <= x < x0 + w and y0 <= y < y0 + h:  # 메뉴 클릭 여부 검사
                command(i)
                return
        pt2 = (x, y) # 종료좌표 저장
        mouse_mode = 1 # 버튼 떼기 상태 지정

    elif event == cv2.EVENT_LBUTTONDOWN: # 왼쪽 버튼 누르기
        pt1 = (x, y)  # 시작좌표 저장
        mouse_mode = 2

# 아이콘 실행 함수
def command(mode):
    global icons, image, title, image_copy, image_copy2, icons_width, icons_height, res, imgColorLips, rows, cols

    # 원본 이미지로 변경 (1)
    if mode == ORIGINAL:  
        image_copy = np.copy(image)

    # 좌우 반전 (2)
    elif mode == FLIP:
        image_copy = np.flip(image_copy, 1)

    # 회전 (3)
    elif mode == ROTATE:
        def onRotation(value):
            global angle
            angle = value
            rotation = cv2.getRotationMatrix2D(center, angle, 1) # 중심좌표 기준으로 angle만큼 회전
            res = cv2.warpAffine(image_copy, rotation, (cols, rows)) # 어파인 함수에 저장
            cv2.imshow(title, res)

        h, w, channel = image.shape
        center = int(w / 2), int(h / 2) # 중심좌표
        angle = 0 # 회전할 각도
        rows, cols = h, w # 세로, 가로
        cv2.imshow(title, image_copy)
        cv2.createTrackbar("rotate", title, 0, 360, onRotation)


    # 워핑 (4)
    elif mode == WARP:
        def onMouse(event, x, y, flags, param):
            global pt1, pt2
            if event == cv2.EVENT_LBUTTONDOWN:
                pt1 = (x, y)  # 드래그 시작 좌표
            elif event == cv2.EVENT_LBUTTONUP:
                pt2 = (x, y)  # 드래그 종료 좌표
                morphing(image, pt1, pt2, image_copy, title)  # 드래그 종료 시 워핑 변환 수행
            elif event == cv2.EVENT_RBUTTONDBLCLK:
                pt1 = pt2 = (-1, -1)
                cv2.imshow(title, image_copy)  # 오른쪽 버튼 더블 클릭 시 원래 이미지로 변경

        image_copy = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
        pt1 = pt2 = (-1, -1)
        cv2.imshow(title, image_copy)
        cv2.setMouseCallback(title, onMouse, 0)

    # 대비 증가 (5)
    elif mode == PLUS:
        val = np.full(image_copy.shape, 10, np.uint8)
        cv2.add(image_copy, val, image_copy)
        
    # 대비 감소 (6)
    elif mode == MINUS:
        val = np.full(image_copy.shape, 10, np.uint8)
        cv2.subtract(image_copy, val, image_copy)
    
    # 샤프닝 (7)
    elif mode == SHARPEN:
        image_copy = cv2.filter2D(image, -1, data1) 

    # 블러 (8)
    elif mode == BLUR:
        hair = 30 # 앞머리까지 처리하기 위한 값
        gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray) # 전처리
        faces = face_cascade.detectMultiScale(gray, 1.1, 2, 0, (100, 100)) # 얼굴 검출
        # 얼굴 제외하고 블러하기
        def onNoFace(value):
            global image_copy, image, title
            if value % 2 == 1:
                image_copy2 = cv2.GaussianBlur(image_copy, (value, value), 0) # 모든 영역 블러처리
                image_copy2[y-hair:y + h, x:x + w] = face_image # 해당 영역에만 얼굴 이미지 삽입
                cv2.imshow(title, image_copy2)
        # 얼굴만 블러하기
        def onFace(value):
            global image_copy, image, title
            if value % 2 == 1:
                blur2 = cv2.GaussianBlur(face_image, (value, value), 0) # 얼굴 부분 블러처리
                image_copy[y-hair:y + h, x:x + w] = blur2
                cv2.imshow(title, image_copy)
        if faces.any():
            x, y, w, h = faces[0]
            face_image = image[y-hair:y + h, x:x + w]
        cv2.createTrackbar("Blur-No", title, 0, 50, onNoFace)
        cv2.createTrackbar("Blue-Face", title, 0, 50, onFace)
        image_copy2 = image_copy

    # CMY 필터 (10)
    elif mode == CMY:
        white = np.array([255, 255, 255], np.uint8)
        image_copy = white - image_copy

    # 스케치 필터 (11)
    elif mode == SKETCH:
        image_copy = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        crow, ccol = rows // 2, cols // 2
        val = 1 # 사용자가 지정해줘야 하는 값
        f = np.fft.fft2(image_copy) # fft 수행
        fshift = np.fft.fftshift(f) # shift 수행
        fshift[crow - val:ccol + val, crow - val:ccol + val] = 0 # 해당 영역 0으로 전환
        f_shift = np.fft.fftshift(fshift) # 또 다시 shift 수행
        image_copy = np.fft.ifft2(f_shift) # 역 변환
        image_copy = np.abs(image_copy)
        image_copy = cv2.convertScaleAbs(image_copy) # 정수형으로 표시

    # 사람 얼굴 인식하여 마스크 씌우기 (12)
    elif mode == MASK:
        mask_image = cv2.imread("../images/mask.png") # 마스크 이미지

        gray_frame = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        faces = detector(image_copy) # 얼굴 검출

        for face in faces:
            landmarks = predictor(gray_frame, face) # 좌표 획득
            center_face = (landmarks.part(51).x, landmarks.part(51).y) # 얼굴의 중심 좌표
            left_face = (landmarks.part(0).x, landmarks.part(0).y) # 얼굴의 좌측 좌표
            right_face = (landmarks.part(16).x, landmarks.part(16).y) # 얼굴의 우측 좌표
            face_width = int(hypot(left_face[0] - right_face[0],
                                   left_face[1] - right_face[1]) * 1.2) # 얼굴 가로 길이 (임의의 값을 곱해 크기 조정)
            face_height = int(face_width * 0.77) # 얼굴 세로 길이 (임의의 값을 곱해 크기 조정)

            top_left = (int(center_face[0] - face_width / 2),
                        int(center_face[1] - face_height / 2)) # 좌측 상단
            bottom_right = (int(center_face[0] + face_width / 2),
                            int(center_face[1] + face_height / 2)) # 우측 하단

            mask_img = cv2.resize(mask_image, (face_width, face_height)) # 마스크 이미지를 얼굴의 크기에 맞게 조정
            mask_img_gray = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
            _, mask_mask = cv2.threshold(mask_img_gray, 25, 255, cv2.THRESH_BINARY_INV) # 마스크 쓰는 부분의 mask

            mask_area = image_copy[top_left[1]:top_left[1] + face_height,
                        top_left[0]:top_left[0] + face_width] # 마스크 씌울 영역
            mask_area_no_mask = cv2.bitwise_and(mask_area, mask_area, mask=mask_mask) # 코 부분 획득

            final_mask = cv2.add(mask_area_no_mask, mask_img) # 마스크 이미지와 코 부분을 합성

            image_copy[top_left[1]:top_left[1] + face_height,
            top_left[0]:top_left[0] + face_width] = final_mask # 이미지의 코 영역에 마스크 삽입

    # 사람 입술 색 변경하기 (13)
    elif mode == LIPS:
        def blue(value):
            global b, imgColorLips
            b = value
            imgColorLips[:] = b, g, r
            imgColorLips = cv2.bitwise_and(imgLips, imgColorLips)
            imgColorLips = cv2.GaussianBlur(imgColorLips, (7, 7), 10)
            imgColorLips = cv2.addWeighted(image_copy, 1, imgColorLips, 0.4, 0)
            cv2.imshow(title, imgColorLips)

        def green(value):
            global g, imgColorLips
            g = value
            imgColorLips[:] = b, g, r
            imgColorLips = cv2.bitwise_and(imgLips, imgColorLips)
            imgColorLips = cv2.GaussianBlur(imgColorLips, (7, 7), 10)
            imgColorLips = cv2.addWeighted(image_copy, 1, imgColorLips, 0.4, 0)
            cv2.imshow(title, imgColorLips)

        def red(value):
            global r, imgColorLips
            r = value
            imgColorLips[:] = b, g, r
            imgColorLips = cv2.bitwise_and(imgLips, imgColorLips)
            imgColorLips = cv2.GaussianBlur(imgColorLips, (7, 7), 10)
            imgColorLips = cv2.addWeighted(image_copy, 1, imgColorLips, 0.4, 0)
            cv2.imshow(title, imgColorLips)

        cv2.createTrackbar("Blue", title, 0, 255, blue)
        cv2.createTrackbar("Green", title, 0, 255, green)
        cv2.createTrackbar("Red", title, 0, 255, red)

        imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(imgGray)
        for face in faces:
            landmarks = predictor(imgGray, face) # 얼굴 좌표 획득
            myPoints = []
            for n in range(68): # 얼굴 좌표는 총 67까지 있음
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                myPoints.append([x, y]) # 얼굴 좌표를 모두 저장
            myPoints = np.array(myPoints)
            imgLips = createBox(image, myPoints[48:61], 3, masked=True, cropped=False) # 입술 영역

            imgColorLips = np.zeros_like(imgLips)
            b = cv2.getTrackbarPos("Blue", title) # blue 값
            g = cv2.getTrackbarPos("Green", title) # green 값
            r = cv2.getTrackbarPos("Red", title) # red 값

            imgColorLips = cv2.bitwise_and(imgLips, imgColorLips) # trackbar를 통해 얻은 색상값과 입술영역 합치기
            imgColorLips = cv2.GaussianBlur(imgColorLips, (7, 7), 10) # 약간의 블러처리
            imgColorLips = cv2.addWeighted(image_copy, 1, imgColorLips, 0.4, 0) #

    # 사람 코 인식하여 이미지 씌우기 (14)
    elif mode == NOSE:
        gray_frame = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        faces = detector(image_copy)
        nose_image = cv2.imread("../images/pig.png")

        for face in faces:
            landmarks = predictor(gray_frame, face)
            top_nose = (landmarks.part(29).x, landmarks.part(29).y)
            center_nose = (landmarks.part(30).x, landmarks.part(30).y)
            left_nose = (landmarks.part(31).x, landmarks.part(31).y)
            right_nose = (landmarks.part(35).x, landmarks.part(35).y)
            nose_width = int(hypot(left_nose[0] - right_nose[0],
                                   left_nose[1] - right_nose[1]) * 1.9)
            nose_height = int(nose_width * 0.77)

            top_left = (int(center_nose[0] - nose_width / 2),
                        int(center_nose[1] - nose_height / 2))
            bottom_right = (int(center_nose[0] + nose_width / 2),
                            int(center_nose[1] + nose_height / 2))

            nose_pig = cv2.resize(nose_image, (nose_width, nose_height))
            nose_pig_gray = cv2.cvtColor(nose_pig, cv2.COLOR_BGR2GRAY)
            _, nose_mask = cv2.threshold(nose_pig_gray, 25, 255, cv2.THRESH_BINARY_INV)
            nose_area = image_copy[top_left[1]:top_left[1] + nose_height,
                        top_left[0]:top_left[0] + nose_width]
            nose_area_no_nose = cv2.bitwise_and(nose_area, nose_area, mask=nose_mask)
            final_nose = cv2.add(nose_area_no_nose, nose_pig)

            image_copy[top_left[1]:top_left[1] + nose_height,
            top_left[0]:top_left[0] + nose_width] = final_nose

    # 웹캠으로 찍은 사진으로 사진 편집하기 (15)
    elif mode == FOLDER:
        image = cv2.imread("../images/icon2/selfcam.png", cv2.IMREAD_COLOR)
        image_copy = np.copy(image)
        rows, cols = image.shape[:2]
        if icons_width > cols:
            res = icons_width
        else:
            res = cols
        img = np.full((rows+icons_height, res, 3), 125, np.uint8)
        icons = place_icons(img, (60, 60))
        img[icons_height:rows + icons_height, :cols] = image
        cv2.imshow("Edit Program", img)
        cv2.imshow(title, image_copy)

    # 웹캠으로 사진 찍기 (16)
    elif mode == CAMERA:
        capture = cv2.VideoCapture(0)  # 노트북 웹캠을 카메라로 사용
        if capture.isOpened() == False: raise Exception("카메라 연결 안됨")
        capture.set(3, 384)  # 너비
        capture.set(4, 374)  # 높이

        ret, frame = capture.read()  # 사진 촬영
        frame = cv2.flip(frame, 1)  # 좌우 대칭

        cv2.imwrite('../images/icon2/selfcam.png', frame)  # 사진 저장
        capture.release()

    cv2.imshow(title, image_copy)

image = cv2.imread("../images/man.jpg", cv2.IMREAD_COLOR)
if image is None: raise Exception("영상파일 읽기 에러")
image_copy = np.copy(image)
image_copy2 = np.copy(image)


rows, cols = image.shape[:2]

icons_width = 481 # 아이콘의 가로 길이 + 1
icons_height = 121 # 아이콘의 세로 길이 + 1
title = "copy_image" # 편집하는 윈도우의 타이틀

# 편집 프로그램 사이즈 정하기
if icons_width > cols: # 아이콘의 길이가 길면 
    res = icons_width # 아이콘의 길이대로
else: # 사진의 길이가 길면
    res = cols # 사진의 길이대로

img = np.full((rows+icons_height, res, 3), 125, np.uint8) # 아이콘 + 이미지 영역
icons = place_icons(img, (60, 60)) # 아이콘 배치

img[icons_height:rows+icons_height, :cols] = image # 아이콘 밑 부분에 이미지 배치

cv2.imshow("Edit Program", img)
cv2.imshow(title, image_copy)
cv2.setMouseCallback("Edit Program", onMouse)

cv2.waitKey(0)

