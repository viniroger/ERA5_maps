#!/usr/bin/env python3.8.11
# -*- Coding: UTF-8 -*-
# Save image sequence as video

import cv2
import os
import glob

# Define type of map
fig_type = ['slpesp','uvt850','advt850','vort500','omega','uv250']
# Loop for all keys
for key in fig_type:
    print(f'PRODUCT {key}')
    pattern = f'output/{key}_*'
    images = [img for img in sorted(glob.glob(pattern), key=os.path.realpath)]
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(f'output/{key}.mp4', fourcc, 11, (width,height))
    for image in images:
        video.write(cv2.imread(image))
    video.release()
