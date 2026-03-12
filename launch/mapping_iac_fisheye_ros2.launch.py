import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    default_config = os.path.join(
        get_package_share_directory("fast_livo"),
        "config",
        "iac_front_lidar_fisheye_ros2.yaml",
    )

    config_arg = DeclareLaunchArgument(
        "config",
        default_value=default_config,
        description="Path to FAST-LIVO2 ROS2 parameter YAML",
    )

    mapping_node = Node(
        package="fast_livo",
        executable="fastlivo_mapping",
        name="laserMapping",
        output="screen",
        parameters=[
            LaunchConfiguration("config"),
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([
        config_arg,
        mapping_node,
    ])
