import numpy as np, cv2
import dlib

ORIGINAL = 0  # 원본 이미지
FLIP = 1  # 좌우 반전
ROTATE = 2  # 회전
WARP = 3  # 와핑
PLUS = 4  # 대비 증가
MINUS = 5  # 대비 감소
SHARPEN = 6  # 샤프닝
BLUR = 7  # 블러
FILTER = 8  # nothing
CMY = 9  # CMY 필터
SKETCH = 10 # 스케치 필터
MASK = 11 # 마스크 씌우기
LIPS = 12 # 입술 색 변경
NOSE = 13 # 코에 이미지 씌우기
FOLDER = 14 # 찍은 사진 열기
CAMERA = 15 # 사진 찍기

# 전역 변수
mouse_mode, draw_mode = 0, 0
pt1, pt2, Color = (0, 0), (0, 0), (0, 0, 0)

# 샤프닝 data
data1 = np.array([[0, -1, 0],
         [-1, 5, -1],
         [0, -1, 0]])

# 얼굴 검출 - harr
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")

# 얼굴 검출 - dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
