import numpy as np
from pyproj import Proj
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import pdb

# local 'zero' point in lat/lon (mcity garage)
# utm zone (ann arbor) = 17
MCITY_LAT = 42.298977
MCITY_LON = -83.699394

# measurements (m) taken on 2015 lincoln mkz
ROH = 1.08
FOH = 1.00
W = 2.850
L = 4.930

# convert from lat/lon to UTM
def latlon_to_utm(lat, lon):
   utm_project = Proj(proj='utm', zone=17, ellps='WGS84')
   utm_x, utm_y = utm_project(lon, lat)

   return utm_x, utm_y

def translate_data(filename):
    data = pd.read_csv(filename)
    utm_mcity_x, utm_mcity_y = latlon_to_utm(MCITY_LAT, MCITY_LON)

    # convert gps to utm 
    data['utm_x'], data['utm_y'] = zip(*data.apply(lambda row: latlon_to_utm(row['latitude'], row['longitude']), axis=1))

    print(f"Vehicle data UTM X: {data['utm_x'][0]}, UTM Y: {data['utm_y'][0]}")

    # translate data using reference point
    utm_col_x = data['utm_x'] - utm_mcity_x
    utm_col_y = data['utm_y'] - utm_mcity_y

    print(f"Translated vehicle data x: {utm_col_x[0]}, y: {utm_col_y[0]}")

    return utm_col_x, utm_col_y

def update(frame, x, y):
    plt.clf()

    # plot all points
    # rtk_x = x[:frame+1]
    # rtk_y = y[:frame+1]

    # only plot current frame
    rtk_x = x[frame]
    rtk_y = y[frame]

    # calculate points based on slides & lincoln mkz measurements
    x1 = rtk_x + (L - ROH)
    y1 = rtk_y - (W / 2)

    x2 = rtk_x - ROH
    y2 = rtk_y - (W / 2)

    x3 = rtk_x - ROH
    y3 = rtk_y + (W / 2)

    x4 = rtk_x + (L - ROH)
    y4 = rtk_y + (W / 2)
    
    # plt.plot(x[:frame+1], y[:frame+1], marker='o')
    plt.plot([x1, x2, x3, x4, x1], [y1, y2, y3, y4, y1], color='red')
    plt.xlim(min(x) - 5, max(x) + 5)
    plt.ylim(min(y) - 5, max(y) + 5)
    plt.title(f"Frame {frame}", fontsize=8)
    plt.suptitle('Animation of Vehicle RTK', fontsize=16)
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

    file_path = 'output/_vehicle_gps_fix.csv'
    x, y = translate_data(file_path)
    print(x)
    print(y)

    fig, ax = plt.subplots()

    num_frames = len(x)
    ani = animation.FuncAnimation(fig, update, frames=num_frames, fargs=(x, y), interval=1, repeat=False)
    plt.show()

    # plot_coordinates(x, y)

if __name__ == "__main__":
    # This block gets executed when the script is run directly
    main()


# def XYfromGPS(lat1, long1, lat2, long2):
#   R = 6.371*10^6 # earth radius
#   lat1_ = (lat1 * np.pi) / 180
#   lat2_ = (lat2 * np.pi) / 180
#   long1_ = (long1 * np.pi) / 180
#   long2_ = (long2 * np.pi) / 180

#   y2 = R * (lat2_ - lat1_)
#   x2 = R * (long2_ - long1_) * np.cos(0.5 * (lat2_ + lat1_))
#   b2 = np.arctan2(x2, y2) * 180 / np.pi + 180

#   return [x2, y2, b2]


# # GPS_x (m) : ref point data (raw GPS arrays)
# # GPS_Y (m) : ref point data
# # Hdg (deg) : ref point heading

# # measurements taken from slides
# ROH = 1.08
# FOH = 1.00
# W = 2.850
# L = 4.930

# # GPS Ref point data into Boundary Points 1-4

# # Center-based boundary points:
# # Basic Position: GPS Reference Point at (0,0), Heading at 0 deg
# # boundary_points_basic - calculate center point
# basic_x = [L/2, -L/2, -L/2, L/2]
# basic_y = [-W/2, -W/2, W/2, W/2]

