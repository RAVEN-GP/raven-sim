cmake_minimum_required(VERSION 3.0.2)
project(utils)

find_package(catkin REQUIRED COMPONENTS
  std_msgs
  message_generation
  rospy
  sensor_msgs
  gazebo_msgs
  cv_bridge
)


 add_message_files(
   FILES
   IMU.msg
   localisation.msg
 )

 generate_messages(
   DEPENDENCIES
   std_msgs
 )


catkin_package(
  CATKIN_DEPENDS message_runtime
)

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)


catkin_install_python(PROGRAMS
  scripts/synthetic_capture.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
