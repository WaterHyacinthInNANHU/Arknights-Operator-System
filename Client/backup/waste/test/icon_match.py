import numpy as np
import cv2
from matplotlib import pyplot as plt
from sklearn.cluster import OPTICS, DBSCAN
from itertools import combinations
from math import sqrt, pow


def get_distances(pts):
    comb = list(combinations(pts, 2))
    res = [np.linalg.norm(x-y) for x, y in comb]
    res = sorted(res)
    return res


def matches2array(match, keypoints):
    pts = np.zeros((len(match), 2))
    for i, gm_ in enumerate(match):
        pts[i][0] = keypoints[gm_.trainIdx].pt[0]
        pts[i][1] = keypoints[gm_.trainIdx].pt[1]
    return pts


MIN_MATCH_COUNT = 5
DBSCAN_EPS = 50

# Read the query resource as query_img
# and traing resource This query resource
# is what you need to find in train resource
# Save it in the same directory
# with the name resource.jpg
query_img = cv2.imread('imgs/template2.png')
train_img = cv2.imread('imgs/target.png')

# Convert it to grayscale
query_img_bw = cv2.cvtColor(query_img, cv2.COLOR_BGR2GRAY)
train_img_bw = cv2.cvtColor(train_img, cv2.COLOR_BGR2GRAY)

# Initialize the ORB detector algorithm
orb = cv2.ORB_create(1000)

# Now detect the keypoints and compute
# the descriptors for the query resource
# and train resource
queryKeypoints, queryDescriptors = orb.detectAndCompute(query_img_bw, None)
trainKeypoints, trainDescriptors = orb.detectAndCompute(train_img_bw, None)


# # Initiate SIFT detector
# sift = cv2.SIFT_create()
# # find the keypoints and descriptors with SIFT
# queryKeypoints, queryDescriptors = sift.detectAndCompute(query_img_bw,None)
# trainKeypoints, trainDescriptors = sift.detectAndCompute(train_img_bw,None)

# Initialize the Matcher for matching
# the keypoints and then match the
# keypoints

FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

queryDescriptors = np.float32(queryDescriptors)
trainDescriptors = np.float32(trainDescriptors)

matches = flann.knnMatch(queryDescriptors, trainDescriptors, k=2)

# Sort them in the order of their distance.
matches = sorted(matches, key=lambda x: x[0].distance)

# check if there are enough matches
good_matches = []
for m, n in matches:
    if m.distance < 0.7*n.distance:
        good_matches.append(m)
print(str(len(good_matches)) + " matches")

# dist = get_distances(pts)

# check if matching is succeed
pt_avg = None
if len(good_matches) < MIN_MATCH_COUNT:
    print("not enough matches are present!")
else:
    print("matching succeed!")
    # find outlier via DBSCAN
    # references:
    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
    # https://stackoverflow.com/questions/12893492/choosing-eps-and-minpts-for-dbscan-r
    pts = matches2array(good_matches, trainKeypoints)
    model = DBSCAN(eps=DBSCAN_EPS, min_samples=MIN_MATCH_COUNT).fit(pts)
    # remove outlier
    good_matches = [good_matches[i] for i in range(0, len(good_matches)) if model.labels_[i] != -1]
    # regenerate pts
    pts = matches2array(good_matches, trainKeypoints)
    pt_avg = pts.mean(axis=0)
    # calculate target's position
    print('target location is ' + str(pt_avg))

# draw the matches to the final resource
final_img = cv2.drawMatches(query_img, queryKeypoints,
                            train_img, trainKeypoints, good_matches, None)

# draw a marker at the estimated position
color = (0, 255, 0)     # Green color in BGR
thickness = -1  # Thickness of -1 will fill the entire shape
if len(good_matches) >= MIN_MATCH_COUNT:
    pos_img = cv2.rectangle(train_img, (int(pt_avg[0]), int(pt_avg[1])), (int(pt_avg[0]) + 20, int(pt_avg[1]) + 20),
                            color, thickness)

# plot
plt.subplot(211), plt.imshow(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB))
plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
if len(good_matches) >= MIN_MATCH_COUNT:
    plt.subplot(212), plt.imshow(cv2.cvtColor(pos_img, cv2.COLOR_BGR2RGB))
    plt.title('Position'), plt.xticks([]), plt.yticks([])
plt.show()
