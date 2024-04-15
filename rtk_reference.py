import numpy as np
from pyproj import Proj
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from helper import latlon_to_utm, convert_string_to_arr, extract_latitude, extract_longitude
import pdb
import ast
import math

# local 'zero' point in lat/lon (mcity garage)
# utm zone (ann arbor) = 17
MCITY_LAT = 42.298977
MCITY_LON = -83.699394

# measurements (m) taken on 2015 lincoln mkz
ROH = 1.08
FOH = 1.00
W = 2.850
L = 4.930

def translate_gps_heading_data(filename1, filename2):
    data1 = pd.read_csv(filename1)
    data2 = pd.read_csv(filename2)
    data = pd.merge(data2, data1, on='stamp', how='inner')

    # Convert string representations of NumPy arrays to actual NumPy arrays
    data['position_covariance'] = data['position_covariance'].apply(convert_string_to_arr)
    data['latitude'] = data['position_covariance'].apply(extract_latitude)
    data['longitude'] = data['position_covariance'].apply(extract_longitude)

    utm_mcity_x, utm_mcity_y = latlon_to_utm(MCITY_LAT, MCITY_LON)

    # convert gps to utm 
    data['utm_x'], data['utm_y'] = zip(*data.apply(lambda row: latlon_to_utm(row['latitude'], row['longitude']), axis=1))
    print(f"Vehicle data UTM X: {data['utm_x'][0]}, UTM Y: {data['utm_y'][0]}")

    # translate data using reference point
    utm_col_x = data['utm_x'] - utm_mcity_x
    utm_col_y = data['utm_y'] - utm_mcity_y
    print(f"Translated vehicle data x: {utm_col_x[0]}, y: {utm_col_y[0]}")

    orientation_w = data['pose.pose.orientation.w']
    orientation_x = data['pose.pose.orientation.x']
    orientation_y = data['pose.pose.orientation.y']
    orientation_z = data['pose.pose.orientation.z']

    return [utm_col_x, utm_col_y, orientation_w, orientation_x, orientation_y, orientation_z]

def translate_gps_data(filename1):
    data = pd.read_csv(filename1)
    
    utm_mcity_x, utm_mcity_y = latlon_to_utm(MCITY_LAT, MCITY_LON)

    # convert gps to utm 
    data['utm_x'], data['utm_y'] = zip(*data.apply(lambda row: latlon_to_utm(row['latitude'], row['longitude']), axis=1))
    print(f"Vehicle data UTM X: {data['utm_x'][0]}, UTM Y: {data['utm_y'][0]}")

    # translate data using reference point
    utm_col_x = data['utm_x'] - utm_mcity_x
    utm_col_y = data['utm_y'] - utm_mcity_y
    print(f"Translated vehicle data x: {utm_col_x[0]}, y: {utm_col_y[0]}")

    return utm_col_x, utm_col_y

def update(frame, x, y, o_w, o_x, o_y, o_z):
    plt.clf()
    frame = frame * 20
    rtk_x = x[frame]
    rtk_y = y[frame]
    init_rtk_x = x[0]
    init_rtk_y = y[0]

    # Extract orientation data for the first frame
    init_w = o_w[0]
    init_x = o_x[0]
    init_y = o_y[0]
    init_z = o_z[0]

    # Extract orientation data for the current frame
    orientation_w = o_w[frame]
    orientation_x = o_x[frame]
    orientation_y = o_y[frame]
    orientation_z = o_z[frame]

    # Calculate the orientation angle (in radians) from quaternion components
    init_angle = np.arctan2(2 * (init_w * init_z + init_x * init_y),
                                   1 - 2 * (init_y**2 + init_z**2))
    orientation_angle = np.arctan2(2 * (orientation_w * orientation_z + orientation_x * orientation_y),
                                   1 - 2 * (orientation_y**2 + orientation_z**2))
    
    # Rotate vehicle based on the orientation angle
    init_rotation_matrix = np.array([[np.cos(init_angle), -np.sin(init_angle)],
                                [np.sin(init_angle), np.cos(init_angle)]])
    rotation_matrix = np.array([[np.cos(orientation_angle), -np.sin(orientation_angle)],
                                [np.sin(orientation_angle), np.cos(orientation_angle)]])

    # Coordinates of the rectangle with respect to the center of rotation (rtk_x, rtk_y)
    rectangle_coords = np.array([[L - ROH, -ROH, -ROH, L - ROH], [-W / 2, -W / 2, W / 2, W / 2]])

    # Rotate vehicle
    init_rotated_points = np.dot(init_rotation_matrix, rectangle_coords)
    rotated_points = np.dot(rotation_matrix, rectangle_coords)

    # Translate the rotated points back to the correct position
    init_rotated_points[0, :] += init_rtk_x
    init_rotated_points[1, :] += init_rtk_y
    rotated_points[0, :] += rtk_x
    rotated_points[1, :] += rtk_y

    # Append the starting point to the end to close the rectangle
    rotated_points = np.hstack([rotated_points, rotated_points[:, 0].reshape(-1, 1)])
    init_rotated_points = np.hstack([init_rotated_points, init_rotated_points[:, 0].reshape(-1, 1)])

    # Plot vehicle RTK
    plt.plot(x[:frame+1], y[:frame+1], marker='o', markersize=3, linestyle='')

    # Plot the original starting position of the vehicle
    plt.plot(init_rotated_points[0, :], init_rotated_points[1, :], color='gray')
    plt.plot(init_rotated_points[0, 3:5], init_rotated_points[1, 3:5], color='darkiv
    green')

    # Plot current position of the vehicle
    plt.plot(rotated_points[0, :], rotated_points[1, :], color='red')
    plt.plot(rotated_points[0, 3:5], rotated_points[1, 3:5], color='green')

    # Plot
    plt.legend(labels=['Vehicle RTK', 'Initial Position', 'Front of Vehicle (Initial)', 'Current Position', 'Front of Vehicle (Current)'])
    plt.xlim(min(x) - 20, max(x) + 20)
    plt.ylim(min(y) - 20, max(y) + 20)
    plt.title(f"Frame {frame}", fontsize=8)
    plt.suptitle('Vehicle RTK', fontsize=16)
    plt.xlabel('X-axis (m) in relation to reference point (mcity garage)')
    plt.ylabel('Y-axis (m)')

def plot_coordinates(x, y):
    plt.plot(x, y, marker='o')
    plt.title('Plot of Coordinates')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()
    
def main():
    utm_x, utm_y = latlon_to_utm(MCITY_LAT, MCITY_LON)
    print(f"MCITY GARAGE UTM X: {utm_x}, UTM Y: {utm_y}")

    # file_path = 'output/_vehicle_gps_fix.csv'
    file_path1 = 'test1_gps.csv'
    file_path2 = 'test1_novatel_utm_odom.csv'
    # x, y = translate_gps_data(file_path)
    vehicle_arr = translate_gps_heading_data(file_path1, file_path2)
    x = vehicle_arr[0]
    y = vehicle_arr[1]
    o_w = vehicle_arr[2]
    o_x = vehicle_arr[3]
    o_y = vehicle_arr[4]
    o_z = vehicle_arr[5]

    print(o_w, o_x, o_y, o_z)

    fig, ax = plt.subplots()

    num_frames = len(x)
    ani = animation.FuncAnimation(fig, update, frames=math.floor(num_frames/20), fargs=(x, y, o_w, o_x, o_y, o_z), interval=1, repeat=False)
    plt.show()

if __name__ == "__main__":
    main()