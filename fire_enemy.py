#!/usr/bin/env python
#coding: utf-8

import pygame
from pygame.locals import *
import os
import sys
import pdb

from load_image import load_image
from enemy import Enemy

START, PLAY, GAMEOVER = (0, 1, 2) 
SCR_RECT = Rect(0, 0, 640, 480)

class FireEnemy(pygame.sprite.Sprite):
    """敵"""
    LEFT,INIT,RIGHT = (-1,0, 1) # 移動方向
    MOVE_SPEED = 1.0            # 移動速度
    JUMP_SPEED = 6.0            # ジャンプの初速度
    GRAVITY = 0.2               # 重力加速度

    def __init__(self, pos, blocks, python):
        pygame.sprite.Sprite.__init__(self, Enemy.containers)
        self.left_image = load_image("fire_enemy.png", -1)
        self.right_image = pygame.transform.flip(self.left_image, 1, 0)

        #self.fire_left_image = load_image("fire.png", -1)
        #self.fire_right_image = pygame.transform.flip(self.fire_left_image, 1, 0)

        self.image = self.left_image
        #self.fire_image = self.fire_left_image

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定

        self.blocks = blocks
        self.python = python
        self.mode = self.LEFT
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        self.time = 0

        self.f_newrect = 0

        #地面にいるか
        self.on_floor = False

    def update(self):
        if self.offset_start():
            if self.rect.x < self.python.rect.x:
                self.image = self.right_image
                self.mode = self.RIGHT
            else:
                self.image = self.left_image
                self.mode = self.LEFT

            # 3秒に1度火を吹く
            if self.time % 180 == 0:
                Fire(self.rect.topleft,self.blocks,self.mode)

            self.time += 1
        else:
            self.time = 0

        self.collision_x()  # X方向の衝突判定処理
        self.collision_y()  # Y方向の衝突判定処理

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
                if self.fpvx > 0:    # 右に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                    self.mode = self.LEFT #反転

                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                    self.mode = self.RIGHT # 反転
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
                if self.fpvy > 0:    # 下に移動中に衝突
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

        if newy > 1000:
            self.kill()

    def offset_start(self):
        offsetx,offsety = self.python.calc_offset()
        screen_rect = Rect(offsetx,offsety,offsetx + SCR_RECT.width,offsety + SCR_RECT.height)
        if screen_rect.colliderect(self.rect):
            return True
        else:
            return False



class Fire(pygame.sprite.Sprite):
    speed = 4  # 移動速度
    LEFT,INIT,RIGHT = (-1,0, 1) # 移動方向
    def __init__(self, pos, blocks, mode):
        # imagesとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.left_yellow_image = load_image("yellow_fire.png", -1)
        self.left_red_image = load_image("red_fire.png", -1)
        self.right_yellow_image = pygame.transform.flip(self.left_yellow_image, 1, 0)
        self.right_red_image = pygame.transform.flip(self.left_red_image, 1, 0)

        self.image = self.left_yellow_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        #self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定
        self.blocks = blocks
        self.mode = mode
        self.frame = 0

    def update(self):
        if self.mode == self.RIGHT:
            if self.frame % 10 > 5:
                self.image = self.right_yellow_image
            else:
                self.image = self.right_red_image
            self.rect.move_ip(self.speed, 0)  # 左へ発射
        else:
            if self.frame % 10 > 5:
                self.image = self.left_yellow_image
            else:
                self.image = self.left_red_image
            #self.image = self.left_yellow_image
            self.rect.move_ip(-self.speed, 0)  # 右へ発射
        self.collision()
        self.frame += 1
        

    def collision(self):
        if pygame.sprite.spritecollideany(self,self.blocks):
            self.kill()
            self.frame = 0





