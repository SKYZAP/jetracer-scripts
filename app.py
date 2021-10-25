import json
import asyncio
import websockets
import numpy as np
from flask import Flask, render_template, Response
import cv2
from threading import Thread
import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
import PIL.Image
# These modules are available on jetracer by default
from jetracer.nvidia_racecar import NvidiaRacecar
from torch2trt import TRTModule

app = Flask(__name__)

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()


def preprocess(image):
    device = torch.device('cuda')
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]


model_trt = TRTModule()
model_trt.load_state_dict(torch.load('models/road_following_model_trt.pth'))

car = NvidiaRacecar()
STEERING_GAIN = 2
STEERING_BIAS = 0.00
car.throttle = -0.8

gst_str = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, format=NV12 ! nvvidconv ! video/x-raw, width=224, height=224, format=BGRx ! videoconvert ! appsink"
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.json")

camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


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
    media_url = str(file_list[0]["id"])
    media_date = datetime.now()
    requests.post(
        "https://fyp-dashboard.vercel.app/api/uploadJetracer?type=UPLOAD&date={}&url={}".format(media_date, media_url))
    print({"media_ID": media_url}, {"media_date": media_date.isoformat()})
    print("IMAGE: ", str(index), " UPLOADED")


def gen_frames():
    index = 0
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            # Self Driving Code
            sd_image = preprocess(frame).half()
            sd_output = model_trt(sd_image).detach().cpu().numpy().flatten()
            sd_x = float(sd_output[0])
            car.steering = -(sd_x * STEERING_GAIN + STEERING_BIAS)
            # Google Upload Code
            print("INDEX: ", index)
            if index % 1800 == 0 and index != 0:
                Thread(target=uploadIM, args=(index, frame)).start()
            index += 1
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def startFlaskApp():
    app.run(host='0.0.0.0', ssl_context="adhoc", threaded=True,
            port="5000")


async def wshandler(websocket, path):
    while True:
        data = [{"message": np.random.randint(0, 1000)}]
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)


def startWSServer(loop, server):
    loop.run_until_complete(server)
    loop.run_forever()


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    start_server = websockets.serve(wshandler, port=5555, loop=new_loop)
    flaskTask = Thread(target=startFlaskApp)
    wsTask = Thread(target=startWSServer, args=(new_loop, start_server))
    wsTask.start()
    flaskTask.start()
    wsTask.join()
    flaskTask.join()
