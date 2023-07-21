import pickle
import cv2
import numpy as np

savefile = open('greyscale_yplane_img.pkl', 'rb')
yplane_arr = pickle.load(savefile)          #already grayscaled
#cv2.imshow('y', yplane_arr)
#cv2.waitKey()

def gaussian_blur(img): return cv2.GaussianBlur(img,(19, 19),0)

def median_blur(img): return cv2.medianBlur(img, 15)

def canny_edge_detect(img): return cv2.Canny(img,50,150)


def region_mask(img):
    height, width = img.shape
    min_height, max_height, min_width, max_width = 0, 0, 0, 0
    triangle = np.array([[(0, height//2), (width//2, 0), (width, height//2)]])

    mask = np.zeros_like(img)
    mask = cv2.fillPoly(mask, triangle, 255)
    mask = cv2.bitwise_and(img, mask)
    return mask


def find_line_formulas(img):
    edges = canny_edge_detect(gaussian_blur(yplane_arr))
    #print(edges.shape)
    #cv2.imshow('edges', edges)
    #cv2.waitKey()

    region_of_interest = region_mask(edges)
    #print(region_of_interest.shape)
    #cv2.imshow('roi', region_of_interest)
    #cv2.waitKey()

    lines  = cv2.HoughLinesP(region_of_interest, rho=2, theta=np.pi/180, threshold=100, np.array([]), minLineLength=40, maxLineGap=5)

    print(lines)
    print(type(lines))

find_line_formulas(yplane_arr)
