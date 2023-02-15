from scipy.spatial import distance as dist
from imutils.video import VideoStream, FPS
from imutils import face_utils
import imutils
import numpy as np
import time
import dlib
import cv2

# Facial landmark detector - api implemented in dlib (68 x-y-coordinates)
# 1-17 face
# 18-22 left eyebrow
# 23-27 right eyebrow
# 28-26 nose
# 37-42 left eye
# 43-48 right eye
# 49-68 mouth

def smile(mouth):
    A = dist.euclidean(mouth[3], mouth[9])
    B = dist.euclidean(mouth[2], mouth[10])
    C = dist.euclidean(mouth[4], mouth[8])
    D = dist.euclidean(mouth[0], mouth[6])

    avg = (A+B+C)/3
    mar = avg/D
    return mar

COUNTER = 0
TOTAL = 0

shape_predictor = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)


(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]


print("Starting live video")
vs = VideoStream(src=0).start()
fileStream = False
time.sleep(1.0)

fps = FPS().start()
cv2.namedWindow("test")

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        mouth = shape[mStart:mEnd]
        mar = smile(mouth)
        mouthHull = cv2.convexHull(mouth)

        cv2.drawContours(frame, [mouthHull], -1, (0,255,0), 1)

        if mar <= 0.3 or mar > 0.38:
            COUNTER+=1
        else:
            if COUNTER >= 15:
                TOTAL+=1
                frame = vs.read()
                time.sleep(0.3)
                frame2 = frame.copy()
                img_name = f"opencv_frame_{TOTAL}"
                print(f"{img_name} written!")
            COUNTER=0

        cv2.putText(frame, f"MAR: {mar}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    fps.update()

    key2 = cv2.waitKey(1) & 0xFF
    if key2 == ord('q'):
        break
fps.stop()

cv2.destroyAllWindows()
vs.stop()