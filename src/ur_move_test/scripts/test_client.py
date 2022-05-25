from sys import path

import numpy as np
import zmq
from math import *

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:22501')

socket.send_json({
    'joints': [0, -pi/2, pi/2, -pi/2, -pi/2, 0]
})
print(socket.recv_json())
