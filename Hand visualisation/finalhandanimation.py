# Importing required libraries
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Load the data from a CSV file into a pandas DataFrame
data_path = 'pinch_1.csv'  
hand_data = pd.read_csv(data_path)
hand_data.columns = hand_data.columns.str.strip()  # Strip leading spaces from column names for consistency

# Mapping of old joint names to new, descriptive names for clarity
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

# Replace the 'Joint' column values in the DataFrame with the new names from the name_remapping dictionary
hand_data['Joint'] = hand_data['Joint'].replace(name_remapping)

# Define the connections between joints to construct the visualisation of the hand
connections = [('HandWristBase', 'HandWristStart'),
               ('HandWristStart', 'Thumb1'),
               ('Thumb1', 'Thumb2'),
               ('Thumb2', 'Thumb3'),
               ('Thumb3', 'Thumb4'),
               ('Thumb4', 'ThumbTip'),
               ('HandWristStart', 'Index1'),
               ('Index1', 'Index2'),
               ('Index2', 'Index3'),
               ('Index3', 'IndexTip'),
               ('HandWristStart', 'Middle1'),
               ('Middle1', 'Middle2'),
               ('Middle2', 'Middle3'),
               ('Middle3', 'MiddleTip'),
               ('HandWristStart', 'Ring1'),
               ('Ring1', 'Ring2'),
               ('Ring2', 'Ring3'),
               ('Ring3', 'RingTip'),
               ('HandWristStart', 'Pinky1'),
               ('Pinky1', 'Pinky2'),
               ('Pinky2', 'Pinky3'),
               ('Pinky3', 'Pinky4'),
               ('Pinky4', 'PinkyTip'),
               ('Thumb2', 'Index1'),
               ('Index1', 'Middle1'),
               ('Middle1', 'Ring1'),
               ('Ring1', 'Pinky2')

]

# Dictionary to map finger names to specific colors for the animation
finger_colors = {
    'Thumb': 'red',
    'Index': 'blue',
    'Middle': 'green',
    'Ring': 'purple',
    'Pinky': 'orange'
}

# Set of connections that should be colored black regardless of the finger
black_connections = {('Thumb1', 'Thumb2'), ('Pinky1', 'Pinky2')}

# Function to determine the color of a connection based on the finger and the predefined colors
def get_color_for_connection(connection):
    # If the connection tuple is in the set of black_connections, return 'black'
    if connection in black_connections or (connection[1], connection[0]) in black_connections:
        return 'black'

    # Loop through each finger in finger_colors to determine the color of the connection
    for finger, color in finger_colors.items():
         # If both joints in the connection belong to the same finger, return the finger's color
        if finger in connection[0] and finger in connection[1]:
            return color
    # Default color if no specific color is determined
    return 'black'


# Function to animate the hand tracking data 
def animate_hand(df, connections):
    # Initialise a new figure and 3D axis for plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Group the DataFrame by 'Timestamp' to animate each frame based on the timestamp
    grouped = df.groupby('Timestamp')

    # Function to update the animation for each frame
    def update(frame_num, grouped, ax):
        # Clear the current axes
        ax.cla()

        # Set the axes limits based on the min and max values of the positions
        ax.set_xlim3d([df['PositionX'].min(), df['PositionX'].max()])
        ax.set_ylim3d([df['PositionY'].min(), df['PositionY'].max()])
        ax.set_zlim3d([df['PositionZ'].min(), df['PositionZ'].max()])
        
        # Get the data for the current frame based on the frame number
        frame_data = grouped.get_group(frame_num)

        # Extract the position data for x, y, and z
        xdata = frame_data['PositionX']
        ydata = frame_data['PositionY']
        zdata = frame_data['PositionZ']

        # Plot the joint positions as scatter points
        ax.scatter(xdata, ydata, zdata)

        # Loop through each connection and plot lines between the connected joints
        for joint_a, joint_b in connections:
            # Check if both joints in the connection are in the current frame data
            if joint_a in frame_data['Joint'].values and joint_b in frame_data['Joint'].values:
                # Get the data for each joint
                joint_a_data = frame_data[frame_data['Joint'] == joint_a]
                joint_b_data = frame_data[frame_data['Joint'] == joint_b]
                # Determine the color for the connection
                color = get_color_for_connection((joint_a, joint_b))
                # Plot the line connecting the two joints with the determined color
                ax.plot([joint_a_data['PositionX'].values[0], joint_b_data['PositionX'].values[0]],
                        [joint_a_data['PositionY'].values[0], joint_b_data['PositionY'].values[0]],
                        [joint_a_data['PositionZ'].values[0], joint_b_data['PositionZ'].values[0]], color=color)

        return fig,

    # Create the animation using FuncAnimation
    ani = FuncAnimation(fig, update, frames=grouped.groups.keys(),
                        fargs=(grouped, ax), interval=50, blit=False)

    return ani
# Call the function to animate the hand data with the defined connections
ani = animate_hand(hand_data, connections)
# Display the animation
plt.show()