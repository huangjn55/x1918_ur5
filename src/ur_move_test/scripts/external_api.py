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

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:22501')


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

    def plan_cartesian_path(self, scale=1):
        waypoints = []
        wpose = self.move_group_commander.get_current_pose().pose
        wpose.position.z -= scale * 0.1  # First move up (z)
        waypoints.append(copy.deepcopy(wpose))
        wpose.position.x += scale * 0.1  # Second move forward/backwards in (x)
        waypoints.append(copy.deepcopy(wpose))
        wpose.position.y += scale * 0.1  # Third move sideways (y)
        waypoints.append(copy.deepcopy(wpose))

        (plan, fraction) = self.move_group_commander.compute_cartesian_path(
            waypoints,  # waypoints to follow
            0.01,  # eef_step
            0.0)  # jump_threshold
        # Note: We are just planning, not asking move_group to actually move the robot yet:
        print "=========== Planning completed, Cartesian path is saved============="
        return plan, fraction

    def set_joint_value(self, joints):

        joint_value = self.move_group_commander.get_joint_value_target()
        print 'the joint value of initial state ', joint_value
        point_value = self.move_group_commander.get_current_pose()
        print 'the position value of initial state ', point_value
        self.move_group_commander.set_joint_value_target(joints)
        plan_joint = self.move_group_commander.plan()
        self.move_group_commander.execute(plan_joint, wait=True)


def motion_planning(req):
    motion_handle = MoveGroupInteface()
    motion_handle.set_joint_value(req['joints'])


def info_raw(req):
    req = json.loads(req.decode('utf-8'))
    try:
        resp = motion_planning(req)
        resp['success'] = True
    except Exception as e:
        resp = {'success': False, 'error': str(e)}
    return json.dumps(resp).encode('utf-8')


print('Waiting for requests...')
while True:
    raw_req = socket.recv()
    print(raw_req)
    raw_resp = info_raw(raw_req)
    socket.send(raw_resp)