import cv2

from threading import Thread


def capCamera():

    camera = cv2.VideoCapture(0)
    index = 0
    while(camera.isOpened()):
        success, frame = camera.read()

        cv2.imshow("FRAME", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        index += 1
    # if index == 5:
    #     break


capCamera()

# LOOK INTO https://stackoverflow.com/questions/46649263/how-to-not-wait-for-function-to-finish-python/46649342
