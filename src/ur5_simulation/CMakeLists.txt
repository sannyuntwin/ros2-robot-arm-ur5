cmake_minimum_required(VERSION 3.8)
project(ur5_simulation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/move_ur5.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME move_ur5
)

install(PROGRAMS
  scripts/pick_place.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME pick_place
)

install(PROGRAMS
  scripts/spawn_box.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME spawn_box
)

ament_package()
