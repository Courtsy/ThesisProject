# Importing necessary libraries
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R

# Load the data
data_path = 'pinch_1.csv'  # Define the path to the CSV file containing hand data
hand_data = pd.read_csv(data_path) # Read the CSV file into a pandas DataFrame
hand_data.columns = hand_data.columns.str.strip()  # Remove any leading or trailing spaces from column names

# Mapping of old joint names to new, more descriptive names for clarity
name_remapping = {'Body_Start': 'HandWristBase',
                  'Body_Hips': 'HandWristStart',
                  'Body_SpineLower': 'Thumb1',
                  'Hand_Thumb1': 'Thumb2',
                  'Body_SpineUpper': 'Thumb3',
                  'Body_Chest': 'Thumb4',
                  'Hand_ThumbTip': 'ThumbTip',
                  'Body_Neck': 'Index1',
                  'Body_Head': 'Index2',
                  'Body_LeftShoulder': 'Index3',
                  'Hand_IndexTip': 'IndexTip',
                  'Body_LeftScapula': 'Middle1',
                  'Body_LeftArmUpper': 'Middle2',
                  'Body_LeftArmLower': 'Middle3',
                  'Hand_MiddleTip': 'MiddleTip',
                  'Hand_Ring1' : 'Ring1',
                  'Body_RightShoulder': 'Ring2',
                  'Hand_Ring3': 'Ring3',
                  'Body_LeftHandThumbDistal': 'RingTip',
                  'Hand_Pinky0': 'Pinky1',
                  'Body_RightArmLower': 'Pinky2',
                  'Hand_Pinky2': 'Pinky3',
                  'Body_LeftHandPalm': 'Pinky4',
                  'Body_LeftHandThumbTip': 'PinkyTip'
}

# Apply the name remapping to the 'Joint' column of the DataFrame
hand_data['Joint'] = hand_data['Joint'].replace(name_remapping)

# Filter out only the columns needed 
hand_data= hand_data[['Joint', 'RotationX', 'RotationY', 'RotationZ', 'RotationW']]

# Print the transformed DataFrame to check the loaded data
print(hand_data)

# Function to compute the rotation angle between two sets of quaternion rotations
def compute_rotation_angle(data_original):
    """
    This function computes the rotation angle for each joint with respect to the first measurement.
    The rotation angle is the angle by which one rotation must be rotated to align with another rotation.
    """
    # Inner function that computes the rotation angle between two quaternions
    def rotation_angle(rotation1, rotation2):
        # Convert quaternions to rotation objects
        r1 = R.from_quat(rotation1)
        r2 = R.from_quat(rotation2)
        # Calculate the relative rotation by inverting one and multiplying it by the other
        relative_rotation = r2.inv() * r1
        # The magnitude of the rotation gives the angle in radians
        return relative_rotation.magnitude()

    # DataFrame to store the names of the joints and their respective rotation angles
    rotation_angles = pd.DataFrame(columns=['Name', 'Value'])

    # Calculate the number of groups of joints by assuming each group has 24 joints
    num_groups = len(data_original) // 24

    # Isolate the first group to serve as a reference for calculating relative rotations
    first_group = data_original.iloc[0:24, :]

    # Iterate over each group to calculate the rotation angles
    for g in range(1, num_groups):
        # Isolate the current group
        group = data_original.iloc[g*24:(g+1)*24, :]
        # Reset the index of the group
        group.reset_index(drop=True, inplace=True)
        # Calculate the rotation angle for each joint in the group relative to the first group
        for i in range(24):
            rotation1 = first_group.iloc[i, 1:5]
            rotation2 = group.iloc[i, 1:5]
            angle = rotation_angle(rotation1, rotation2)
            # Create a new row with the joint name and the computed angle
            new_row = pd.DataFrame({'Name': [first_group.iloc[i, 0]], 'Value': [angle]})
            # Append the new row to the DataFrame of angles
            rotation_angles = pd.concat([rotation_angles, new_row], ignore_index=True)

    return rotation_angles

# Function to transform the original data to a new structure for robotic hand simulation
def transform_data(data):
    """
    This function transforms the data into a structure that is more suitable for robotic hand simulation.
    It maps the joints to new names and groups the data in a way that can be used to control a robotic hand.
    """
    # Add a 'Group' column to the DataFrame to help in identifying the set of rotations
    data['Group'] = data.index // 24

    # Define a mapping for the joints to new names for the robotic hand
    mapping = {
        'Index1': 'FFJ3',
        'Index2': 'FFJ2',
        'Index3': 'FFJ1',
        'Middle1': 'MFJ3',
        'Middle2': 'MFJ2',
        'Middle3': 'MFJ1',
        'Ring1': 'RFJ3',
        'Ring2': 'RFJ2',
        'Ring3': 'RFJ1',
        'Pinky1': 'LFJ5',
        'Pinky2': 'LFJ3',
        'Pinky3': 'LFJ2',
        'Pinky4': 'LFJ1',
        'Thumb1': 'THJ5',
        'Thumb2': 'THJ4',
        'Thumb3': 'THJ2',
        'Thumb4': 'THJ1',
        
    }

    # Define the new column names for the transformed data
    columns_new = ['WRJ2', 'WRJ1', 'FFJ4', 'FFJ3', 'FFJ2', 'FFJ1', 'FFtip', 'MFJ4', 'MFJ3', 'MFJ2', 'MFJ1', 'MFtip', 'RFJ4', 'RFJ3', 'RFJ2', 'RFJ1',
                   'RFtip', 'LFJ5', 'LFJ4', 'LFJ3', 'LFJ2', 'LFJ1', 'LFtip', 'THJ5', 'THJ4', 'THJ3', 'THJ2', 'THJ1', 'thtip']

    # DataFrame to hold the transformed data
    df_new = pd.DataFrame(columns=columns_new)

    # Iterate over each group and transform the data accordingly
    for group, data_grouped in data.groupby('Group'):
        # Series to hold the data for the new row
        row_new = pd.Series(index=columns_new, dtype='float')

        # Map the original data to the new structure using the defined mapping
        for col_new in columns_new:
            if col_new in mapping.values():
                # Find the original column name that maps to the new column name
                col_original = [k for k, v in mapping.items() if v == col_new][0]
                # Set the value in the new row
                row_new[col_new] = data_grouped[data_grouped['Name'] == col_original]['Value'].values[0]
            else:
                # If there's no mapping, set the value to 0
                row_new[col_new] = 0
        # Add the new row to the DataFrame
        df_new = pd.concat([df_new, pd.DataFrame(row_new).transpose()])

    return df_new

# Use the compute_rotation_angle function to calculate the rotation angles
data = compute_rotation_angle(hand_data)

# Transform the data using the transform_data function
df_new = transform_data(data)

# Save the transformed data to a new CSV file for use with the robotic hand
df_new.to_csv('pinchrobot.csv', index=False)

