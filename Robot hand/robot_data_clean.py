import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R

# Load the data
data_path = 'pinch_1.csv'  # Replace with the path to your data file
hand_data = pd.read_csv(data_path)
hand_data.columns = hand_data.columns.str.strip()  # Strip leading spaces from column names

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

hand_data['Joint'] = hand_data['Joint'].replace(name_remapping)

hand_data= hand_data[['Joint', 'RotationX', 'RotationY', 'RotationZ', 'RotationW']]

print(hand_data)

def compute_rotation_angle(data_original):
    # This function will compute the rotation angle between two quaternions
    def rotation_angle(rotation1, rotation2):
        r1 = R.from_quat(rotation1)
        r2 = R.from_quat(rotation2)
        relative_rotation = r2.inv() * r1
        return relative_rotation.magnitude()

    # Create an empty DataFrame to store the computed rotation angles
    rotation_angles = pd.DataFrame(columns=['Name', 'Value'])

    # Compute the number of groups
    num_groups = len(data_original) // 24

    # Get the first group of data
    first_group = data_original.iloc[0:24, :]

    # Compute the rotation angle for each group compared to the first group
    for g in range(1, num_groups):
        group = data_original.iloc[g*24:(g+1)*24, :]
        # Reset the index of the group
        group.reset_index(drop=True, inplace=True)
        for i in range(24):
            rotation1 = first_group.iloc[i, 1:5]
            rotation2 = group.iloc[i, 1:5]
            angle = rotation_angle(rotation1, rotation2)
            new_row = pd.DataFrame({'Name': [first_group.iloc[i, 0]], 'Value': [angle]})
            rotation_angles = pd.concat([rotation_angles, new_row], ignore_index=True)

    return rotation_angles

def transform_data(data):
    # Create a new column 'Group' to identify each group of 24 rows
    data['Group'] = data.index // 24

    # Define the mapping and new column names as before
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
        # Add more mappings if there are more joints
    }
    columns_new = ['WRJ2', 'WRJ1', 'FFJ4', 'FFJ3', 'FFJ2', 'FFJ1', 'FFtip', 'MFJ4', 'MFJ3', 'MFJ2', 'MFJ1', 'MFtip', 'RFJ4', 'RFJ3', 'RFJ2', 'RFJ1',
                   'RFtip', 'LFJ5', 'LFJ4', 'LFJ3', 'LFJ2', 'LFJ1', 'LFtip', 'THJ5', 'THJ4', 'THJ3', 'THJ2', 'THJ1', 'thtip']

    # Create a new DataFrame to hold the transformed data
    df_new = pd.DataFrame(columns=columns_new)

    # For each group of 24 rows...
    for group, data_grouped in data.groupby('Group'):
        # Create a new row in the new DataFrame
        row_new = pd.Series(index=columns_new, dtype='float')

        # Fill the new row using the original data and the mapping
        for col_new in columns_new:
            if col_new in mapping.values():
                col_original = [k for k, v in mapping.items() if v == col_new][0]
                row_new[col_new] = data_grouped[data_grouped['Name'] == col_original]['Value'].values[0]
            else:
                row_new[col_new] = 0
        # Add the new row to the new DataFrame using pd.concat
        df_new = pd.concat([df_new, pd.DataFrame(row_new).transpose()])

    return df_new

data = compute_rotation_angle(hand_data)
df_new = transform_data(data)
df_new.to_csv('pinchrobot.csv', index=False)