# Rotated_vehicle_boundary_x = basic_x * np.cos(Hdg) - basic_y*np.sin(Hdg)
# Rotated_vehicle_boundary_y = basic_x *np.sin(Hdg) + basic_y*np.cos(Hdg)

# Final_vehicle_boundary_center_x = center_x + Rotated_vehicle_boundary_x
# Final_vehicle_boundary_center_y = center_y + Rotated_vehicle_boundary_y

# # GPS-based boundary points:
# basic_x = [L-ROH, -ROH, -ROH, L-ROH]
# basic_y = [-W/2, -W/2 ,  W/2 , W/2]

# Rotated_vehicle_boundary_x = basic_x * np.cos(Hdg) - basic_y*np.sin(Hdg)
# Rotated_vehicle_boundary_y = basic_x *np.sin(Hdg) + basic_y*np.cos(Hdg)

# Final_vehicle_boundary_GPS_x = GPS_x + Rotated_vehicle_boundary_x
# Final_vehicle_boundary_GPS_y = GPS_y + Rotated_vehicle_boundary_y

# # animate box using  trigonometric translation and rotation of the 4 corners of the box relative to the (assumed) GPS Reference point
# # [ Final_vehicle_boundary_GPS_x, Final_vehicle_boundary_GPS_y ]
# Point1_x = Final_vehicle_boundary_GPS_x + (L - ROH)
# Point1_y = Final_vehicle_boundary_GPS_y - (W / 2)

# Point2_x = Final_vehicle_boundary_GPS_x - ROH
# Point2_y = Final_vehicle_boundary_GPS_y - (W / 2)

# Point3_x = Final_vehicle_boundary_GPS_x - ROH
# Point3_y = Final_vehicle_boundary_GPS_y + (W / 2)

# Point4_x = Final_vehicle_boundary_GPS_x + (L - ROH)
# Point4_y = Final_vehicle_boundary_GPS_y + (W / 2)

# coordinates_list = [
#     [(0, 0), (1, 0), (1, 1), (0, 1)],
#     [(1, 1), (2, 1), (2, 2), (1, 2)],
#     [(2, 2), (3, 2), (3, 3), (2, 3)],
#     [(3, 3), (4, 3), (4, 4), (3, 4)],
#     [(4, 4), (5, 4), (5, 5), (4, 5)]
# ]

# def get_new_coordinates(frame):
#     if frame < len(coordinates_list):
#         return coordinates_list[frame]
#     else:
#         # Handle the case where frame is out of range
#         return coordinates_list[-1]  # Return the last set of coordinates

# def draw_rectangle(ax, coordinates):
#   x = [point[0] for point in coordinates]
#   y = [point[1] for point in coordinates]
#   ax.add_patch(Rectangle((x[0], y[0]), x[2] - x[0], y[2] - y[0], fill=None, edgecolor='r'))

# def update(frame):
#   pdb.set_trace()
#   print(frame)
#   global min_x, max_x, min_y, max_y
#   ax.clear()
#   ax.plot([0, 5],[0, 5])
#   new_coordinates = get_new_coordinates(frame)
#   draw_rectangle(ax, new_coordinates)
#   # ax.set_xlim(min_x, max_x + 1)
#   # ax.set_ylim(min_y, max_y + 1)
#   ax.set_title('Frame {}'.format(frame))

# # Set up the figure and axis
# fig, ax = plt.subplots()
# ax.plot([0, 10],[0, 10])

# min_x = min(point[0] for point in coordinates_list)
# max_x = max(point[0] for point in coordinates_list)
# min_y = min(point[1] for point in coordinates_list)
# max_y = max(point[1] for point in coordinates_list)

# initial_coordinates = [(0, 0), (1, 0), (1, 1), (0, 1)]

# # Draw the initial rectangle
# draw_rectangle(ax, initial_coordinates)

# # Set up the animation
# num_frames = 5 # Adjust the number of frames as needed
# ani = animation.FuncAnimation(fig=fig, func=update, frames=num_frames, interval=30, repeat=False)
# plt.show()