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
    

# class Bomb():
#     def __init__(self):
#         self.x = 3
#         self.y = 11
#         self.power = 2

    


def judgement(bomb, map_lst:list):
    """
    bomb:爆弾
    map_lst:

    引数:接触判定したいbombクラス
    返値:内容を変更したmap_lst
    """
    for i in range(1, bomb.power + 1):  # 上側の判定
        if map_lst[bomb.x][bomb.y - i] == 1:  # 壁と接触していたら,その時点で終了
            break
        elif map_lst[bomb.x][bomb.y - i] == 2:  # blockと接触したら
            print("yobidasareta")
            map_lst[bomb.x][bomb.y - i] = 0    #blockを消す

    for i in range( 1, bomb.power + 1):  # 下側の判定
        if map_lst[bomb.x][bomb.y + i] == 1:
            break
        elif map_lst[bomb.x][bomb.y + i] == 2:
            map_lst[bomb.x][bomb.y + i] = 0

    for i in range( 1, bomb.power + 1):  # 右側の判定
        if map_lst[bomb.x + i][bomb.y] == 1:
            break
        elif map_lst[bomb.x + i][bomb.y] == 2:
            map_lst[bomb.x + i][bomb.y] = 0

    for i in range( 1, bomb.power + 1):  # 左側の判定
        if map_lst[bomb.x - i][bomb.y] == 1:
            break
        elif map_lst[bomb.x - i][bomb.y] == 2:
            map_lst[bomb.x - i][bomb.y] = 0
    
    return map_lst
    

class Player():

    hyper_life = 0  # 発動時間
    hyper_count = 1 # 発動回数

    def __init__(self):
        self.x = 3
        self.y = 11
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x*SQ_SIDE,self.y*SQ_SIDE)
    
    def invincible(self, state: str, screen: pg.Surface):
        """
        コウカトンを無敵状態にする
        """
        if state == "hyper" and Player.hyper_life > 0:
            self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
            self.img = pg.transform.laplacian(self.img)
            screen.blit(self.img, self.rect)


        # if state == "normal":
        #     self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
        #     screen.blit(self.img, self.rect)
            
    def invi_time(self):
        """
        hyper_lifeを管理する関数
        """
        if Player.hyper_life > 0 and Player.hyper_life != 0:
            Player.hyper_life -= 1

        if Player.hyper_life <= 0:
            self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
    
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
    dwall_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/damaged_wall.png"),0, 2.5)
    map_lst = [[0 for i in range(17)] for j in range(26)]
    for x in range(YOKO):
        for y in range(TATE):
            num = random.randint(0,2)
            if num != 0:
                if not((player.x-1 <= x <= player.x+1)and(player.y-1 <= y <= player.y+1)): #  プレイヤーの周りに配置しない
                    map_lst[x][y] = 2
                
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
                # 壊れる壁配置
                if map_lst[x][y] == 2:
                    screen.blit(dwall_image,(x*SQ_SIDE,y*SQ_SIDE))
                    
    
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
                if event.key == pg.K_i and Player.hyper_count > 0:
                    Player.hyper_life = 100
                    if Player.hyper_life > 0:
                        player.invincible("hyper", screen)
                        Player.hyper_count -= 1
        
        player.invi_time()
        player.update(mv, screen,map_lst)
        pg.display.update()
        #print(Player.hyper_life)
        pass



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()