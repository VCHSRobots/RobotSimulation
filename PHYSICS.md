Process Outline:
  The physics engine will consist of state vector for the robot and its components, the user input, and the physics equations which calculate the effects of the latter on the former.
  Each frame, the total forces applied to each part of the robot will be calculated. The state vector (both velocity and position) will then be modified accordingly.
User Input:
  Motor Current (for each motor)
  Wheel Direction
Parameters:
  Robot weight
  Coefficent of friction (static and dynamic)
  Motor power/torque
  Motor Voltage
  Robot center of gravity
  Wheel Locations (relative to robot cg)
  Wheel radius
  Rpm curves
  Slip ratio curves
  Motor RPM
Assumptions:
  The swerve wheel motors can instantaneously move to a given direction
  Voltage given to robot does not vary
  Software has perfect control over motor currents
  Terrain is flat and has no obstacles
  There is no air resistance
  Gear ratios do not affect driving
Calculating Force Vectors:
  Finding Wheel RPM:
    The rpm output by a motor is derived from the motor's torque and the current given to the motor. In order to solve for RPM with a given power and torque, the equasion Torque*RPM/9.549296 must be derived from the following:
      Watt = Newton*meter/sec
      meter/min = 2π*radius*RPM
      meter/sec = meter/min/60
      meter/sec = 2π*radius*RPM/60
      Torque = Newton*radius
      Newton = Torque/radius
      Newton*meter/sec = (Torque/radius)*(2π*radius*RPM/60)
      Newton*meter/sec = Torque*2π*<s>radius</s>*RPM/60*<s>radius</s>
      Newton*meter/sec = Torque*2π*RPM/60
      Newton*meter/sec = Torque*RPM/9.549296 = Watt
    RPM can then be solved for:
      Watt = Torque*RPM/9.549296
      Torque*RPM = Watt*9.549296
      RPM = Watt*9.549296/Torque
  Finding Forces Applied to Wheels:
    Finding Traction:
      Traction moves the wheels foward by causing them to slip backwards and create a friction force in their foward direction. The effectiveness of traction is determined by the slip ratio, which measures how much the wheel is slipping on the floor as opposed to rolling on the ground. A lower ratio indicates rolling, while a higher ratio indicates more slippage between the ground and wheel
      Slip ratio is defined as follows:
        σ = (ω*R-v^long)/|v^long|
        with ω as wheel angular velocity in rad/sec
             R as wheel radius
             v^long as total robot velocity parallel to the wheel
      There are several different equasions to express slip ratio, but this equasion works for driving in reverse
      After the slip ratio is calculated, a slip ratio to longtitudinal force curve must be referenced to find the foward force on the wheel. This curve scales linear to the load placed on the wheel. For now, wheel load is calculated as follows:
        WL = RW/4
        with RW as robot weight
      And longtitudinal force is calculated as follows:
        F^long = curve(σ)*L
        with curve() as a slip ratio reference table function
             σ as slip ratio
             L as wheel load
      The slip ratio will be effectively infinite when v^long = 0, and will return the maximum slippage allowed by the graph
    Finding Rolling Resistance:
      let RW be the robot weight
      let f^s be the static coefficent of friction
      let f^d be the dynamic coefficent of friction
      The main resistance force in this simulation is friction
    Adressing Wheel Skid:
      let θ^r be the angle the robot is moving
      let m^r be the velocity at which the robot is moving
      let θ^w be the angle at which a given wheel is pointed
  Finding Robot Forces:
    Transforming Wheel Force Vectors onto Frame:
      The force vectors applied to each of the wheels affects the frame in the x, y, and yaw directions. The component of the wheel vector which is parelell with the line between the robot and wheel caster is applied to the robot in the direction of the line. The perpendicular component adds yaw velocity to the robot.
      To calculate how the components of the vector are distributed, the difference in the wheel's force direction and the direction of the line must be computed as follows:
        θ^w = θ^v-θ^l
        with θ^v as the direction of the vector applied to the wheel
             θ^l as the positive direction of the line which connects the caster and center of gravity
      The effects of each of the vectors can then be totaled for every wheel:
        F^f += magnitude^wheel*cos(θ^wheel) in direciton θ^w
        Velocity^yaw += magnitude^wheel*sin(θ^wheel) in direction clockwise if positive or counterclockwise if negitive
    Finding Frame Friction:
      Frame friction can be either static or dynamic, depending on if the robot is moving or not. If the robot is not moving, it must overcome the higher static friction before the dynamic friction will engage.
      The friction force is applied in the opposite to the robot. This is either the robot's direction of travel, or the opposite direction of any force attempting to move the robot.
      The following equasion defines friction
        F^friction = C^friction*RW*G, D^robot-pi
        with C^friction as which ever coefficent of friction is engage
             RW as the Robot Weight in kilograms
             G as gravity in meters per second
             D^robot as which ever direction is registered as the robot direction
Transforming State Vectors:
  Calculating Velocity:
    Calculating Wheel Velocities:
      Wheel velocities are integrated from the rolling forces applied to the wheels. Every update, tey are incremented based on the amount of time passed (ΔT) as follows:
        Velocity^Wheel' = Velocity^Wheel+(ΔT*Force)
      Note that force can be either positive or negative, meaning velocity can increment or decrement depending on force
    Calculating Robot Velocity:
      The Robot x and y velocities are integrated from the components of the vector applied to the frame. Every update, their x and y components are incremented based on the amount of time passed (ΔT) as follows:
        Velocity^x' = Velocity^x+(ΔT*Magnitude*cos(Direction))
        Velocity^y' = Velocity^y+(ΔT*Magnitude*sin(Direction))
        with Magnitude and Direction as the magnitude and direciton of the frame force vector
  Calculating Position:
    Calculating Robot Position:
      Calculating x and y Position:
        The Robot's cartesian position is integrated from the x and y velocities
          Position^x' = Position^x+(ΔT*Velocity^x)
          Position^y' = Position^y+(ΔT*Velocity^y)
      Calculating Roll, Pitch, and Yaw:
        Roll and pitch are currently not factored into the physics calculations, but Yaw is affected by the perpendicular component of the wheel vectors (the part which is not transfered to the frame). It is integrated from the velocity calculated from that time
          Position^yaw' = Position^yaw+(ΔT*Velocity^yaw)
    Calculating Wheel Position:
      Wheel position is integrated from each wheel's velocity as follows:
        Position^wheel' = Position^wheel+(ΔT*Velocity^wheel)
Note - Values to measure:
  Motor torque in newton-meters
  Slip ratio curve
    