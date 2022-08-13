#!/usr/bin/env python
# coding: utf-8


import os
import sys

import pygame
from pygame.locals import *

from load_image import load_image

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)


class Enemy(pygame.sprite.Sprite):
    """敵"""

    LEFT, STOP, RIGHT = (-1, 0, 1)  # 移動方向
    MOVE_SPEED = 1.0  # 移動速度
    JUMP_SPEED = 6.0  # ジャンプの初速度
    GRAVITY = 0.2  # 重力加速度

    def __init__(self, pos, blocks, player):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.left_image = load_image("enemy.png", -1)
        self.right_image = pygame.transform.flip(self.left_image, 1, 0)
        self.image = self.left_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定

        self.blocks = blocks
        self.player = player
        self.mode = self.LEFT
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        self.f_newrect = 0

        # 地面にいるか
        self.on_floor = False

    def update(self):
        if self.offset_start():
            if self.mode == self.LEFT:
                self.image = self.left_image
                self.fpvx = -self.MOVE_SPEED
            elif self.mode == self.RIGHT:
                self.image = self.right_image
                self.fpvx = self.MOVE_SPEED
        else:
            self.offset_start()
            self.fpvx = 0.0
            self.fpvy = 0.0

        if not self.on_floor:
            self.fpvy += self.GRAVITY

        self.collision_x()  # X方向の衝突判定処理
        self.collision_y()  # Y方向の衝突判定処理
        if self.front_collision_y():
            if self.mode == self.LEFT:
                self.mode = self.RIGHT
            else:
                self.mode = self.LEFT

        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)

    def collision_x(self):
        """X方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width - 1
        height = self.rect.height

        # X方向の移動先の座標と矩形を求める
        newx = self.fpx + self.fpvx
        newrect = Rect(newx, self.fpy, width, height)
        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvx > 0:  # 右に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                    self.mode = self.LEFT  # 反転

                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                    self.mode = self.RIGHT  # 反転
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpx = newx

    def collision_y(self):
        """Y方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width - 1
        height = self.rect.height

        # Y方向の移動先の座標と矩形を求める
        newy = self.fpy + self.fpvy
        newrect = Rect(self.fpx, newy, width, height)

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvy > 0:  # 下に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpy = block.rect.top - height
                    self.fpvy = 0
                    # 下に移動中に衝突したなら床の上にいる
                    self.on_floor = True
                    self.jump_count = 0  # ジャンプカウントをリセット
                elif self.fpvy < 0:  # 上に移動中に衝突
                    self.fpy = block.rect.bottom
                    self.fpvy = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpy = newy
                # 衝突ブロックがないなら床の上にいない
                self.on_floor = False

        if newy > 10000:
            self.kill()

    def front_collision_y(self):
        if self.on_floor and self.fpvy == 0:
            newy = self.fpy + self.fpvy
            newx = self.fpx + self.fpvx
            width = self.rect.width - 1
            height = self.rect.height

            if self.mode == self.LEFT:
                self.f_newrect = Rect(newx - width, newy + height, width, height)
            else:
                self.f_newrect = Rect(newx + width, newy + height, width, height)

            # pdb.set_trace()

            for block in self.blocks:
                f_collide = self.f_newrect.colliderect(block.rect)
                if f_collide:
                    return False

            return True
        else:
            return False

    def offset_start(self):
        offsetx, offsety = self.player.calc_offset()
        screen_rect = Rect(
            offsetx, offsety, offsetx + SCR_RECT.width, offsety + SCR_RECT.height
        )
        if screen_rect.colliderect(self.rect):
            return True
        else:
            return False
