import numpy
from prpy.tsr.tsrlibrary import TSRFactory
from prpy.tsr.tsr import TSR, TSRChain

@TSRFactory('herb', 'fuze_bottle', 'lift')
def fuze_lift(robot, bottle, manip=None, distance=0.1):
    """
    This creates a TSR for lifting the bottle a specified distance. 
    It is assumed that when called, the robot is grasping the bottle

    @param robot The robot to perform the lift
    @param bottle The bottle to lift
    @param manip The manipulator to lift 
    @param distance The distance to lift the bottle
    """
    print 'distance = %0.2f' % distance

    if manip is None:
        manip = robot.GetActiveManipulator()
        manip_idx = robot.GetActiveManipulatorIndex()
    else:
         with manip.GetRobot():
             manip.SetActive()
             manip_idx = manip.GetRobot().GetActiveManipulatorIndex()

    #TSR for the goal
    start_position = manip.GetEndEffectorTransform()
    end_position = manip.GetEndEffectorTransform()
    end_position[2, 3] += distance

    Bw = numpy.zeros((6, 2))
    epsilon = 0.05
    Bw[0,:] = [-epsilon, epsilon]
    Bw[1,:] = [-epsilon, epsilon]
    Bw[4,:] = [-epsilon, epsilon]

    tsr_goal = TSR(T0_w = end_position, Tw_e = numpy.eye(4),
            Bw = Bw, manip = manip_idx)

    goal_tsr_chain = TSRChain(sample_start = False, sample_goal = True, 
            constrain = False, TSRs = [tsr_goal])

    #TSR that constrains the movement
    Bw_constrain = numpy.zeros((6, 2))
    Bw_constrain[:, 0] = -epsilon
    Bw_constrain[:, 1] = epsilon
    if distance < 0:
        Bw_constrain[1,:] = [-epsilon+distance, epsilon]
    else:
        Bw_constrain[1,:] = [-epsilon, epsilon+distance]

    tsr_constraint = TSR(T0_w = start_position, Tw_e = numpy.eye(4),
            Bw = Bw_constrain, manip = manip_idx)

    movement_chain = TSRChain(sample_start = False, sample_goal = False, 
            constrain = True, TSRs = [tsr_constraint])

    return [goal_tsr_chain, movement_chain] 

@TSRFactory('herb', 'fuze_bottle', 'grasp')
def fuze_grasp(robot, fuze, manip=None):
    """
    @param robot The robot performing the grasp
    @param fuze The fuze to grasp
    @param manip The manipulator to perform the grasp, if None
       the active manipulator on the robot is used
    """
    return _fuze_grasp(robot, fuze, manip = manip)

@TSRFactory('herb', 'fuze_bottle', 'push_grasp')
def fuze_grasp(robot, fuze, push_distance = 0.1, manip=None):
    """
    @param robot The robot performing the grasp
    @param fuze The fuze to grasp
    @param push_distance The distance to push before grasping
    @param manip The manipulator to perform the grasp, if None
       the active manipulator on the robot is used
    """
    return _fuze_grasp(robot, fuze, push_distance = push_distance, manip = manip)

def _fuze_grasp(robot, fuze, push_distance = 0.0, manip = None):
    """
    @param robot The robot performing the grasp
    @param fuze The fuze to grasp
    @param push_distance The distance to push before grasping
    @param manip The manipulator to perform the grasp, if None
       the active manipulator on the robot is used
    """
    if manip is None:
        manip_idx = robot.GetActiveManipulatorIndex()
    else:
        with manip.GetRobot():
            manip.SetActive()
            manip_idx = manip.GetRobot().GetActiveManipulatorIndex()

    T0_w = fuze.GetTransform()
    ee_to_palm_distance = 0.18
    default_offset_distance = 0.05 # This is the radius of the fuze
                                   # plus a little bit
    total_offset = ee_to_palm_distance + default_offset_distance + push_distance
    Tw_e = numpy.array([[ 0., 0., 1., -total_offset], 
                        [1., 0., 0., 0.], 
                        [0., 1., 0., 0.108], # half of fuze bottle height
                        [0., 0., 0., 1.]])

    Bw = numpy.zeros((6,2))
    Bw[2,:] = [0.0, 0.02]  # Allow a little vertical movement
    Bw[5,:] = [-numpy.pi, numpy.pi]  # Allow any orientation
    
    grasp_tsr = TSR(T0_w = T0_w, Tw_e = Tw_e, Bw = Bw, manip = manip_idx)
    grasp_chain = TSRChain(sample_start=False, sample_goal = True, constrain=False, TSR = grasp_tsr)

    return [grasp_chain]

