#!/usr/bin/env python
# coding: utf-8

import cv2

WIDTH = 32
HEIGHT = 32


def python_coloer_change():
    img = cv2.imread("data/block.png", -1)

    for x in range(HEIGHT):
        for y in range(WIDTH):
            b, g, r = img[x, y]
            img[x, y] = b, g, 0

    cv2.imwrite("data/drop_block.png", img)


def python_white_change():
    img = cv2.imread("data/python.png", -1)
    for x in range(HEIGHT):
        for y in range(WIDTH):
            b, g, r, a = img[x, y]
            if g < b and r < b:
                img[x, y] = 255, 255, 255, a
    cv2.imwrite("data/damage.png", img)


def python_resize():
    img = cv2.imread("data/Python.png", -1)
    orgHeight, orgWidth = img.shape[:2]
    halfImg = cv2.resize(img, (int(orgHeight * 0.8), int(orgWidth * 0.8)))
    cv2.imwrite("data/half.png", halfImg)


if __name__ == "__main__":
    python_coloer_change()
    # python_white_change()
    # python_resize()
