import cv2
import numpy as np
from sklearn.cluster import KMeans
from random import randrange

import sys
import pickle
import time

#Image Pre-processing
def grey(img):
    img=np.asarray(img)
    return cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

def gauss(img, blur_param):
    return cv2.GaussianBlur(img,(blur_param,blur_param),0)

def blur(img):
    return cv2.blur(img,(15,15))

def preprocess_img(img):
    #blur_img = blur(grey_img)
    gauss_img = gauss(myimage, 27)
    myedges = canny(gauss_img)
    
    height, width = myimage.shape
    rectangle = np.array([[0, height//9], [width, height//9], [width, height], [0, height]])
    myedges = region_mask(myedges, rectangle)                              # masked region of interest image

    return myedges


#Canny edge detection
def canny(img):
    edges = cv2.Canny(img,20,50)
    return edges

def region_mask(img, endpoints):                                    # endpoints = np.array of polynomial's endpoints
    height, width = img.shape

    mask = cv2.fillPoly(np.zeros_like(img), pts=[endpoints], color=255)         # ORDER OF ENDPOINTS MATTER
    #cv2.imshow('region_mask', mask)
    #cv2.waitKey()
    mask = cv2.bitwise_and(img, mask)
    return mask

def lines(img):
    return cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=5, minLineLength=20,maxLineGap=10)
    #return cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=50, minLineLength=10, maxLineGap=10)


#Clustering Approach
def clip(num, boundary):
   if num < 0: return 0
   elif num > boundary: return boundary-1
   return num

def cluster_lanes(width, height, lines_matrix, gap_distance):
   edge_coordinates = []
   if (num_edges:=lines_matrix.shape[0]) > 200: num_edges = 200

   for x1,y1,x2,y2 in lines_matrix[:num_edges,0,:]:
      edge_coordinates.append([clip(randrange(x1-gap_distance,x1+gap_distance), width), clip(randrange(y1-gap_distance,y1+gap_distance), height)])                                                  # gap_distance = estimated # of pixels (horizontally) between a lane's inner and outer edges
      edge_coordinates.append([clip(randrange(x2-gap_distance,x2+gap_distance), width), clip(randrange(y2-gap_distance,y2+gap_distance), height)])

   return edge_coordinates, KMeans(n_clusters=2, init=np.array([[width//4, height//2], [3*width//4, height//2]]), n_init=1).fit_predict(np.array(edge_coordinates))

def separate_lanes(edge_coordinates, labels):                                                                                    # assumes labels = list of 0's and 1's
   lane_one_coords, lane_two_coords = [], []
   for i in range(len(labels)):
      if(labels[i] == 0): lane_one_coords.append(edge_coordinates[i])
      else: lane_two_coords.append(edge_coordinates[i])
   return np.array(lane_one_coords), np.array(lane_two_coords)

def curve_func(y, a, b, c):
   return a*y**2 + b*y + c

def get_curve_coordinates(min_y, max_y, coeffs):                                                                                 # functions assume form x = _____ because parabolas need to open up sideways in x-axis direction
   coeffs = [round(coeff, 5) for coeff in coeffs]                                                                                # careful with rounding, rounding too small may cause large changes depending on img size
   return (y_coords:=[i for i in range(min_y, max_y)]), [curve_func(y, coeffs[0], coeffs[1], coeffs[2]) for y in y_coords]       # y, x coordinates of fitted line

def get_center_curve(lane_one_coeffs, lane_two_coeffs, lane_one_y, lane_two_y):
   lane_one_y_min, lane_one_y_max, lane_two_y_min, lane_two_y_max = min(lane_one_y), max(lane_one_y), min(lane_two_y), max(lane_two_y)
   center_y_min, center_y_max = max(lane_one_y_min, lane_two_y_min), min(lane_one_y_max, lane_two_y_max)
   return (y_coords:=[i for i in range(center_y_min, center_y_max)]), [int((curve_func(y, lane_one_coeffs[0], lane_one_coeffs[1], lane_one_coeffs[2]) + curve_func(y, lane_two_coeffs[0], lane_two_coeffs[1], lane_two_coeffs[2])) // 2) for y in y_coords]

def plot_all_lanes(edge_coordinates, labels, lane_one_y, lane_two_y, lane_one_coeffs, lane_two_coeffs):
   curve1y, curve1x = get_curve_coordinates(min(lane_one_y), max(lane_one_y), lane_one_coeffs)
   curve2y, curve2x = get_curve_coordinates(min(lane_two_y), max(lane_two_y), lane_two_coeffs)
   center_curve_y, center_curve_x = get_center_curve(lane_one_coeffs, lane_two_coeffs, lane_one_y, lane_two_y)

   plt.scatter(curve1x, curve1y)
   plt.scatter(curve2x, curve2y)
   plt.scatter(center_curve_x, center_curve_y)
   plt.scatter(np.array(edge_coordinates)[:,0], np.array(edge_coordinates)[:,1], c=labels, s=20, cmap='viridis')
   #cv2.waitKey()

def get_center_lane(img, lines_matrix, lane_gap_distance):
   height, width = img.shape
   edge_coordinates, labels = cluster_lanes(width, height, lines_matrix, lane_gap_distance)

   lane_one_coords, lane_two_coords = separate_lanes(edge_coordinates, labels)

   lane_one_coeffs = np.polyfit((lane_one_y:=lane_one_coords[:,1]), lane_one_coords[:,0], 2)
   lane_two_coeffs = np.polyfit((lane_two_y:=lane_two_coords[:,1]), lane_two_coords[:,0], 2)

   #plot_all_lanes(edge_coordinates, labels, lane_one_y, lane_two_y, lane_one_coeffs, lane_two_coeffs)

   return edge_coordinates, get_center_curve(lane_one_coeffs, lane_two_coeffs, lane_one_y, lane_two_y)


#Displaying the img
def display_img(img, edge_coordinates, curve_coords):                                 # edge_coordinates = [ [x1,y1], [x2,y2], ..., [xn, yn] ] <list of list of ints>, curve_coords = ( [y_coords], [x_coords] ) <tuple of lists of ints for y and doubles for x>
   img_matrix = np.zeros(img.shape + (3,))

   for coord in edge_coordinates: img_matrix[coord[1]-2:coord[1]+2, coord[0]-2:coord[0]+2] = 255 

   center_y, center_x = curve_coords
   for i in range(len(center_x)): img_matrix[center_y[i]-1:center_y[i]+1, round(center_x[i])-1:round(center_x[i])+1] = 255 

   cv2.imshow('img_matrix', img_matrix)
   cv2.waitKey()

start = time.perf_counter()
savefile = open(sys.argv[1], 'rb')
myimage = pickle.load(savefile)
#cv2.imshow('myimage', myimage)
#cv2.waitKey()

hough_edges = lines(preprocess_img(myimage))

edge_coordinates, center_coords = get_center_lane(myimage, hough_edges, 5)
end = time.perf_counter()
print(f"Time taken: {end-start}")
#display_img(myimage, edge_coordinates, center_coords) 
