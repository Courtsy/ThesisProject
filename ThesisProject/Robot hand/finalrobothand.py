import os
import pybullet as p
import pandas as pd
import time

# Connect to PyBullet
p.connect(p.GUI)
p.setGravity(0, 0, 0)


# Reset the camera for a better view
p.resetDebugVisualizerCamera(cameraDistance=0.01, cameraYaw=30,
                             cameraPitch=-30, cameraTargetPosition=[0.5, -0.9, 0.75])

# Load the robot hand URDF (use the direct path instead of os.path.join)
robot_id = p.loadURDF(r"C:\Users\tommo\Downloads\simox_ros-master\simox_ros-master\sr_grasp_description\urdf\shadowhand.urdf", useFixedBase=True)

# Read the joint information
joint_name_to_index = {p.getJointInfo(robot_id, i)[1].decode('utf-8'): i for i in range(p.getNumJoints(robot_id))}



# Load CSV data
csv_file_path = r'C:\Users\tommo\animation_hand\test2.csv'
data = pd.read_csv(csv_file_path)
dataset = data.values.tolist()

# Set the position for each joint according to the CSV file
for data_row in dataset:
    for joint_name, target_position in zip(data.columns, data_row):
        if joint_name in joint_name_to_index:
            joint_index = joint_name_to_index[joint_name]
            p.setJointMotorControl2(bodyUniqueId=robot_id,
                                    jointIndex=joint_index,
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=target_position)





    # Step the simulation
    p.stepSimulation()
    # Sleep to control the speed of the simulation
    time.sleep(1.0 / 100.0)

# Keep the simulation window open until closed by the user
while p.isConnected():
    p.stepSimulation()
    time.sleep(1.0 / 240.0)

# Disconnect from PyBullet
p.disconnect()
