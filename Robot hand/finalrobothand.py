# Import the necessary libraries.
import pybullet as p
import pandas as pd
import time

# Connect to the PyBullet physics simulation.
p.connect(p.GUI)
p.setGravity(0, 0, 0) # Set gravity to zero for all axes


# Reset the camera to have a clear view of the simulation
# Adjust the camera's distance, yaw, pitch, and target position for better visualisation
p.resetDebugVisualizerCamera(cameraDistance=0.01, cameraYaw=30,
                             cameraPitch=-30, cameraTargetPosition=[0.5, -0.9, 0.75])

# Load the robot hand URDF file
robot_id = p.loadURDF(r"C:\Users\tommo\Downloads\simox_ros-master\simox_ros-master\sr_grasp_description\urdf\shadowhand.urdf", useFixedBase=True)

# Create a mapping of joint names to their respective indices within the PyBullet simulation
joint_name_to_index = {p.getJointInfo(robot_id, i)[1].decode('utf-8'): i for i in range(p.getNumJoints(robot_id))}



# Load the CSV file containing the formatted data for the hand
csv_file_path = r'C:\Users\tommo\animation_hand\test2.csv'
data = pd.read_csv(csv_file_path)
dataset = data.values.tolist()

# Iterate through each row in the dataset, which corresponds to a set of joint positions
for data_row in dataset:
    # Zip together the column names (joint names) and the values in the row (target positions)
    for joint_name, target_position in zip(data.columns, data_row):
        # If the joint name is recognized in the simulation, find its index
        if joint_name in joint_name_to_index:
            joint_index = joint_name_to_index[joint_name]
            # Set the joint to move to the target position
            p.setJointMotorControl2(bodyUniqueId=robot_id,
                                    jointIndex=joint_index,
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=target_position)





    # Step the simulation forward
    p.stepSimulation()
    # Sleep to control the speed of the simulation
    time.sleep(1.0 / 100.0)

# Keep the simulation window open until manually closed
while p.isConnected():
    p.stepSimulation()
    time.sleep(1.0 / 240.0)

# Disconnect from PyBullet once the simulation is closed
p.disconnect()
