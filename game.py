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
TYPE_DICT = {0:"floor",1:"wall",2:"block",3:"bomb",4:"explosion"}


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
    
def judgement(bomb, map_lst:list):
    """
    bomb:爆弾
    map_lst:

    引数:接触判定したいbombクラス
    返値:内容を変更したmap_lst
    """
    exps = []
    for i in range(1, bomb.power + 1):  # 上側の判定
        if map_lst[bomb.x][bomb.y - i] == 1:  # 壁と接触していたら,その時点で終了
            break
        elif map_lst[bomb.x][bomb.y - i] == 2:  # blockと接触したら
            map_lst[bomb.x][bomb.y - i] = 0    #blockを消す
            exps.append(Explosion(bomb.x,bomb.y-i))
            break
        exps.append(Explosion(bomb.x,bomb.y-i))

    for i in range( 1, bomb.power + 1):  # 下側の判定
        if map_lst[bomb.x][bomb.y + i] == 1:
            break
        elif map_lst[bomb.x][bomb.y + i] == 2:
            map_lst[bomb.x][bomb.y + i] = 0
            exps.append(Explosion(bomb.x,bomb.y+i))
            break
        exps.append(Explosion(bomb.x,bomb.y+i))

    for i in range( 1, bomb.power + 1):  # 右側の判定
        if map_lst[bomb.x + i][bomb.y] == 1:
            break
        elif map_lst[bomb.x + i][bomb.y] == 2:
            map_lst[bomb.x + i][bomb.y] = 0
            exps.append(Explosion(bomb.x+i,bomb.y))
            break
        exps.append(Explosion(bomb.x+i,bomb.y))

    for i in range( 1, bomb.power + 1):  # 左側の判定
        if map_lst[bomb.x - i][bomb.y] == 1:
            break
        elif map_lst[bomb.x - i][bomb.y] == 2:
            map_lst[bomb.x - i][bomb.y] = 0
            exps.append(Explosion(bomb.x-i,bomb.y))
            break
        exps.append(Explosion(bomb.x-i,bomb.y))
    exps.append(Explosion(bomb.x,bomb.y))
    return map_lst,exps
    
    
class Player():
  
    hyper_life = 0  # 発動時間
    hyper_count = 1 # 発動回数

    def __init__(self,x,y,name):
        self.x = x
        self.y = y
        self.name = name
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
        if map_lst[self.x][self.y] == 4:
            self.x,self.y = (3,11)
        screen.blit(self.img,self.rect.center)


class Bomb(pg.sprite.Sprite):
    """
    プレイヤーの足元に爆弾を置き、爆発のエフェクトを発生させる機能

    """
    def __init__(self,player):
        super().__init__()
        self.x = player.x
        self.y = player.y
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/bomb.png"), 0, 0.05)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x * SQ_SIDE, self.y * SQ_SIDE)
        self.timer = 0
        self.explosions = []
        self.power = 2

    def update(self, screen: pg.Surface,map_lst:list):
        self.timer += 1
        map_lst[self.x][self.y] = 3
        if self.timer >= 180:
            self.kill()  # 持続時間が経過したら爆発エフェクトを消去する
            map_lst[self.x][self.y] = 0
        screen.blit(self.img, self.rect.center)

        
    def explode(self, screen: pg.Surface,map_lst:list):
        if self.timer >= 180: 
            return judgement(self,map_lst)
        return map_lst,[]
      

class Explosion(pg.sprite.Sprite):
    """
    爆弾の四方に爆発が起こるようにする。
    """
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/explosion.gif"),0 ,0.5)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x * SQ_SIDE, self.y * SQ_SIDE)
        self.timer = 0
        self.duration = 60
                
    def update(self, screen: pg.Surface,map_lst:list):
        self.timer += 1
        map_lst[self.x][self.y] = 4
        if self.timer >= self.duration: 
            self.kill()
            self.timer = 0
            map_lst[self.x][self.y] = 0
        screen.blit(self.img, self.rect.center)


def main():
    pg.display.set_caption("吹き飛べ！！こうかとん！！！")
    player = Player(3,11,"p1")
    player2 = Player(20,3,"p2")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    wall_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/wall.png"),0, 2.5)
    dwall_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/damaged_wall.png"),0, 2.5)
    map_lst = [[0 for i in range(17)] for j in range(26)]
    bombs = pg.sprite.Group()  # 爆弾インスタンスのリスト
    explosions = pg.sprite.Group()  # 爆発インスタンスのリスト
    for x in range(YOKO):
        for y in range(TATE):
            num = random.randint(0,2)
            if num != 0:
                if not((player.x-1 <= x <= player.x+1)and(player.y-1 <= y <= player.y+1)): #  プレイヤーの周りに配置しない
                    map_lst[x][y] = 2
    
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
                
    while True:
        screen.blit(bg_img, [0, 0])
        # 壁描画
        for x in range(YOKO):
            for y in range(TATE):
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
                if player.name == "p1":
                    if event.key == pg.K_w:
                        mv[1] -= 1
                    if event.key == pg.K_s:
                        mv[1] += 1
                    if event.key == pg.K_d:
                        mv[0] += 1
                    if event.key == pg.K_a:
                        mv[0] -= 1
                if player.name == "p2":
                    if event.key == pg.K_UP:
                        mv[1] -= 1
                    if event.key == pg.K_DOWN:
                        mv[1] += 1
                    if event.key == pg.K_RIGHT:
                        mv[0] += 1
                    if event.key == pg.K_LEFT:
                        mv[0] -= 1
                if event.key== pg.K_LSHIFT:  # 左シフトキーが押されたかチェック
                    new_bomb = Bomb(player)
                    bombs.add(new_bomb)
                if event.key == pg.K_i and Player.hyper_count > 0:
                    Player.hyper_life = 100
                    if Player.hyper_life > 0:
                        player.invincible("hyper", screen)
                        Player.hyper_count -= 1
        
        player.invi_time()
        player.update(mv, screen,map_lst)
        
        for bomb in bombs:  # 爆弾をイテレート
            bomb.update(screen,map_lst)
            if bomb.timer >= 180:
                map_lst,explosion = bomb.explode(screen,map_lst)
                if explosion:
                    explosions.add(explosion)
                    
        for explosion in explosions:  # 爆発をイテレート
            explosion.update(screen,map_lst)
        pg.display.update()


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()