import cv2
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from threading import Thread
from datetime import datetime
import requests

gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.json")
camera = cv2.VideoCapture(0)


def uploadIM(index, frame):
    drive = GoogleDrive(gauth)
    fileName = "im.jpg"
    # Write image locally
    cv2.imwrite("images/"+fileName, frame)
    # Create image metadata and upload to drive
    imageFile = drive.CreateFile(
        {'parents': [{'id': '1H6W8hv3ZYG-08yaiqX2sMllcAsGH00yf'}],
         'title': fileName,
         'mimeType': 'image/jpeg'})
    imageFile.SetContentFile("images/"+fileName)
    imageFile.Upload()
    # Find latest image ID
    file_list = drive.ListFile(
        {'q': "mimeType='image/jpeg' and trashed=false"}).GetList()
    print("LATEST: ", file_list[0]["id"])
    media_url = str(file_list[0]["id"])
    media_date = datetime.now()
    requests.post(
        "http://localhost:3000/api/uploadJetracer?type=UPLOAD&date={}&url={}".format(media_date, media_url))
    print({"media": media_url}, {"media_date": media_date.isoformat()})
    for file1 in file_list:
        print('title: %s, id: %s' % (file1['title'], file1['id']))
    print("IMAGE: ", str(index), " UPLOADED")


def capCamera():
    index = 0
    while(camera.isOpened()):
        success, frame = camera.read()
        if index % 1800 == 0 and index != 0:
            Thread(target=uploadIM, args=(index, frame)).start()
        cv2.imshow("FRAME", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        index += 1
    # if index == 5:
    #     break


capCamera()

# LOOK INTO https://stackoverflow.com/questions/46649263/how-to-not-wait-for-function-to-finish-python/46649342
