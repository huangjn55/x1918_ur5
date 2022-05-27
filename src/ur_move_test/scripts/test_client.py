#!/usr/bin/env python

from sys import path
import numpy as np
import zmq
from math import *

# context = zmq.Context()
# socket = context.socket(zmq.REQ)
# socket.connect('tcp://localhost:22501')

# socket.send_json({
#     'mode': "Pose",
#     'data': [0, -pi/2, pi/2, -pi/2, -pi/2, 0]
# })


# print(socket.recv_json())


class Client2UR:
    def __init__(self, net='tcp://localhost:22501'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(net)

    def set_velocity(self, vel):
        self.socket.send_json({
            'mode': "Velocity",
            'data': vel
        })
        recv = self.socket.recv_json()['data']
        print recv

        return recv

    def get_pose(self):
        self.socket.send_json({
            'mode': "Pose",
            # 'data': []
        })
        recv = self.socket.recv_json()['data']
        print recv

        return recv

    def joint_control(self, joints):
        self.socket.send_json({
            'mode': "Joint",
            'data': joints
        })
        recv = self.socket.recv_json()
        print recv

    def end_control(self, pose):
        self.socket.send_json({
            'mode': "End",
            'data': pose
        })
        recv = self.socket.recv_json()
        print recv


if __name__ == '__main__':
    client = Client2UR()
    pose = client.get_pose()
    client.set_velocity(1)
    pose['pos'][2] = pose['pos'][2] + 0.05
    print pose
    client.end_control(pose)

    # joints = [0, -pi/2, pi/2, -pi/2, -pi/2, 0]
    # client.joint_control(joints)
