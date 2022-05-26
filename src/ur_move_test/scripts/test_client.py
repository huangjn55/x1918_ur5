from sys import path

import numpy as np
import zmq
from math import *

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:22501')

# 三种控制模式，“Pose"获取当前robot姿态，“Joint”直接控制关节，“End”控制末端末端位置
socket.send_json({
    'mode': "Joint",
    'data': [0, -pi/2, pi/2, -pi/2, -pi/2, 0]
})


print(socket.recv_json())
