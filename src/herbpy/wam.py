import cbirrt, chomp, logging, openravepy
from planner import PlanningError 
from methodlist_decorator import CreateMethodListDecorator

WamMethod = CreateMethodListDecorator()

@WamMethod
def SetStiffness(manipulator, stiffness):
    try:
        manipulator.arm_controller.SendCommand('SetStiffness {0:f}'.format(stiffness))
        return True
    except openravepy.openrave_exception, e:
        logging.error(e)
        return False

@WamMethod
def MoveHand(manipulator, f1=None, f2=None, f3=None, spread=None, timeout=None):
    # Default any None's to the current DOF values.
    hand_indices = sorted(manipulator.GetChildDOFIndices())
    preshape = manipulator.parent.GetDOFValues(hand_indices)

    if f1     is not None: preshape[0] = f1
    if f2     is not None: preshape[1] = f2
    if f3     is not None: preshape[2] = f3
    if spread is not None: preshape[3] = spread

    manipulator.hand_controller.SetDesired(preshape)
    if timeout == None:
        manipulator.parent.WaitForController(0)
    elif timeout > 0:
        manipulator.parent.WaitForController(timeout)
    return True

@WamMethod
def GetForceTorque(manipulator):
    sensor_data = manipulator.ft_sensor.GetSensorData()
    return sensor_data.force, sensor_data.torque

@WamMethod
def TareForceTorqueSensor(manipulator):
    manipulator.ft_sensor.SendCommand('Tare')

@WamMethod
def SetVelocityLimits(manipulator, velocity_limits, min_accel_time):
    num_dofs = len(manipulator.GetArmIndices())
    if len(velocity_limits) != num_dofs:
        logging.error('Incorrect number of velocity limits; expected {0:d}, got {1:d}.'.format(
                      num_dofs, len(velocity_limits)))
        return False

    args  = [ 'SetSpeed' ]
    args += [ str(min_accel_time) ]
    args += [ str(velocity) for velocity in velocity_limits ]
    args_str = ' '.join(args)
    manipulator.arm_controller.SendCommand(args_str)
    return True