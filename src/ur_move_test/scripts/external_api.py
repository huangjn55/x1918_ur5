#!/usr/bin/env python
# use moveit_commander (the Python MoveIt user interfaces )
import sys
import copy
<<<<<<< HEAD
=======
import traceback

>>>>>>> spencer
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
<<<<<<< HEAD
=======
from scipy.interpolate import CubicSpline
>>>>>>> spencer

import math
from math import pi
import json
import zmq


class MoveGroupInteface(object):
<<<<<<< HEAD
    def __init__(self):
=======
    def __init__(self, waypoints=None, ts=None):
>>>>>>> spencer
        super(MoveGroupInteface, self).__init__()
        # setup
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('ur_move_test_node', anonymous=True)
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()  # Not used in this tutorial

        group_name = "manipulator"  # group_name can be find in ur5_moveit_config/config/ur5.srdf
        self.move_group_commander = moveit_commander.MoveGroupCommander(group_name)
        self.move_group_commander.set_max_velocity_scaling_factor(0.1)
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

<<<<<<< HEAD
=======
        if waypoints is not None:
            self.waypoints = waypoints
        if ts is not None:
            self.ts = ts

>>>>>>> spencer
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

        # (plan, fraction) = self.move_group_commander.compute_cartesian_path(
        #     [target_pose],  # waypoints to follow
        #     0.01,  # eef_step
        #     0.0)  # jump_threshold
        # # Note: We are just planning, not asking move_group to actually move the robot yet:
        # print "=========== Planning completed, Start execution============="
        # self.move_group_commander.execute(plan, wait=True)
        self.move_group_commander.set_pose_target(target_pose)
        self.move_group_commander.plan()
        self.move_group_commander.go()

<<<<<<< HEAD
    def set_joint_value(self, joints):
        joint_value = self.move_group_commander.get_joint_value_target()
        print 'the joint value of initial state ', joint_value
        point_value = self.move_group_commander.get_current_pose()
        print 'the position value of initial state ', point_value
        self.move_group_commander.set_joint_value_target(joints)
        plan_joint = self.move_group_commander.plan()
        self.move_group_commander.execute(plan_joint, wait=True)

=======
    def set_joint_value(self, joints, msg_type):

        self.move_group_commander.set_joint_value_target(joints)
        plan_joint = self.move_group_commander.plan()
        if msg_type == 'motionPlanning':
            # print "===== plan before"
            # print plan_joint
            plan_joint = self.modify_plan(plan_joint)
            # print "===== plan after"
            # print plan_joint
        self.move_group_commander.execute(plan_joint, wait=True)

    def modify_plan(self, plan):
        # the number of points could be different between resample and plan from moveit commander
        l1 = len(self.ts)
        l2 = len(plan.joint_trajectory.points)
        data = [0, 0, 0, 0, 0, 0]
        if l1 >= l2:
            i = 0
            for point in plan.joint_trajectory.points:
                point.positions = self.waypoints[i]
                point.velocities = data
                point.accelerations = data
                point.time_from_start.secs = int(self.ts[i] // 1)
                point.time_from_start.nsecs = int(self.ts[i] % 1 * 10 ** 9)
                i += 1

            for j in range(i, l1):
                plan.joint_trajectory.points.append(plan.joint_trajectory.points[-1])
                plan.joint_trajectory.points[-1].positions = self.waypoints[j]
                plan.joint_trajectory.points[-1].velocities = data
                plan.joint_trajectory.points[-1].accelerations = data
                plan.joint_trajectory.points[-1].time_from_start.secs = int(self.ts[j] // 1)
                plan.joint_trajectory.points[-1].time_from_start.nsecs = int(self.ts[j] % 1 * 10 ** 9)
        else:
            for k in range(l1):
                plan.joint_trajectory.points[k].positions = self.waypoints[k]
                plan.joint_trajectory.points[k].velocities = data
                plan.joint_trajectory.points[k].accelerations = data
                plan.joint_trajectory.points[k].time_from_start.secs = int(self.ts[k] // 1)
                plan.joint_trajectory.points[k].time_from_start.nsecs = int(self.ts[k] % 1 * 10 ** 9)

            plan.joint_trajectory.points = plan.joint_trajectory.points[: l1]

        return plan
>>>>>>> spencer

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
<<<<<<< HEAD

=======
>>>>>>> spencer
        self.robot_move = MoveGroupInteface()
        # moveit_commander.set

    def set_move_velocity_scaling(self, vel):
        self.robot_move.move_group_commander.set_max_velocity_scaling_factor(vel)

    def recv_resp(self):
        req = self.socket.recv()
        req = json.loads(req.decode('utf-8'))

        try:
            resp = self.motion_planning(req)
<<<<<<< HEAD
        except Exception as e:
            resp = {'success': False, 'error': str(e)}
=======
        except:
            traceback.print_exc()
            resp = {'success': False}
>>>>>>> spencer

        return json.dumps(resp).encode('utf-8')

    def motion_planning(self, req):
        resp = {}
<<<<<<< HEAD
        if req['mode'] == "Velocity":
            self.set_move_velocity_scaling(req['data'])
            resp['data'] = req['data']
        elif req['mode'] == "Pose":
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
=======
        if req['owner'] == 'huangjn':
            if req['mode'] == "Velocity":
                self.set_move_velocity_scaling(req['data'])
                resp['data'] = req['data']
            elif req['mode'] == "Pose":
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
        elif req['owner'] == 'spencer':
            times = req['ts']
            waypoints = req['waypoints']
            msg_type = req['msg_type']
            if msg_type == 'motionPlanning':
                path, ts = self.resample(waypoints, times)
                motion_handle = MoveGroupInteface(waypoints=path, ts=ts)
            else:
                motion_handle = MoveGroupInteface()

            motion_handle.set_joint_value(waypoints[0], msg_type)
            resp = {'success': True}

        return resp

    def modify_config(self, config):
        cf0 = config[0] + 180 * pi / 180
        cf1 = config[1] - 60 * pi / 180
        cf2 = config[2] - 107 * pi / 180
        cf3 = config[3] - 13 * pi / 180
        cf4 = config[4] + 90 * pi / 180
        cf5 = config[5] - 90 * pi / 180

        return [cf0, cf1, cf2, cf3, cf4, cf5]

    def resample(self, waypoints, ts, interval=0.01):
        ts_new = [0]
        while ts_new[-1] < ts[-1]:
            ts_new.append(ts_new[-1] + interval)

        ts_new[-1] = ts[-1]

        _waypoints = []
        for waypoint in waypoints:
            _waypoints.append(self.modify_config(waypoint))

        print('waypoints[0]: ', _waypoints[0])
        wpts_func = CubicSpline(ts, _waypoints)
        wpts = wpts_func(ts_new)

        return wpts, ts_new


if __name__ == '__main__':
    ser = ExternalApi()
    # req = {}
>>>>>>> spencer
    # req['mode'] = 'End'
    # req['data'] = {'pos': [0.379260105581, 0.180132452938, 0.423940547116],
    #                'ori': [-0.0182792096446, 0.705899930593, 0.0169701332457, 0.70787228584]}
    # ser.motion_planning(req)
    while True:
        raw_resp = ser.recv_resp()
        ser.socket.send(raw_resp)

<<<<<<< HEAD

=======
>>>>>>> spencer
