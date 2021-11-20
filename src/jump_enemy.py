#!/usr/bin/env python
# coding: utf-8

import pygame
from pygame.locals import *
import os
import sys
import pdb

from load_image import load_image
from enemy import Enemy

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)


class JumpEnemy(pygame.sprite.Sprite):
    """敵"""

    LEFT, INIT, RIGHT = (-1, 0, 1)  # 移動方向
    MOVE_SPEED = 2.0  # 移動速度
    JUMP_SPEED = 6.0  # ジャンプの初速度
    GRAVITY = 0.2  # 重力加速度

    def __init__(self, pos, blocks):
        pygame.sprite.Sprite.__init__(self, Enemy.containers)
        self.left_image = load_image("jump_enemy.png", -1)
        self.right_image = pygame.transform.flip(self.left_image, 1, 0)
        self.image = self.left_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定

        self.blocks = blocks
        self.direct = self.LEFT
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        self.time = 0
        self.f_newrect = 0

        # 地面にいるか
        self.on_floor = False
        self.mode = 0

    def update(self):
        if self.mode == 0:
            self.fpvy = -self.JUMP_SPEED  # 上向きに初速度を与える
            self.on_floor = False
            self.mode = 1

        elif self.mode == 1:
            if self.direct == self.LEFT:
                self.image = self.left_image
                self.fpvx = -self.MOVE_SPEED
            elif self.direct == self.RIGHT:
                self.image = self.right_image
                self.fpvx = self.MOVE_SPEED

            if self.on_floor:
                self.mode = 2

        elif self.mode == 2:
            self.fpvx = 0.0
            self.time += 1
            if self.time % 60 == 0:
                self.mode = 0
                self.time = 0

        self.fpvy += self.GRAVITY

        self.collision_x()  # X方向の衝突判定処理
        self.collision_y()  # Y方向の衝突判定処理

        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)

    def collision_x(self):
        """X方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height

        # X方向の移動先の座標と矩形を求める
        newx = self.fpx + self.fpvx
        newrect = Rect(newx, self.fpy, width, height)
        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvx > 0:  # 右に移動中に衝突
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                    self.direct = self.LEFT  # 反転

                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                    self.direct = self.RIGHT  # 反転
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

        if newy > 10000:
            self.kill()

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
                elif self.fpvy < 0:  # 上に移動中に衝突
                    self.fpy = block.rect.bottom
                    self.fpvy = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpy = newy
                # 衝突ブロックがないなら床の上にいない
                self.on_floor = False
