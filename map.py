#!/usr/bin/env python
#coding: utf-8

import pygame
from pygame.locals import *
import os
import sys
import pdb

from python import Python
from enemy import Enemy
from jump_enemy import JumpEnemy
from fire_enemy import FireEnemy
from fire_enemy import Fire
from electric_enemy import ElectricEnemy
from electric_enemy import Electric
from drop_block import DropBlock

from load_image import load_image


START, PLAY, GAMEOVER = (0, 1, 2) 
SCR_RECT = Rect(0, 0, 640, 480)


class Map:
    """マップ（プレイヤーや内部のスプライトを含む）"""
    GS = 32  # グリッドサイズ
    
    def __init__(self, filename):

        # スプライトグループの登録
        self.game_state = PLAY
        # マップをロードしてマップ内スプライトの作成

        self.all = pygame.sprite.RenderUpdates()
        self.player = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.thorns = pygame.sprite.Group()
        self.enemys = pygame.sprite.Group()
        self.fires  = pygame.sprite.Group()
        self.electrics   = pygame.sprite.Group()
        self.drop_blocks = pygame.sprite.Group()

        Block.containers = self.all, self.blocks
        Thorn.containers = self.all, self.thorns
        Enemy.containers = self.all, self.enemys
        Fire.containers  = self.all, self.fires
        Electric.containers = self.all, self.electrics
        Python.containers = self.all, self.player

        self.load(filename)
        
        # マップサーフェイスを作成
        self.surface = pygame.Surface((self.col*self.GS, self.row*self.GS)).convert()
        
    def draw(self, screen):
        """マップサーフェイスにマップ内スプライトを描画"""
        self.surface.fill((0,0,0))
        self.all.draw(self.surface)
    
    def update(self):
        """マップ内スプライトを更新"""
        self.all.update()

    def game_mode(self,game_state):
        #self.python_sp = Python.containers[1].sprites()[0]
        if self.python.game_state == GAMEOVER:
            self.game_state = self.python.game_state
            
        return self.game_state
    
    def calc_offset(self):
        """オフセットを計算"""
        offsetx = self.python.rect.topleft[0] - SCR_RECT.width/2
        offsety = self.python.rect.topleft[1] - SCR_RECT.height/2
        return offsetx, offsety

    def load(self, filename):
        """マップをロードしてスプライトを作成"""
        map = []
        fp = open(filename, "r")
        for line in fp:
            line = line.rstrip()  # 改行除去
            map.append(list(line))
            self.row = len(map)
            self.col = len(map[0])
        self.width = self.col * self.GS
        self.height = self.row * self.GS
        fp.close()
        self.map_size = (self.width,self.height)
        
        # マップからスプライトを作成
        for i in range(self.row):
            for j in range(self.col):
                if map[i][j] == 'B':
                    Block((j*self.GS, i*self.GS))  # ブロック
                if map[i][j] == 'U':
                    Thorn((j*self.GS, i*self.GS),0)  # トゲ
                if map[i][j] == 'R':
                    Thorn((j*self.GS, i*self.GS),1)  # トゲ
                if map[i][j] == 'L':
                    Thorn((j*self.GS, i*self.GS),2)  # トゲ
                if map[i][j] == 'D':
                    Thorn((j*self.GS, i*self.GS),3)  # トゲ
                
        for i in range(self.row):
            for j in range(self.col):
                if map[i][j] == 'P':
                    self.python = Python((j*self.GS, i*self.GS), 
                                          self.blocks, 
                                          self.thorns,
                                          self.enemys,
                                          self.fires,
                                          self.electrics,
                                          self.map_size)
                    break

        for i in range(self.row):
            for j in range(self.col):            
                if map[i][j] == 'E':
                    Enemy((j*self.GS, i*self.GS),self.blocks,self.python)
                if map[i][j] == 'J':
                    JumpEnemy((j*self.GS, i*self.GS),self.blocks)
                if map[i][j] == 'F':
                    FireEnemy((j*self.GS, i*self.GS),self.blocks,self.python)
                if map[i][j] == 'Y':
                    ElectricEnemy((j*self.GS, i*self.GS),self.blocks,self.python)
                if map[i][j] == 'C':
                    DropBlock((j*self.GS, i*self.GS),self.python,self.blocks)

class Block(pygame.sprite.Sprite):
    """ブロック"""
    NORMAL, DROP = (0,1)
    def __init__(self, pos):
        self.image = load_image("block.png", -1)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.block_type = 0

    def collision_up(self):
        return False

class Thorn(pygame.sprite.Sprite):
    """トゲ"""
    U,R,L,D = (0,1,2,3)
    def __init__(self, pos, direction):
        if direction == self.U:
            self.image = load_image("thorn_u.png", -1)
        elif direction == self.R:
            self.image = load_image("thorn_r.png", -1)
        elif direction == self.L:
            self.image = load_image("thorn_l.png", -1)
        elif direction == self.D:
            self.image = load_image("thorn_d.png", -1)

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption("mapテスト")
    Map("data/test.map")

