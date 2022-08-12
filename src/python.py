#!/usr/bin/env python
# coding: utf-8


import os
import pdb
import sys

import pygame
from pygame.locals import *

from load_image import load_image

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)


class Python(pygame.sprite.Sprite):
    """プレイヤー"""

    MOVE_SPEED = 2.5  # 移動速度
    JUMP_SPEED = 6.0  # ジャンプの初速度
    GRAVITY = 0.2  # 重力加速度
    MAX_JUMP_COUNT = 2  # ジャンプ段数の回数

    def __init__(self, pos, blocks, thorns, enemys, fires, electrics, map_size):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.left_image = load_image("half.png", -1)
        self.right_image = pygame.transform.flip(self.left_image, 1, 0)
        self.image = self.right_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定
        self.blocks = blocks  # 衝突判定用
        self.thorns = thorns  # ダメージ判定用
        self.enemys = enemys
        self.fires = fires
        self.electrics = electrics

        self.damage_point = 0
        self.time = 0
        self.map_size = map_size
        self.fall = map_size[1] + self.rect.width * 10

        # ジャンプ回数
        self.jump_count = self.MAX_JUMP_COUNT
        self.prev_button = 1

        # 浮動小数点の位置と速度
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        self.inertia_x = 0.0
        self.inertia_y = 0.0

        self.block_hit = 0

        self.game_state = START

        # 地面にいるか？
        self.on_floor = False
        self.damage = False
        self.start = True

    def update(self):
        """スプライトの更新"""
        if self.damage:
            self.time += 1
            delay = 10
            if self.time > delay:
                if self.time % 4 == 0:
                    self.image = pygame.transform.rotate(self.image, 90)
                t = self.time - delay
                y = (
                    self.damage_point
                    - self.JUMP_SPEED * t
                    + 1 / 2 * self.GRAVITY * (t ** 2)
                )
            else:
                y = self.rect.y
            self.rect.x = int(self.fpx)
            self.rect.y = int(y)
            if y > self.map_size[1] + 200:
                self.game_state = GAMEOVER
                self.kill()

        elif self.start:
            self.time += 1
            if self.time > 30:
                self.start = False
                self.time = 0
            self.fpvy += self.GRAVITY  # 下向きに重力をかける
            self.collision_x()  # X方向の衝突判定処理
            self.collision_y()  # Y方向の衝突判定処理
            self.rect.x = self.fpx
            self.rect.y = self.fpy
        else:
            # キー入力取得
            pressed_keys = pygame.key.get_pressed()
            # 左右移動
            if pressed_keys[K_RIGHT]:
                self.image = self.right_image
                self.fpvx = self.MOVE_SPEED
            elif pressed_keys[K_LEFT]:
                self.image = self.left_image
                self.fpvx = -self.MOVE_SPEED
            else:
                self.fpvx = 0.0

            # ジャンプ
            if pressed_keys[K_SPACE]:
                if self.on_floor:
                    self.fpvy = -self.JUMP_SPEED  # 上向きに初速度を与える
                    # self.on_floor = False
                    self.jump_count = 1
                elif not self.prev_button and self.jump_count < self.MAX_JUMP_COUNT:
                    self.fpvy = -self.JUMP_SPEED
                    self.jump_count += 1

            # 速度を更新
            # if not self.on_floor:
            self.fpvy += self.GRAVITY  # 下向きに重力をかける

            self.collision_x()  # X方向の衝突判定処理
            self.collision_y()  # Y方向の衝突判定処理

            # print(self.on_floor)

            self.collision_thorn()
            self.collision_enemy()
            self.collision_fall()

            # 浮動小数点の位置を整数座標に戻す
            # スプライトを動かすにはself.rectの更新が必要！

            self.rect.x = self.fpx
            self.rect.y = self.fpy

            self.python_on_floor()

            # ボタンのジャンプキーの状態を記録
            self.prev_button = pressed_keys[K_SPACE]

    def collision_x(self):
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height

        # X方向の移動先の座標と矩形を求める
        newx = self.fpx + self.fpvx + self.inertia_x
        newrect = Rect(newx, self.fpy, width, height)

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if block.collision_up():
                    continue
                if self.fpvx > 0:  # 右に移動中に衝突
                    # めり込まないように調整して速度を0に
                    # pdb.set_trace()
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                break  # 衝突ブロックは1個調べれば十分
        else:
            # 衝突ブロックがない場合、位置を更新
            self.fpx = newx

    def collision_y(self):
        # パイソンのサイズ
        width = self.rect.width
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
                    # self.on_floor = True
                    self.jump_count = 0  # ジャンプカウントをリセット
                elif self.fpvy < 0:  # 上に移動中に衝突
                    self.fpy = block.rect.bottom
                    self.fpvy = 0
                    # self.on_floor = False
                break  # 衝突ブロックは1個調べれば十分
        else:
            # self.on_floor = False
            # 衝突ブロックがない場合、位置を更新
            self.fpy = newy

    def collision_thorn(self):
        if pygame.sprite.spritecollideany(self, self.thorns):
            self.python_die()

    def collision_enemy(self):
        if pygame.sprite.spritecollideany(self, self.enemys):
            self.python_die()

        if pygame.sprite.spritecollideany(self, self.fires):
            self.python_die()

        if pygame.sprite.spritecollideany(self, self.electrics):
            self.python_die()

    def collision_fall(self):
        # Y方向の移動先の座標と矩形を求める
        newy = self.fpy + self.fpvy
        # pdb.set_trace()
        if newy > self.fall:
            self.time += 1
            if self.time > 60:
                self.game_state = GAMEOVER
                self.kill()

    def python_on_floor(self):
        w = self.rect.width
        h = self.rect.height

        newrect = Rect(self.fpx, self.fpy + 1, w, h)

        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:
                self.on_floor = True
                if block.block_type == 1:
                    self.press_check()
                break
        else:
            self.on_floor = False

    def press_check(self):
        w = self.rect.width
        h = self.rect.height

        uprect = Rect(self.fpx, self.fpy - 1, w, h)
        for block in self.blocks:
            collide = uprect.colliderect(block.rect)
            if collide:
                self.python_die()

    def python_die(self):
        self.damage = True
        if not self.damage_point:
            self.damage_point = self.rect.y

    def calc_offset(self):
        offsetx = self.rect.topleft[0] - SCR_RECT.width / 2
        offsety = self.rect.topleft[1] - SCR_RECT.height / 2

        # 端ではスクロールしない
        if offsetx < 0:
            offsetx = 0
        elif offsetx > self.map_size[0] - SCR_RECT.width:
            offsetx = self.map_size[0] - SCR_RECT.width

        if offsety < 0:
            offsety = 0
        elif offsety > self.map_size[1] - SCR_RECT.height:
            offsety = self.map_size[1] - SCR_RECT.height
        return offsetx, offsety
