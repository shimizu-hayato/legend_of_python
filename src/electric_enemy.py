#!/usr/bin/env python
# coding: utf-8

import math
import os
import pdb
import sys

import pygame
from pygame.locals import *

from enemy import Enemy
from load_image import load_image

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)


class ElectricEnemy(pygame.sprite.Sprite):
    """敵"""

    LEFT, INIT, RIGHT = (-1, 0, 1)  # 移動方向
    MOVE_SPEED = 1.0  # 移動速度
    JUMP_SPEED = 7.0  # ジャンプの初速度
    GRAVITY = 0.2  # 重力加速度

    def __init__(self, pos, blocks, python):
        pygame.sprite.Sprite.__init__(self, Enemy.containers)
        self.left_image = load_image("electric_enemy.png", -1)
        self.right_image = pygame.transform.flip(self.left_image, 1, 0)

        self.image = self.left_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定

        self.blocks = blocks
        self.python = python
        self.direct = self.LEFT
        self.mode = 0
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        self.time = 0

        self.f_newrect = 0

        # 地面にいるか
        self.on_floor = False

    def update(self):
        if self.rect.x < self.python.rect.x:
            self.image = self.right_image
            self.direct = self.RIGHT
        else:
            self.image = self.left_image
            self.direct = self.LEFT
        if self._start():
            if self.mode == 0:
                self.fpvy = -self.JUMP_SPEED  # 上向きに初速度を与える
                self.on_floor = False
                self.mode = 1

            elif self.mode == 1 and self.fpvy > 0:
                self.mode = 2

            elif self.mode == 2:
                Electric(
                    self.rect.topleft, self.python.rect.topleft, self.blocks, self.direct
                )
                self.mode = 3
            elif self.mode == 3:
                self.time += 1
                if self.time % 120 == 0:
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
                    # めり込まないように調整して速度を0に
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
        width = self.rect.width
        height = self.rect.height

        # Y方向の移動先の座標と矩形を求める
        newy = self.fpy + self.fpvy
        newrect = Rect(self.fpx, newy, width, height)

        if newy > 1000:
            self.kill()

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvy >= 0:  # 下に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpy = block.rect.top - height + 1
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

    def _start(self):
        # playerが画面内に入ったか確認
        offsetx, offsety = self.python.calc_offset()
        screen_rect = Rect(
            offsetx, offsety, offsetx + SCR_RECT.width, offsety + SCR_RECT.height
        )
        print(self.rect)
        print(screen_rect)
        if screen_rect.colliderect(self.rect):
            return True
        else:
            return False

class Electric(pygame.sprite.Sprite):
    speed = 6  # 移動速度
    LEFT, INIT, RIGHT = (-1, 0, 1)  # 移動方向

    def __init__(self, pos, python_pos, blocks, mode):
        # imagesとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.left_yellow_image = load_image("electric_white.png", -1)
        self.left_red_image = load_image("electric_blue.png", -1)
        self.right_yellow_image = pygame.transform.flip(self.left_yellow_image, 1, 0)
        self.right_red_image = pygame.transform.flip(self.left_red_image, 1, 0)

        self.image = self.left_yellow_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.python_pos = python_pos
        # self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定
        self.blocks = blocks
        self.direct = mode
        self.vector = self.unit_vector()
        self.frame = 0

    def update(self):
        # 傾きを求める
        if self.frame % 10 > 5:
            self.image = self.right_yellow_image
        else:
            self.image = self.right_red_image
        self.rect.move_ip(
            self.vector[0] * self.speed, self.vector[1] * self.speed
        )  # 敵へ発射

        self.collision()
        self.frame += 1

    # 単位ベクトルを求める
    def unit_vector(self):
        enemy_x = self.rect.x
        enemy_y = self.rect.y
        python_x = self.python_pos[0]
        python_y = self.python_pos[1]
        vec = (python_x - enemy_x, python_y - enemy_y)
        scala = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        return (vec[0] / scala, vec[1] / scala)

    def collision(self):
        if pygame.sprite.spritecollideany(self, self.blocks):
            self.kill()
            self.frame = 0
