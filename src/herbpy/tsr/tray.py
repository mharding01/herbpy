import numpy
from prpy.tsr.tsrlibrary import TSRFactory
from prpy.tsr.tsr import TSR, TSRChain

@TSRFactory('herb', 'wicker_tray', 'point_on')
def point_on(robot, tray, manip=None, padding=0.0):
    '''
    This creates a TSR that allows you to sample poses on the tray.
    The samples from this TSR should be used to find points for object placement.
    They are directly on the tray, and thus not suitable as an end-effector pose.
    Grasp specific calculations are necessary to find a suitable end-effector pose.

    @param robot The robot performing the grasp
    @param tray The tray to sample poses on
    @param manip The manipulator to perform the grasp, if None
       the active manipulator on the robot is used
    @param padding The amount of space around the edge to exclude from sampling
       If using this to place an object, this would be the maximum radius of the object
    '''
    if manip is None:
        manip_idx = robot.GetActiveManipulatorIndex()
    else:
        with manip.GetRobot():
            manip.SetActive()
            manip_idx = manip.GetRobot().GetActiveManipulatorIndex()
            
    T0_w = tray.GetTransform()

    # The frame is set on the ta such that the y-axis is normal to the table surface
    Tw_e = numpy.eye(4)
    Tw_e[2,3] = 0.04 # set the object on top of the tray

    Bw = numpy.zeros((6,2))

    # TODO - replace this with hard coded extents that make sense, this won't work
    #  right if the tray isn't axis-aligned
    xdim = 0.235 - 2.*padding #tray_extents[0] - 2.*padding
    ydim = 0.33 - 2.*padding #tray_extents[1] - 2.*padding
    Bw[0,:] = [-xdim, xdim ] # move along x and z directios to get any point on tray
    Bw[1,:] = [-ydim, ydim]
    Bw[2,:] = [-0.02, 0.04] # verticle movement
    Bw[5,:] = [-numpy.pi, numpy.pi] # allow any rotation around z - which is the axis normal to the tray top

    
    tray_top_tsr = TSR(T0_w = T0_w, Tw_e = Tw_e, Bw = Bw, manip = manip_idx)
    tray_top_chain = TSRChain(sample_start = False, sample_goal = True, constrain=False, 
                               TSR = tray_top_tsr)
    return [tray_top_chain]


@TSRFactory('herb', 'wicker_tray', 'handle_grasp')
def handle_grasp(robot, tray, manip=None, handle=None):
    '''
    This creates a TSR for grasping the left handle of the tray
    By default, the handle is grasped with the left hand, unless manip is specified

    @param robot The robot performing the grasp
    @param tray The tray to grasp
    @param manip The manipulator to perform the grasp, if None
      the active manipulator on the robot is used
    '''
    if manip is None:
        manip_idx = robot.GetActiveManipulatorIndex()
    else:
        with manip.GetRobot():
            manip.SetActive()
            manip_idx = manip.GetRobot().GetActiveManipulatorIndex()
            
    tray_in_world = tray.GetTransform()

    # Compute the pose of both handles in the tray
    handle_one_in_tray = numpy.eye(4)
    handle_one_in_tray[1,3] = -0.33
    
    handle_two_in_tray = numpy.eye(4)
    handle_two_in_tray[1,3] = 0.33

    handle_poses = [handle_one_in_tray, handle_two_in_tray]

    # Define the grasp relative to a particular handle
    grasp_in_handle = numpy.array([[0.,  1.,  0., 0.],
                                   [1.,  0.,  0., 0.],
                                   [0.,  0., -1., 0.33],
                                   [0.,  0.,  0., 1.]])

    Bw = numpy.zeros((6,2))
    epsilon = 0.03
    Bw[0,:] = [0., epsilon] # Move laterally along handle
    Bw[2,:] = [-0.01, 0.01] # Move up or down a little bit
    Bw[5,:] = [-5.*numpy.pi/180., 5.*numpy.pi/180.] # Allow 5 degrees of yaw

    # Now build tsrs for both
    chains = []
    best_dist = float('inf')
    for handle_in_tray in handle_poses:
        dist = numpy.linalg.norm(handle_in_tray[:2,3] - manip.GetEndEffectorTransform()[:2,3])
        if handle == 'closest' and dist > best_dist:
            continue
        handle_in_world = numpy.dot(tray_in_world, handle_in_tray)
        tray_grasp_tsr = TSR(T0_w = handle_in_world, 
                             Tw_e = grasp_in_handle, 
                             Bw = Bw, 
                             manip=manip_idx)
        tray_grasp_chain = TSRChain(sample_start = False, 
                                    sample_goal = True, 
                                    constrain=False,
                                    TSR = tray_grasp_tsr)
        if handle == 'closest':
            chains = []
        chains.append(tray_grasp_chain)
    return chains

@TSRFactory('herb', 'wicker_tray', 'lift')
def lift(robot, tray, distance=0.1):
    '''
    This creates a TSR for lifting the tray a specified distance with both arms
    It is assumed that when called, the robot is grasping the tray with both arms

    @param robot The robot to perform the lift
    @param tray The tray to lift
    @param distance The distance to lift the tray
    '''
    print 'distance = %0.2f' % distance

    with robot:
        robot.left_arm.SetActive()
        left_manip_idx = robot.GetActiveManipulatorIndex()

        robot.right_arm.SetActive()
        right_manip_idx = robot.GetActiveManipulatorIndex()


    tray_in_world = tray.GetTransform()
    left_in_world = robot.left_arm.GetEndEffectorTransform()
    right_in_world = robot.right_arm.GetEndEffectorTransform()
    
    # First create a goal for the right arm that is 
    #  the desired distance above the current tray pose
    right_in_tray = numpy.dot(numpy.linalg.inv(tray_in_world),
                              right_in_world)
    left_in_tray = numpy.dot(numpy.linalg.inv(tray_in_world),
                             left_in_world)
    desired_tray_in_world = tray.GetTransform()
    desired_tray_in_world[2,3] += distance

    tsr_right_goal = TSR(T0_w = desired_tray_in_world,
                     Tw_e = right_in_tray,
                     Bw = numpy.zeros((6,2)), 
                     manip=right_manip_idx)
    goal_right_chain = TSRChain(sample_start = False, sample_goal = True, constrain=False,
                          TSRs = [tsr_right_goal])

    tsr_left_goal = TSR(T0_w = desired_tray_in_world,
                     Tw_e = left_in_tray,
                     Bw = numpy.zeros((6,2)), 
                     manip=left_manip_idx)
    goal_left_chain = TSRChain(sample_start = False, sample_goal = True, constrain=False,
                          TSRs = [tsr_left_goal])

    # Create a constrained chain for the left arm that keeps it
    #  in the appropriate pose relative to the right arm
    left_in_right = numpy.dot(numpy.linalg.inv(right_in_world),
                              left_in_world)
                                               
    Bw = numpy.zeros((6,2))
    tsr_0 = TSR(T0_w = numpy.eye(4),
                Tw_e = left_in_right,
                Bw = Bw,
                manip=left_manip_idx,
                bodyandlink='%s %s' % (robot.GetName(), robot.right_arm.GetEndEffector().GetName()))
    movement_chain = TSRChain(sample_start = False, sample_goal = False, constrain=True,
                              TSRs = [tsr_0])
    
    return [movement_chain, goal_right_chain, goal_left_chain ]
