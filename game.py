import math
import os
import random
import sys
import time
import pygame as pg

WIDTH = 1000  # ゲームウィンドウの幅 25
HEIGHT = 680  # ゲームウィンドウの高さ 17
SQ_SIDE = 40  # マス一辺 
TATE = 17  # マス数
YOKO = 25
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
TYPE_DICT = {0:"floor",1:"wall",2:"block",3:"bomb"}


def check_bound(obj,map_lst:list,mv):
    """
    obj:対象のインスタンス(座標としてself.x,self.yを定義してあるもの)
    map_lst:マップ
    mv:動く距離
    """
    if map_lst[obj.x+mv[0]][obj.y+mv[1]] == 0:
        return obj.x+mv[0],obj.y+mv[1]
    else:
        return obj.x,obj.y



class Player():
    def __init__(self):
        self.x = 3
        self.y = 11
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x*SQ_SIDE,self.y*SQ_SIDE)
    
    def update(self,mv,screen: pg.Surface,map_lst):
        self.x,self.y = check_bound(self,map_lst,mv)
        self.rect.center = (self.x*SQ_SIDE,self.y*SQ_SIDE)
        screen.blit(self.img,self.rect.center)





def main():
    pg.display.set_caption("吹き飛べ！！こうかとん！！！")
    player = Player()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    wall_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/wall.png"),0, 2.5)
    map_lst = [[0 for i in range(17)] for j in range(26)]
    while True:
        screen.blit(bg_img, [0, 0])
        # 壁設置 
        for x in range(YOKO):
            for y in range(TATE):
                if x == 0 or x == YOKO-1:
                    map_lst[x][y] = 1
                elif y == 0 or y == TATE-1:
                    map_lst[x][y] = 1
                elif x%2 == 0 and y%2 == 0:
                    map_lst[x][y] = 1
                if map_lst[x][y] == 1:
                    screen.blit(wall_image,(x*SQ_SIDE,y*SQ_SIDE))
    
        key_lst = pg.key.get_pressed()
        mv = [0,0]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    mv[1] -= 1
                if event.key == pg.K_DOWN:
                    mv[1] += 1
                if event.key == pg.K_RIGHT:
                    mv[0] += 1
                if event.key == pg.K_LEFT:
                    mv[0] -= 1
            
        player.update(mv, screen,map_lst)
        pg.display.update()
        pass
    # score = Score()
    # bird = Bird(3, (900, 400))
    # bombs = pg.sprite.Group()
    # beams = pg.sprite.Group()
    # shield = pg.sprite.Group()
    # exps = pg.sprite.Group()
    # emys = pg.sprite.Group()
    # gravitys = pg.sprite.Group()
    # num = 3
    # tmr = 0
    # clock = pg.time.Clock()


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()