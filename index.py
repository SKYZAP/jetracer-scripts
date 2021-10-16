import cv2
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

camera = cv2.VideoCapture(0)
index = 0

while(camera.isOpened()):
    success, frame = camera.read()

    if index % 120 == 0:
        fileName = "im"+str(index)+".jpg"
        cv2.imwrite("images/"+fileName, frame)
        imageFile = drive.CreateFile(
            {'parents': [{'id': '1H6W8hv3ZYG-08yaiqX2sMllcAsGH00yf'}],
             'title': fileName,
             'mimeType': 'image/jpeg'})
        imageFile.SetContentFile("images/"+fileName)
        imageFile.Upload()
        print("IMAGE UPLOADED")

    cv2.imshow("FRAME", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    index += 1
    # if index == 5:
    #     break


# LOOK INTO https://stackoverflow.com/questions/46649263/how-to-not-wait-for-function-to-finish-python/46649342
