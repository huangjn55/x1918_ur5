#!/usr/bin/env python
# use moveit_commander (the Python MoveIt user interfaces )
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import math
from math import pi
import json
import zmq


class MoveGroupInteface(object):
    def __init__(self):
        super(MoveGroupInteface, self).__init__()
        # setup
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('ur_move_test_node', anonymous=True)
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()  # Not used in this tutorial
        group_name = "manipulator"  # group_name can be find in ur5_moveit_config/config/ur5.srdf
        self.move_group_commander = moveit_commander.MoveGroupCommander(group_name)
        self.display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',
                                                            moveit_msgs.msg.DisplayTrajectory, queue_size=20)

        # Getting Basic Information
        self.planning_frame = self.move_group_commander.get_planning_frame()
        print "============ Planning frame: %s" % self.planning_frame
        self.eef_link = self.move_group_commander.get_end_effector_link()
        print "============ End effector link: %s" % self.eef_link
        self.group_names = self.robot.get_group_names()
        print "============ Available Planning Groups:", self.robot.get_group_names()
        print "============ Printing robot state:"
        print self.robot.get_current_state()
        print ""

    def plan_cartesian_path(self, end_pose, scale=1):
        # waypoint_init = []
        target_pose = geometry_msgs.msg.Pose()
        target_pose.position.x = end_pose['pos'][0]
        target_pose.position.y = end_pose['pos'][1]
        target_pose.position.z = end_pose['pos'][2]
        target_pose.orientation.w = end_pose['ori'][0]
        target_pose.orientation.x = end_pose['ori'][1]
        target_pose.orientation.y = end_pose['ori'][2]
        target_pose.orientation.z = end_pose['ori'][3]
        # waypoint_init.append(copy.deepcopy(target_pose))

        (plan, fraction) = self.move_group_commander.compute_cartesian_path(
            [target_pose],  # waypoints to follow
            0.01,  # eef_step
            0.0)  # jump_threshold
        # Note: We are just planning, not asking move_group to actually move the robot yet:
        print "=========== Planning completed, Start execution============="
        self.move_group_commander.execute(plan, wait=True)

    def set_joint_value(self, joints):
        joint_value = self.move_group_commander.get_joint_value_target()
        print 'the joint value of initial state ', joint_value
        point_value = self.move_group_commander.get_current_pose()
        print 'the position value of initial state ', point_value
        self.move_group_commander.set_joint_value_target(joints)
        plan_joint = self.move_group_commander.plan()
        self.move_group_commander.execute(plan_joint, wait=True)


# def info_raw(req):
#     req = json.loads(req.decode('utf-8'))
#     try:
#         resp = motion_planning(req)
#         resp['success'] = True
#     except Exception as e:
#         resp = {'success': False, 'error': str(e)}
#     return json.dumps(resp).encode('utf-8')


# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind('tcp://*:22501')

# print('Waiting for requests...')
# while True:
#     raw_req = socket.recv()
#     print(raw_req)
#     raw_resp = info_raw(raw_req)
#     socket.send(raw_resp)


class ExternalApi:
    def __init__(self, net='tcp://*:22501'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(net)

        self.robot_move = MoveGroupInteface()

    def recv_resp(self):
        req = self.socket.recv()
        req = json.loads(req.decode('utf-8'))

        print self.robot_move.move_group_commander.get_current_pose().pose
        try:
            resp = self.motion_planning(req)
        except Exception as e:
            resp = {'success': False, 'error': str(e)}

        return json.dumps(resp).encode('utf-8')

    def motion_planning(self, req):
        resp = {}
        if req['mode'] == "Pose":
            cur_pose = self.robot_move.move_group_commander.get_current_pose().pose
            resp['data'] = {'pos': [cur_pose.position.x, cur_pose.position.y, cur_pose.position.z],
                            'ori': [cur_pose.orientation.w, cur_pose.orientation.x,
                                    cur_pose.orientation.y, cur_pose.orientation.z]}
        elif req['mode'] == "Joint":
            self.robot_move.set_joint_value(req['data'])
            resp['J_success'] = True
        elif req['mode'] == "End":
            self.robot_move.plan_cartesian_path(req['data'])
            resp['E_success'] = True

        return resp


if __name__ == '__main__':
    robot_move = MoveGroupInteface()
    ser = ExternalApi()
    req = {}
    # req['mode'] = 'End'
    # req['data'] = {'pos': [0.379260105581, 0.180132452938, 0.423940547116],
    #                'ori': [-0.0182792096446, 0.705899930593, 0.0169701332457, 0.70787228584]}
    # ser.motion_planning(req)
    while True:
        raw_resp = ser.recv_resp()
        ser.socket.send(raw_resp)


