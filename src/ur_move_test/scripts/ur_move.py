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


class MoveGroupInteface(object):
    def __init__(self, action):
        super(MoveGroupInteface, self).__init__()
        self.action = action
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

    def execute_plan(self, plan):
        # Use execute if you would like the robot to follow
        # the plan that has already been computed:
        self.move_group_commander.execute(plan, wait=True)

    def set_initial_point(self):
        # plan a path to initial point
        waypoint_init = []
        wpose_init = self.move_group_commander.get_current_pose().pose
        wpose_init.orientation.w = -pi
        wpose_init.position.x = 0.5
        wpose_init.position.y = 0
        wpose_init.position.z = 0.2
        wpose_init.orientation.x = 0
        wpose_init.orientation.y = math.sin(pi/4)
        wpose_init.orientation.z = 0
        wpose_init.orientation.w = math.sin(pi/4)
        waypoint_init.append(copy.deepcopy(wpose_init))
        (plan, fraction) = self.move_group_commander.compute_cartesian_path(
            waypoint_init,  # waypoints to follow
            0.01,  # eef_step
            0.0)  # jump_threshold
        self.move_group_commander.execute(plan, wait=True)
        print "initialize successful"
        print "position after initialization", self.move_group_commander.get_current_pose()

    def set_joint_value(self):

        joint_value = self.move_group_commander.get_joint_value_target()
        print 'the joint value of initial state ', joint_value
        point_value = self.move_group_commander.get_current_pose()
        print 'the position value of initial state ', point_value
        joint_value = [0, -pi/2, pi/2, -pi/2, -pi/2, 0]
        self.move_group_commander.set_joint_value_target(joint_value)
        plan_joint = self.move_group_commander.plan()
        self.move_group_commander.execute(plan_joint, wait=True)

    def action_move(self):
        # calculate the start point of action
        start_point_x = self.action[0]
        start_point_y = self.action[1]
        start_point_z = self.action[3]
        action_start_position = self.move_group_commander.get_current_pose().pose
        action_start_position.position.x = start_point_x
        action_start_position.position.y = start_point_y
        action_start_position.position.z = start_point_z

        # execute the way from robot start to action start
        waypoint_robot_to_action = [action_start_position]
        (plan_robot_to_action, fraction) = self.move_group_commander.compute_cartesian_path(
            waypoint_robot_to_action,  # waypoints to follow
            0.01,  # eef_step
            0.0)  # jump_threshold
        self.move_group_commander.execute(plan_robot_to_action, wait=True)

        # spain the effector
        joint_action = self.move_group_commander.get_current_joint_values()
        joint_action[5] = - self.action[2]
        self.move_group_commander.set_joint_value_target(joint_action)
        plan_joint_action = self.move_group_commander.plan()
        self.move_group_commander.execute(plan_joint_action, wait=True)

        # calculate the end point of the action
        action_start_position = self.move_group_commander.get_current_pose().pose
        action_end_position = self.move_group_commander.get_current_pose().pose
        action_end_position.position.x = action_start_position.position.x - self.action[4]*math.cos(self.action[2])
        action_end_position.position.y = action_start_position.position.y - self.action[4]*math.sin(self.action[2])

        # execute the action from start to end

        waypoint_start_to_end = [action_end_position]
        (plan_start_to_end, fraction) = self.move_group_commander.compute_cartesian_path(
            waypoint_start_to_end,  # waypoints to follow
            0.01,  # eef_step
            0.0)  # jump_threshold
        self.move_group_commander.execute(plan_start_to_end, wait=True)
        waypoint_end_to_start = [action_start_position]
        (plan_end_to_start, fraction) = self.move_group_commander.compute_cartesian_path(
            waypoint_end_to_start,  # waypoints to follow
            0.01,  # eef_step
            0.0)  # jump_threshold
        self.move_group_commander.execute(plan_end_to_start, wait=True)


if __name__ == '__main__':
    try:

        print "============ Press `Enter` to begin =========="
        # raw_input()
        tutorial = MoveGroupInteface([0.4, 0.2, -pi/4, 0.2, -0.2])
        print "============ Press `Enter` to initialize the joint =========="
        raw_input()
        tutorial.set_joint_value()
        print tutorial.move_group_commander.get_current_pose()
        print "============ Press `Enter` to the initialize the position =========="
        raw_input()
        tutorial.set_initial_point()
        print "============ Press `Enter` to the execute the action =========="
        raw_input()
        tutorial.action_move()
    except rospy.ROSInterruptException:
        pass
