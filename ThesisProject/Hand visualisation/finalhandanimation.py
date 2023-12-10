import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

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

finger_colors = {
    'Thumb': 'red',
    'Index': 'blue',
    'Middle': 'green',
    'Ring': 'purple',
    'Pinky': 'orange'
}

black_connections = {('Thumb1', 'Thumb2'), ('Pinky1', 'Pinky2')}

def get_color_for_connection(connection):
    # Check if the connection should be black
    if connection in black_connections or (connection[1], connection[0]) in black_connections:
        return 'black'

    # Check for each finger color
    for finger, color in finger_colors.items():
        if finger in connection[0] and finger in connection[1]:
            return color

    return 'black'


# Define the function to animate the hand data
# Define the function to animate the hand data
def animate_hand(df, connections):
    # Define figure and 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Group data by 'Timestamp'
    grouped = df.groupby('Timestamp')

    # Prepare the data for animation
    def update(frame_num, grouped, ax):
        ax.cla()

        # Set the axes properties
        ax.set_xlim3d([df['PositionX'].min(), df['PositionX'].max()])
        ax.set_ylim3d([df['PositionY'].min(), df['PositionY'].max()])
        ax.set_zlim3d([df['PositionZ'].min(), df['PositionZ'].max()])
        

        frame_data = grouped.get_group(frame_num)

        xdata = frame_data['PositionX']
        ydata = frame_data['PositionY']
        zdata = frame_data['PositionZ']

        ax.scatter(xdata, ydata, zdata)

        for joint_a, joint_b in connections:
            if joint_a in frame_data['Joint'].values and joint_b in frame_data['Joint'].values:
                joint_a_data = frame_data[frame_data['Joint'] == joint_a]
                joint_b_data = frame_data[frame_data['Joint'] == joint_b]
                color = get_color_for_connection((joint_a, joint_b))
                ax.plot([joint_a_data['PositionX'].values[0], joint_b_data['PositionX'].values[0]],
                        [joint_a_data['PositionY'].values[0], joint_b_data['PositionY'].values[0]],
                        [joint_a_data['PositionZ'].values[0], joint_b_data['PositionZ'].values[0]], color=color)

        return fig,

    ani = FuncAnimation(fig, update, frames=grouped.groups.keys(),
                        fargs=(grouped, ax), interval=50, blit=False)

    return ani

ani = animate_hand(hand_data, connections)
plt.show()