from aiohttp import web
import aiohttp
import json
import asyncio
import websockets
import numpy as np
from flask import Flask, render_template, Response, Blueprint
from flask_sockets import Sockets
import cv2
import multiprocessing

app = Flask(__name__)

gst_str = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12 ! nvvidconv ! video/x-raw, width=(int)1280, height=(int)720, format=(string)BGRx ! videoconvert ! appsink"

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
    app.run(host='0.0.0.0', ssl_context='adhoc', threaded=True,
            port="5000")


async def wshandler(websocket, path):
    while True:
        data = [{"message": np.random.randint(0, 1000)}]
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)


def startWSServer():
    start_server = websockets.serve(wshandler, port=5555)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    flaskServ = multiprocessing.Process(target=startFlaskApp)
    asyncioServ = multiprocessing.Process(target=startWSServer)
    flaskServ.start()
    asyncioServ.start()
    flaskServ.join()
    asyncioServ.join()
