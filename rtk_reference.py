# function [x2 y2 b2] = XYfromGPS(lat1, long1, lat2, long2)
# % url: https://ccv.eng.wayne.edu/m_script.html
# % converts GPS coordinates into cartesian coordinate system
# % such that XY plane is tangent to P1 and Y points to the NORTH and
# % X points to the EAST and assuming P1 is at the origin (x1,y1)=(0,0)
# % North
# %   ^
# %   |
# %   Y
# %   |
# %  0,0---X--->East
# % inputs lat1, long1, lat2, long2
# % output x2 y2 b2-heading
#   R=6.371*10^6; %earth radius
#   lat1_=lat1*pi/180; %convert degrees into radians
#   lat2_=lat2*pi/180;
#   long1_=long1*pi/180;
#   long2_=long2*pi/180;

#   y2 = R*(lat2_-lat1_);
#   x2 = R*(long2_-long1_).*cos(lat1_);
#   b2 = atan2(x2,y2)*180/pi+180;
#   %b2 = atan2(x2,y2)*180/pi;
# end

import numpy as np

def XYfromGPS(lat1, long1, lat2, long2):
  R = 6.371*10^6 # earth radius
  lat1_ = (lat1 * np.pi) / 180
  lat2_ = (lat2 * np.pi) / 180
  long1_ = (long1 * np.pi) / 180
  long2_ = (long2 * np.pi) / 180

  y2 = R * (lat2_ - lat1_)
  x2 = R * (long2_ - long1_) * np.cos(0.5 * (lat2_ + lat1_))
  b2 = np.arctan2(x2, y2) * 180 / np.pi + 180

  return [x2, y2, b2]

# initial assumption of RTK:

# GPS_x (m) : ref point data
# GPS_Y (m) : ref point data
# Hdg (deg) : ref point heading

# measurements taken from slides
ROH = 1.08
FOH = 1.00
W = 2.850
L = 4.930


# GPS Ref point data into Boundary Points 1-4

# GPS-based boundary points:
# Basic Position: GPS Reference Point at (0,0), Heading at 0 deg
# boundary_points_basic - calculate center point
center_x = [L/2, -L/2, -L/2, L/2]
center_y = [-W/2, -W/2, W/2, W/2]

Rotated_vehicle_boundary_x = center_x * np.cos(Hdg) - center_y*np.sin(Hdg)
Rotated_vehicle_boundary_y = center_x *np.sin(Hdg) + center_y*np.cos(Hdg)

Final_vehicle_boundary_center_x = center_x + Rotated_vehicle_boundary_x
Final_vehicle_boundary_center_y = center_y + Rotated_vehicle_boundary_y


basic_x = [L-ROH, -ROH, -ROH, L-ROH]
basic_y = [-W/2, -W/2 ,  W/2 , W/2]

Rotated_vehicle_boundary_x = basic_x * np.cos(Hdg) - basic_y*np.sin(Hdg)
Rotated_vehicle_boundary_y = basic_x *np.sin(Hdg) + basic_y*np.cos(Hdg)

Final_vehicle_boundary_GPS_x = basic_x + Rotated_vehicle_boundary_x
Final_vehicle_boundary_GPS_y = basic_y + Rotated_vehicle_boundary_y

# animate box using  trigonometric translation and rotation of the 4 corners of the box relative to the (assumed) GPS Reference point

# [ Final_vehicle_boundary_GPS_x, Final_vehicle_boundary_GPS_y ]

Point1_x = Final_vehicle_boundary_GPS_x + (L - ROH)
Point1_y = Final_vehicle_boundary_GPS_y - (W / 2)

Point2_x = Final_vehicle_boundary_GPS_x - ROH
Point2_y = Final_vehicle_boundary_GPS_y - (W / 2)

Point3_x = Final_vehicle_boundary_GPS_x - ROH
Point3_y = Final_vehicle_boundary_GPS_y + (W / 2)

Point4_x = Final_vehicle_boundary_GPS_x + (L - ROH)
Point4_y = Final_vehicle_boundary_GPS_y + (W / 2)

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import pdb

coordinates_list = [
    [(0, 0), (1, 0), (1, 1), (0, 1)],
    [(1, 1), (2, 1), (2, 2), (1, 2)],
    [(2, 2), (3, 2), (3, 3), (2, 3)],
    [(3, 3), (4, 3), (4, 4), (3, 4)],
    [(4, 4), (5, 4), (5, 5), (4, 5)]
]

def get_new_coordinates(frame):
    if frame < len(coordinates_list):
        return coordinates_list[frame]
    else:
        # Handle the case where frame is out of range
        return coordinates_list[-1]  # Return the last set of coordinates

def draw_rectangle(ax, coordinates):
  x = [point[0] for point in coordinates]
  y = [point[1] for point in coordinates]
  ax.add_patch(Rectangle((x[0], y[0]), x[2] - x[0], y[2] - y[0], fill=None, edgecolor='r'))

def update(frame):
  pdb.set_trace()
  print(frame)
  global min_x, max_x, min_y, max_y
  ax.clear()
  ax.plot([0, 5],[0, 5])
  new_coordinates = get_new_coordinates(frame)
  draw_rectangle(ax, new_coordinates)
  # ax.set_xlim(min_x, max_x + 1)
  # ax.set_ylim(min_y, max_y + 1)
  ax.set_title('Frame {}'.format(frame))

# Set up the figure and axis
fig, ax = plt.subplots()
ax.plot([0, 10],[0, 10])

min_x = min(point[0] for point in coordinates_list)
max_x = max(point[0] for point in coordinates_list)
min_y = min(point[1] for point in coordinates_list)
max_y = max(point[1] for point in coordinates_list)

initial_coordinates = [(0, 0), (1, 0), (1, 1), (0, 1)]

# Draw the initial rectangle
draw_rectangle(ax, initial_coordinates)

# Set up the animation
num_frames = 5 # Adjust the number of frames as needed
ani = animation.FuncAnimation(fig=fig, func=update, frames=num_frames, interval=30, repeat=False)
plt.show()

