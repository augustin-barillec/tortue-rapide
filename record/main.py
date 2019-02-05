import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def main():
    return render_template('index.html')


@socketio.on('record')
def record():
    print('lala')

    # camera = cv2.VideoCapture(0)
    # i = 0
    # while i < 10:
    #     return_value, image = camera.read()
    #     cv2.imwrite('pics/opencv' + str(i) + '.png', image)
    #     i += 1
    # camera.release()


if __name__ == '__main__':
    socketio.run(app)
