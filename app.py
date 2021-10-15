import json
import asyncio
import websockets
import numpy as np
from flask import Flask, render_template, Response, Blueprint
import cv2
from threading import Thread

app = Flask(__name__)

gst_str = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, format=NV12 ! nvvidconv ! video/x-raw, width=224, height=224, format=BGRx ! videoconvert ! appsink"


camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
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


def uploadIM():
    import requests
#     url = 'http://localhost:3000/api/uploadJetracer?'
#     files = {'media': open('bird.jpg', 'rb')}
#     requests.post(url, files=files)
    return "DONE"


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    start_server = websockets.serve(wshandler, port=5555, loop=new_loop)
    flaskTask = Thread(target=startFlaskApp)
    wsTask = Thread(target=startWSServer, args=(new_loop, start_server))
    wsTask.start()
    flaskTask.start()
    wsTask.join()
    flaskTask.join()
