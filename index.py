import cv2
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from threading import Thread

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
camera = cv2.VideoCapture(0)


def uploadIM(index, frame):
    drive = GoogleDrive(gauth)
    fileName = "im.jpg"
    cv2.imwrite("images/"+fileName, frame)
    imageFile = drive.CreateFile(
        {'parents': [{'id': '1H6W8hv3ZYG-08yaiqX2sMllcAsGH00yf'}],
         'title': fileName,
         'mimeType': 'image/jpeg'})
    imageFile.SetContentFile("images/"+fileName)
    imageFile.Upload()
    print("IMAGE: ", str(index), " UPLOADED")


def capCamera():
    index = 0
    while(camera.isOpened()):
        success, frame = camera.read()
        if index % 120 == 0:
            Thread(target=uploadIM, args=(index, frame)).start()
        cv2.imshow("FRAME", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        index += 1
    # if index == 5:
    #     break


capCamera()

# LOOK INTO https://stackoverflow.com/questions/46649263/how-to-not-wait-for-function-to-finish-python/46649342
