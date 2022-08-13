#!/usr/bin/env python
# coding: utf-8

import pygame
from pygame.locals import *

from load_image import load_image


class MoveBlock(pygame.sprite.Sprite):
    """ブロック"""

    speed = 2  # 移動速度

    def __init__(self, pos, player, blocks):
        from map import Block

        self.image = load_image("move_block.png", -1)
        pygame.sprite.Sprite.__init__(self, Block.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.player = player
        self.frame = 0
        self.range = 8 * 32
        self.block_type = 2

    def update(self):
        if not self.player.damage:
            if self.block_type == 1:
                self.move_up()
            elif self.block_type == 2:
                self.move_flat()
        else:
            self.player.inertia_x = 0

    def move_down(self):
        if self.collision_up():
            self.frame += 1
            if self.frame > 60:
                self.rect.move_ip(0, self.speed)
                self.player.inertia_y = self.speed
        else:
            self.player.inertia_y = 0.0

    def move_up(self):
        if self.collision_up():
            self.frame += 1
            if self.frame > 60:
                self.rect.move_ip(0, -self.speed)
                # self.player.inertia_y = self.speed
        else:
            self.player.inertia_y = 0.0

    def move_flat(self):
        if self.collision_up():
            self.frame += 1
            if self.frame > 60:
                self.rect.move_ip(self.speed, 0)
                self.player.inertia_x = self.speed
                # x = self.rect.x
                # newrect = Rect(x + 1,self.rect.y,self.rect.width,self.rect.height)

        else:
            self.player.inertia_x = 0.0

    def collision_up(self):
        w = self.rect.width
        h = self.rect.height

        x = self.rect.x
        y = self.rect.y

        newrect = Rect(x, y - 1, w, h)
        collide = newrect.colliderect(self.player.rect)
        if collide and self.player.on_floor:  # 衝突するブロックあり
            return True
        else:
            return False
