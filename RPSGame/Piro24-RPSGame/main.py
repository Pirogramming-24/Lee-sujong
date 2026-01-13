import mediapipe as mp
import cv2 as cv
import math, time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from visualization import *
from webcam import *

# 거리 구하는 함수
def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

if __name__ == "__main__":
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1) 
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        detection_result = detector.detect(mp_image)

        current_rps_state = None

        if detection_result.hand_landmarks:
            # 손 가져오기
            hand_landmarks = detection_result.hand_landmarks[0]
            wrist = hand_landmarks[0]
            
            # 검지(8), 중지(12), 약지(16), 소지(20) 체크
            finger_indices = [(8, 6), (12, 10), (16, 14), (20, 18)]
            open_fingers_count = 0
            
            for tip_idx, pip_idx in finger_indices:
                tip = hand_landmarks[tip_idx]
                pip = hand_landmarks[pip_idx]
                
                # TIP이 PIP보다 손목에서 멀면 펴짐
                if get_distance(tip, wrist) > get_distance(pip, wrist):
                    open_fingers_count += 1
            
            # 0: Rock, 1: Paper, 2: Scissors
            
            if open_fingers_count == 0:
                current_rps_state = 0  # Rock (주먹)
            elif open_fingers_count >= 4:
                current_rps_state = 1  # Paper (보)
            elif open_fingers_count == 2:
                current_rps_state = 2  # Scissors (가위)
            else:
                current_rps_state = None # 애매한 경우 출력 안 함

        # 랜드마크 점 그리기
        frame = draw_manual(frame, detection_result)
        
        # 결과 텍스트 출력
        frame = print_RSP_result(frame, current_rps_state)

        # 화면 출력
        cv.imshow('RPS', frame)

        # 'q' 키를 누르면 종료
        if cv.waitKey(1) == ord('q'):
            break
    
    # 종료
    cap.release()
    cv.destroyAllWindows()