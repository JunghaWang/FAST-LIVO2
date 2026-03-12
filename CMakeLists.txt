cmake_minimum_required(VERSION 3.16)
project(fast_livo)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -fexceptions")

if("$ENV{ROS_DISTRO}" STRLESS "iron")
  add_compile_definitions(PRE_ROS_IRON)
endif()

add_compile_definitions(ROOT_DIR="${CMAKE_CURRENT_SOURCE_DIR}/")

include(ProcessorCount)
ProcessorCount(N)
if(N GREATER 4)
  add_compile_definitions(MP_EN MP_PROC_NUM=4)
elseif(N GREATER 1)
  add_compile_definitions(MP_EN MP_PROC_NUM=${N})
else()
  add_compile_definitions(MP_PROC_NUM=1)
endif()

if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm|aarch64|ARM|AARCH64)")
  add_compile_definitions(ARM_ARCH)
else()
  add_compile_definitions(X86_ARCH)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(rcpputils REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread)
find_package(OpenMP QUIET)

set(FAST_LIVO_DEPS
  rclcpp
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  std_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
  cv_bridge
  pcl_conversions
  rcpputils
)

set(FAST_LIVO_INCLUDE_DIRS
  include
  thirdparty/Sophus
  thirdparty/rpg_vikit/vikit_common/include
  ${EIGEN3_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
)

add_definitions(${PCL_DEFINITIONS})

add_library(sophus_vendor STATIC
  thirdparty/Sophus/sophus/so2.cpp
  thirdparty/Sophus/sophus/so3.cpp
  thirdparty/Sophus/sophus/se2.cpp
  thirdparty/Sophus/sophus/se3.cpp
  thirdparty/Sophus/sophus/scso3.cpp
  thirdparty/Sophus/sophus/sim3.cpp
)
target_include_directories(sophus_vendor PUBLIC
  thirdparty/Sophus
  ${EIGEN3_INCLUDE_DIRS}
)

add_library(vikit_common_vendor STATIC
  thirdparty/rpg_vikit/vikit_common/src/atan_camera.cpp
  thirdparty/rpg_vikit/vikit_common/src/omni_camera.cpp
  thirdparty/rpg_vikit/vikit_common/src/math_utils.cpp
  thirdparty/rpg_vikit/vikit_common/src/vision.cpp
  thirdparty/rpg_vikit/vikit_common/src/robust_cost.cpp
  thirdparty/rpg_vikit/vikit_common/src/pinhole_camera.cpp
  thirdparty/rpg_vikit/vikit_common/src/equidistant_camera.cpp
  thirdparty/rpg_vikit/vikit_common/src/polynomial_camera.cpp
)
target_include_directories(vikit_common_vendor PUBLIC
  thirdparty/rpg_vikit/vikit_common/include
  thirdparty/Sophus
  ${EIGEN3_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
)
target_link_libraries(vikit_common_vendor PUBLIC
  sophus_vendor
  ${OpenCV_LIBRARIES}
)

add_library(utils src/utils.cpp)
add_library(vio src/vio.cpp src/frame.cpp src/visual_point.cpp)
add_library(lio src/voxel_map.cpp)
add_library(pre src/preprocess.cpp)
add_library(imu_proc src/IMU_Processing.cpp)
add_library(laser_mapping src/LIVMapper.cpp)

function(configure_fast_livo_target target)
  target_include_directories(${target} PUBLIC ${FAST_LIVO_INCLUDE_DIRS})
  ament_target_dependencies(${target} ${FAST_LIVO_DEPS})
  target_link_libraries(${target} ${PCL_LIBRARIES} ${OpenCV_LIBRARIES})
  if(OpenMP_CXX_FOUND)
    target_link_libraries(${target} OpenMP::OpenMP_CXX)
  endif()
endfunction()

configure_fast_livo_target(utils)
configure_fast_livo_target(vio)
configure_fast_livo_target(lio)
configure_fast_livo_target(pre)
configure_fast_livo_target(imu_proc)
configure_fast_livo_target(laser_mapping)

target_link_libraries(vio vikit_common_vendor sophus_vendor)
target_link_libraries(lio utils)
target_link_libraries(laser_mapping vio lio pre imu_proc utils vikit_common_vendor sophus_vendor)

add_executable(fastlivo_mapping src/main.cpp)
configure_fast_livo_target(fastlivo_mapping)
target_link_libraries(fastlivo_mapping
  laser_mapping
  vio
  lio
  pre
  imu_proc
  utils
  vikit_common_vendor
  sophus_vendor
  ${Boost_LIBRARIES}
)

install(TARGETS
  fastlivo_mapping
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  config
  launch
  rviz_cfg
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
