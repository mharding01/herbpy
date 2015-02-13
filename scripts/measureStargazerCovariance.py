
# Make sure stargazer covariance is set to 0 before doing this

import herbpy
env, robot = herbpy.initialize(sim=False, attach_viewer='rviz')

import time
import math

ts = []
for _ in xrange(50):
    ts.append(robot.GetTransform())
    time.sleep(.1)

xys = [ t[:2,3] for t in ts ]
thetas = [ math.atan2(t[1,0], t[0,0]) for t in ts ]

xyt = [ (x,y,t) for (x,y),t in zip(xys, thetas) ]

xavg = sum([ x for (x,y,t) in xyt ])/len(xyt)
yavg = sum([ y for (x,y,t) in xyt ])/len(xyt)
tavg = sum([ t for (x,y,t) in xyt ])/len(xyt)

xvar = sum([ (x-xavg)**2 for (x,y,t) in xyt ])/len(xyt)
yvar = sum([ (y-yavg)**2 for (x,y,t) in xyt ])/len(xyt)
tvar = sum([ (t-tavg)**2 for (x,y,t) in xyt ])/len(xyt)

#TODO add covariance, right now we're just doing variance

print 'xvar, yvar, tvar'
print xvar, yvar, tvar

import IPython; IPython.embed()
