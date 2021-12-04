# 프로그램 개요
<h3>1. 프로그램 설명</h3>
- photo editor는 사진을 편집하는 프로그램으로써 사용자들이 주로 사용하는 총 15가지의 기능을 제공한다.
<h3>2. 프로그램 기능</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719064-d3941e74-72b5-483e-94a3-f798c468816c.png" />
<hr></hr>

# 핵심 코드
<h3>1. Rotate</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719199-498071c1-7327-47c9-b307-1ddb18d44133.png" />

- getRotationMartrix2D()를 이용하여 좌표를 설정한 후 트랙바의 값에 따라 회전하는 각도가 정해진다.<br>
wrapAffine()을 통해 어파인 변환을 수행한 이미지를 출력한다.

<h3>2. Warping</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719215-3acbebb8-2139-4a63-8108-822ebeae3598.png" />

- x'=x+ratio*(pt2.x-pt1.y), y'=y+ratio*(pt2.y-pt1.y) 다음 두 수식을 통해 목적영상을 구성한다. <br>
가로, 세로 드래그를 모두 구현하기 위해 x, y 수식을 모두 사용하였다.

<h3>3. Blur</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719260-d62aa9e8-997d-48cd-8e92-eb124d512b88.png" />

- GaussianBlur()에서 kernel의 값은 홀수만 가능하기 때문에 홀수처리를 해주었고, hair의 경우는 앞머리까지의 영역을 처리하기 위함이다.

<h3>4. 마스크 필터</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719307-5e93db94-77c5-4d73-897b-a52c20794519.png" />

- dlib라이브러리의 landmark를 사용하여 얼굴의 좌표를 모두 구해온다. (그림 참조)

<img src="https://user-images.githubusercontent.com/73030613/144719322-fd5ef11b-545a-441e-ac90-7e58631e010d.png" />

- 이미지 얼굴의 크기에 마스크 크기를 맞추기 위해 마스크의 사이즈를 조정해준다. 마스크이미지를
threshold를 통해 mask처리를 해준다[1]. 이미지에서 마스크를 쓸 부분에 bitwise연산자를 통해 mask처리
된 마스크이미지를 합성하고[2] 마스크이미지를 더해준다.

<h3>5. 입술 색 변경</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719352-1b1bc4bb-6295-4106-8d81-73a699c73b9f.png" />

- 입술 영역을 추출하는 함수이다. (4) 마스크 필터와 마찬가지로 landmark를 이용하여 입술영역을 지정
해주어 다각형을 그려준 후 bitwise를 이용하여 입술 영역을 추출한다. 

<img src="https://user-images.githubusercontent.com/73030613/144719370-cc561674-eb8d-4598-a135-27d26144361a.png" />

- 저장된 얼굴좌표중 [48:61] 입술영역을 그려준다.

<img src="https://user-images.githubusercontent.com/73030613/144719385-5ce63aec-484d-422b-96f9-a9c3d01786a4.png" />

- 추출한 입술영역은 b, g, r의 값이 적용되며 이미지와 합치게 된다. 

<h3>6. 코 이미지</h3>
<img src="https://user-images.githubusercontent.com/73030613/144719398-9f5e59a0-02de-46b7-8c6a-87f97664838e.png" />

- (4) 마스크 필터와 동일하며 (4) 마스크 필터는 하관부분을 추출했다면 이번 필터는 landmark에서 코
의 영역만 추출한다.

# 시연 스크린샷
<img src="https://user-images.githubusercontent.com/73030613/144719455-9eb0fced-f500-4baf-8690-139fdb6a1bc3.png" />
