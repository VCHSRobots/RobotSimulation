import time

import primitivePhysics
s = primitivePhysics.Swerve()
s.sendControls(y=1)
time.sleep(1)
s.update()
print(s.position)
s.sendControls(y=-1)
time.sleep(1)
s.update()
print(s.position)
