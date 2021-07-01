# Driver


<p align="center">
 <img src="./assets/Driver.gif" height="300" width="300">
</p>


in this project we implemented the basic infrastructure for the world cleaner robot. 
This robot can drive with given speed and rotate in different angles.  The driving operations are implemented using basic control that is needed for more accurate angle rotation.

- [Driver](#driver)
  * [Further Work](#further-work)


The driver modules gets a string of driving instructions which he can parse. those instructions are coming from the instructions list in the sql db
this way we can control the driving while creating the base for future module to send the instructions itself.
Driver uses 4 motors that gets command from sabertooth controller 2x12 which gets commands from the nvidia TX2.

## Further Work
Improve and optimize the driving control system so that driving distance can be more accurate and also rotation angle.
This can be done using also Computer vision based algorithms or with better old fashion control
