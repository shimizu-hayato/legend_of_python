#!/usr/bin/env python
# coding: utf-8

import pygame
from pygame.locals import *
import os
import sys
import pdb

from map import Map
from load_image import load_image

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)


def calc_offset(python):
    offsetx = self.python.rect.topleft[0] - SCR_RECT.width / 2
    offsety = self.python.rect.topleft[1] - SCR_RECT.height / 2

    # 端ではスクロールしない
    if offsetx < 0:
        offsetx = 0
    elif offsetx > self.map.width - SCR_RECT.width:
        offsetx = self.map.width - SCR_RECT.width

    if offsety < 0:
        offsety = 0
    elif offsety > self.map.height - SCR_RECT.height:
        offsety = self.map.height - SCR_RECT.height
