import numpy as np
from pyproj import Proj

# convert from lat/lon to UTM
def latlon_to_utm(lat, lon):
   if lat is not np.nan and lon is not np.nan:
    utm_project = Proj(proj='utm', zone=17, ellps='WGS84')
    utm_x, utm_y = utm_project(lon, lat)

    return utm_x, utm_y
   return np.nan, np.nan

def convert_string_to_arr(s):
    # Remove leading '[' and trailing ']' from the string
    if isinstance(s, str):
        s = s.strip('[').strip(']')
        num_strings = s.split()
        num_arr = [float(num) for num in num_strings]
        return num_arr
    else:
        return None

def extract_latitude(arr):
    # Check if the input is a list
    if isinstance(arr, (list, np.ndarray)):
        return arr[3]
    else:
        return np.nan

def extract_longitude(arr):
    # Check if the input is a list 
    if isinstance(arr, (list, np.ndarray)):
        return arr[4]
    else:
        return np.nan