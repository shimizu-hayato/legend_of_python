#!/usr/bin/env python
# coding: utf-8

import os
import pdb
import sys

import pygame
from pygame.locals import *

from load_image import load_image
from map import Map

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)


class PyAction:
    def __init__(self):
        pygame.init()
        # self.time = 0

        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("Legend of Python")

        self.init_game()

        # メインループ
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()

    def init_game(self):
        """ゲームオブジェクトを初期化"""

        # ゲーム状態
        self.game_state = START

        # マップのロード
        dirname = os.path.dirname(__file__)
        filename = "../map_data/test.map"
        if not dirname:
            self.map = Map(filename)
        else:
            self.map = Map(dirname + "/" + filename)

    def update(self):
        """スプライトの更新"""
        # pdb.set_trace()
        if self.map.game_mode(self.game_state) == GAMEOVER:
            self.game_state = GAMEOVER
        self.map.update()

    def draw(self, screen):
        """スプライトの描画"""
        screen.fill((0, 0, 0))
        if self.game_state == START:
            # タイトルを描画
            title_font = pygame.font.SysFont(None, 80)
            title = title_font.render("Legend of Python", False, (255, 0, 0))
            screen.blit(title, ((SCR_RECT.width - title.get_width()) / 2, 100))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (255, 255, 255))
            screen.blit(
                push_space, ((SCR_RECT.width - push_space.get_width()) / 2, 300)
            )
        elif self.game_state == PLAY:
            self.map.draw(screen)
            # オフセットに基づいてマップの一部を画面に描画
            offsetx, offsety = self.map.calc_offset()

            # 端ではスクロールしない
            if offsetx < 0:
                offsetx = 0
            elif offsetx > self.map.width - SCR_RECT.width:
                offsetx = self.map.width - SCR_RECT.width

            if offsety < 0:
                offsety = 0
            elif offsety > self.map.height - SCR_RECT.height:
                offsety = self.map.height - SCR_RECT.height

            # マップの一部を画面に描画
            screen.blit(
                self.map.surface,
                (0, 0),
                (offsetx, offsety, SCR_RECT.width, SCR_RECT.height),
            )
        elif self.game_state == GAMEOVER:
            # GAME OVERを描画
            gameover_font = pygame.font.SysFont(None, 80)
            gameover = gameover_font.render("GAME OVER", False, (255, 0, 0))
            screen.blit(gameover, ((SCR_RECT.width - gameover.get_width()) / 2, 100))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (255, 255, 255))
            screen.blit(
                push_space, ((SCR_RECT.width - push_space.get_width()) / 2, 300)
            )

    def key_handler(self):
        """キー入力処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.game_state == START:  # スタート画面でスペースを押したとき
                    self.game_state = PLAY

                elif self.game_state == GAMEOVER:  # ゲームオーバー画面でスペースを押したとき
                    self.init_game()  # ゲームを初期化して再開
                    self.game_state = PLAY

            elif event.type == KEYDOWN and event.key == K_r:
                if self.game_state == PLAY:
                    self.init_game()  # ゲームを初期化して再開
                    self.game_state = START


if __name__ == "__main__":
    PyAction()
