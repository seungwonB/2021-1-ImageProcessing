import numpy as np, cv2

# 아이콘 배치
def place_icons(image, size):
    icon_name = ["original", "flip", "rotation", "warp",
                 "plus", "minus", "sharpen", "blur", "filter", 'CMY', 'sketch', 'mask', 'lips', 'nose', 'folder', 'camera']
    icons = [(i%8, i//8, 1, 1) for i in range(len(icon_name))]
    icons = np.multiply(icons, size*2)

    for roi, name in zip(icons, icon_name):
        icon = cv2.imread('../images/icon2/%s.png' % name, cv2.IMREAD_COLOR)
        if icon is None: continue
        x, y, w, h = roi
        image[y:y+h, x:x+w] = cv2.resize(icon, size)
    return list(icons)

# drag morphing
def morphing(image, pt1, pt2, image_copy, title):
    h, w = image.shape[:2]
    dst = np.zeros((h, w), image.dtype)
    ys = np.arange(0, image.shape[0], 0.1) # y 좌표 인덱스
    xs = np.arange(0, image.shape[1], 0.1) # x 좌표 인덱스

    y1, y10 = pt1[1], pt1[1] * 10 # 0.1 간격의 10배(왜곡 값 정밀) y1은 클릭 된 좌표, y10은 인덱싱 위해 확대
    ratios = ys / y1 # 기본 변경 비율
    ratios[y10:] = (h - ys[y10:]) / (h - y1) # 클릭 좌표 이후 y좌표에 대한 변경 비율

    x1, x10 = pt1[0], pt1[0] * 10 # y와 동일
    ratios2 = xs / x1
    ratios2[x10:] = (w - xs[x10:]) / (w - x1)

    dys = ys + ratios * (pt2[1] - pt1[1]) # 수식에 따른 y 좌표의 변경 인덱스
    ys, dys = ys.astype(int), dys.astype(int) # 인덱스로 사용 위해 정수형으로 변경

    dxs = xs + ratios2 * (pt2[0] - pt1[0]) # 수식에 따른 x 좌표의 변경 인덱스
    xs, dxs = xs.astype(int), dxs.astype(int) # 인덱스로 사용 위해 정수형으로 변경

    ym, xm = np.meshgrid(ys, xs) # 원본 좌표 정방행렬
    dym, dxm = np.meshgrid(dys, dxs) # 변경 좌표 정방행렬
    dst[dym, dxm] = image_copy[ym, xm] # 원본 좌표를 목적 좌표로 매칭
    cv2.imshow(title, dst)

# 입술 영역
def createBox(image, points, scale=5, masked=False, cropped=True):
    if masked:
        mask = np.zeros_like(image) # image mask 생성
        mask = cv2.fillPoly(mask, [points], (255, 255, 255)) # 채워진 다각형 그리기
        image = cv2.bitwise_and(image, mask) # 입술 영역만 추출
    if cropped:
        bbox = cv2.boundingRect(points) # 경계면(입술)을 둘러싸는 사각형 계산
        x, y, w, h = bbox # 좌표 획득
        imageCrop = image[y:y + h, x:x + w] # 입술 영역
        return imageCrop
    else:
        return mask
