#!/usr/bin/env python
"""
Provides a simple console that sets up basic functionality for 
using herbpy and openravepy.
"""

import os
if os.environ.get('ROS_DISTRO', 'hydro')[0] in 'abcdef':
    import roslib
    roslib.load_manifest('herbpy')

# Source: http://stackoverflow.com/a/19227287/111426
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

import argparse, herbpy, logging, numpy, openravepy, sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='utility script for loading HerbPy')
    parser.add_argument('-v', '--viewer', nargs='?', const=True,
                        help='attach a viewer of the specified type')
    parser.add_argument('--robot-xml', type=str,
                        help='robot XML file; defaults to herb_description')
    parser.add_argument('--env-xml', type=str,
                        help='environment XML file; defaults to an empty environment')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug logging')

    group = parser.add_argument_group('Simulation Options')
    group.add_argument('-s', '--sim', action='store_true',
                        help='simulate the entire robot')

    # All of these options default to None. If the option is specified with no
    # arguments, e.g. --left-arm-sim, the option defaults to True. This
    # behavior can be overriden by specifying a value; e.g. --left-arm-sim=1.
    # See: http://stackoverflow.com/a/15301183/111426
    group.add_argument('--left-arm-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the left Barrett WAM arm')
    group.add_argument('--left-hand-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the left BarrettHand hand')
    group.add_argument('--left-ft-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the left 6-axis force/torque sensor')
    group.add_argument('--right-arm-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the right Barrett WAM arm')
    group.add_argument('--right-hand-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the right BarrettHand hand')
    group.add_argument('--right-ft-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the right 6-axis force/torque sensor')
    group.add_argument('--head-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the head pan/tilt unit')
    group.add_argument('--segway-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the Segway RMP base')
    group.add_argument('--vision-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the visual perception system')
    group.add_argument('--talker-sim', type=str2bool, nargs='?', const=True,
                        help='simulate the text-to-speech engine')

    args = parser.parse_args()

    openravepy.misc.InitOpenRAVELogging()

    if args.debug:
        openravepy.RaveSetDebugLevel(openravepy.DebugLevel.Debug)

    herbpy_args = {
        'attach_viewer': args.viewer,
        'robot_xml': args.robot_xml,
        'env_path': args.env_xml,
        # Simulation flags.
        'sim': args.sim,
        'left_arm_sim': args.left_arm_sim,
        'left_hand_sim': args.left_hand_sim,
        'left_ft_sim': args.left_ft_sim,
        'right_arm_sim': args.right_arm_sim,
        'right_hand_sim': args.right_hand_sim,
        'right_ft_sim': args.right_ft_sim,
        'head_sim': args.head_sim,
        'segway_sim': args.segway_sim,
        'vision_sim': args.vision_sim,
        'talker_sim': args.talker_sim,
    }
    
    env, robot = herbpy.initialize(**herbpy_args)

    import IPython
    IPython.embed()
