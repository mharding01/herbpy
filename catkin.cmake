cmake_minimum_required(VERSION 2.8.3)

find_package(catkin REQUIRED)
catkin_package()
catkin_python_setup()

install(DIRECTORY config/
    DESTINATION "${CATKIN_PACKAGE_SHARE_DESTINATION}/config"
)
install(PROGRAMS scripts/console.py
                 scripts/generate_primitives_herb.py
                 scripts/plot_primitives.py
    DESTINATION "${CATKIN_PACKAGE_BIN_DESTINATION}"
)
