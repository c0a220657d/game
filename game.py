import math
import os
import random
import sys
import time
from typing import Any
import pygame as pg

WIDTH = 1000  # ゲームウィンドウの幅 25マス
HEIGHT = 680  # ゲームウィンドウの高さ 17マス
SQ_SIDE = 40  # マス一辺 
TATE = 17  # マス数
YOKO = 25
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
TYPE_DICT = {0:"floor",1:"wall",2:"block",3:"bomb",4:"explosion"}
P_1 = (3,14)  # 初期位置 
P_2 = (22,3)


def check_bound(obj,map_lst:list,mv):
    """
    obj:対象のインスタンス(座標としてself.x,self.yを定義してあるもの)
    map_lst:マップ
    mv:動く距離
    return:移動後の座標
    """
    if map_lst[obj.x+mv[0]][obj.y+mv[1]] in [0,4]:
        return obj.x+mv[0],obj.y+mv[1]
    else:
        return obj.x,obj.y


def judgement(bomb, map_lst:list):
    """
    bomb:爆弾
    map_lst:マップ
    爆発に関する処理を行う(壁破壊、アイテムドロップ、マップ更新)
    引数:接触判定したいbombクラス
    返値:内容を変更したmap_lst
    """
    exps = []
    newitem = []
    bound = random.random()
    for i in range(1, bomb.power + 1):  # 上側の判定
        if map_lst[bomb.x][bomb.y - i] == 1:  # 壁と接触していたら,その時点で終了
            break
        elif map_lst[bomb.x][bomb.y - i] == 2:  # blockと接触したら
            map_lst[bomb.x][bomb.y - i] = 0    #blockを消す
            if bound > 0.5:
                newitem.append(Item(bomb.x,bomb.y-i))
            exps.append(Explosion(bomb.x,bomb.y-i))
            break
        exps.append(Explosion(bomb.x,bomb.y-i))

    bound = random.random()
    for i in range( 1, bomb.power + 1):  # 下側の判定
        if map_lst[bomb.x][bomb.y + i] == 1:
            break
        elif map_lst[bomb.x][bomb.y + i] == 2:
            map_lst[bomb.x][bomb.y + i] = 0
            if bound > 0.5:
                newitem.append(Item(bomb.x,bomb.y+i))
            exps.append(Explosion(bomb.x,bomb.y+i))
            break
        exps.append(Explosion(bomb.x,bomb.y+i))

    bound = random.random()
    for i in range( 1, bomb.power + 1):  # 右側の判定
        if map_lst[bomb.x + i][bomb.y] == 1:
            break
        elif map_lst[bomb.x + i][bomb.y] == 2:
            map_lst[bomb.x + i][bomb.y] = 0
            if bound > 0.5:
                newitem.append(Item(bomb.x+i,bomb.y))
            exps.append(Explosion(bomb.x+i,bomb.y))
            break
        exps.append(Explosion(bomb.x+i,bomb.y))

    bound = random.random()
    for i in range( 1, bomb.power + 1):  # 左側の判定
        if map_lst[bomb.x - i][bomb.y] == 1:
            break
        elif map_lst[bomb.x - i][bomb.y] == 2:
            map_lst[bomb.x - i][bomb.y] = 0
            if bound > 0.5:
                newitem.append(Item(bomb.x-i,bomb.y))
            exps.append(Explosion(bomb.x-i,bomb.y))
            break
        exps.append(Explosion(bomb.x-i,bomb.y))
    exps.append(Explosion(bomb.x,bomb.y))
    return map_lst,exps,newitem
    
    
class Player(pg.sprite.Sprite):
    """
    プレイヤーの情報を管理するクラス
    pos:初期位置 name:プレイヤー名(仮)
    """
    def __init__(self,pos:tuple,name:str):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.name = name
        self.bomb_cnt = 0  # 置いた爆弾の数 
        self.bomb_max = 3  # 置ける爆弾の最大数 
        self.bomb_power = 1  # 爆風の長さ
        self.hyper_life = 0  # 発動時間 
        self.hyper_count = 1 # 発動回数 
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.info = self.font.render(f"MAX:{self.bomb_max},POW:{self.bomb_power}", 0, "blue")
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x*SQ_SIDE,self.y*SQ_SIDE)
        
    def invincible(self, state: str, screen: pg.Surface):
        """
        コウカトンを無敵状態にする
        """
        if state == "hyper" and self.hyper_life > 0:
            self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
            self.img = pg.transform.laplacian(self.img)
            screen.blit(self.img, self.rect)

    def invi_time(self):
        """
        hyper_lifeを管理する関数
        """
        if self.hyper_life > 0 and self.hyper_life != 0:
            self.hyper_life -= 1

        if self.hyper_life <= 0:
            self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/player.png"), 0, 2.5)
    
    def update(self,mv:list[int,int],screen: pg.Surface,map_lst:list):
        """
        mv:動く距離
        """
        self.x,self.y = check_bound(self,map_lst,mv)
        self.rect.center = (self.x*SQ_SIDE,self.y*SQ_SIDE)
        if map_lst[self.x][self.y] == 4 and self.hyper_life <= 0:
            if self.name == "p1":
                self.x,self.y = P_1
            elif self.name == "p2":
                self.x,self.y = P_2
        screen.blit(self.img,self.rect.center)
        self.info = self.font.render(f"MAX:{self.bomb_max},POW:{self.bomb_power}", 0, "blue")
        if self.name == "p1":
                screen.blit(self.info,(60,0))
        elif self.name == "p2":
                screen.blit(self.info,(800,640))


class Item(pg.sprite.Sprite):
    """
    アイテムを管理するクラス
    x,y:アイテムの場所
    """
    item_types = ("power_up","hyper","max_bomb")  # アイテムの効果
    def __init__(self,x:int,y:int):
        super().__init__()
        self.x = x
        self.y = y
        self.type = random.choice(__class__.item_types)  # アイテムの効果決定
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{self.type}.png"), 0, 2.5)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x*SQ_SIDE,self.y*SQ_SIDE)

    def get_item(self,player:Player,screen:pg.Surface):
        """
        アイテムが拾われた時に呼び出される関数
        player:playerインスタンス
        """
        if self.type == "power_up":
            player.bomb_power += 1
        elif self.type == "hyper":
            player.hyper_life = 300
            player.invincible("hyper",screen)
        elif self.type == "max_bomb":
            player.bomb_max += 1
        self.kill()
    
    def update(self,screen:pg.Surface):
        screen.blit(self.img,self.rect.center)


class Bomb(pg.sprite.Sprite):
    """
    プレイヤーの足元に爆弾を置き、爆発のエフェクトを発生させる機能

    """
    def __init__(self,player:Player):
        super().__init__()
        self.parent = player
        self.x = player.x
        self.y = player.y
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/bomb.png"), 0, 0.05)
        self.rect = self.img.get_rect()
        self.rect.center = (self.x * SQ_SIDE, self.y * SQ_SIDE)
        self.timer = 0
        self.explosions = []
        self.power = player.bomb_power

    def update(self, screen: pg.Surface,map_lst:list):
        self.timer += 1
        map_lst[self.x][self.y] = 3
        if self.timer >= 180:
            self.kill()  # 持続時間が経過したら爆発エフェクトを消去する
            map_lst[self.x][self.y] = 0
            self.parent.bomb_cnt -= 1
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
    players = [Player(P_1,"p1"),Player(P_2,"p2")]
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    wall_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/wall.png"),0, 2.5)
    dwall_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/damaged_wall.png"),0, 2.5)
    map_lst = [[0 for i in range(17)] for j in range(26)]
    bombs = pg.sprite.Group()  # 爆弾インスタンスのリスト
    explosions = pg.sprite.Group()  # 爆発インスタンスのリスト
    items = pg.sprite.Group()
    for x in range(YOKO):
        for y in range(TATE):
            num = random.randint(0,2)
            if num != 0:
                if not((players[0].x-1 <= x <= players[0].x+1)and(players[0].y-1 <= y <= players[0].y+1)): #  プレイヤーの周りに配置しない
                    if not((players[1].x-1 <= x <= players[1].x+1)and(players[1].y-1 <= y <= players[1].y+1)):
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
        mv1 = [0,0]
        mv2 = [0,0]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                for player in players:
                    if player.name == "p1":
                        if event.key == pg.K_w:
                            mv1[1] -= 1
                        if event.key == pg.K_s:
                            mv1[1] += 1
                        if event.key == pg.K_d:
                            mv1[0] += 1
                        if event.key == pg.K_a:
                            mv1[0] -= 1
                        if event.key== pg.K_LSHIFT and player.bomb_cnt < player.bomb_max:  # 左シフトキーが押されたかチェック
                            new_bomb = Bomb(player)
                            player.bomb_cnt += 1
                            bombs.add(new_bomb)
                        if event.key == pg.K_e and player.hyper_count > 0:
                            player.hyper_life = 100
                            if player.hyper_life > 0:
                                player.invincible("hyper", screen)
                            player.hyper_count -= 1
                    if player.name == "p2":
                        if event.key == pg.K_UP:
                            mv2[1] -= 1
                        if event.key == pg.K_DOWN:
                            mv2[1] += 1
                        if event.key == pg.K_RIGHT:
                            mv2[0] += 1
                        if event.key == pg.K_LEFT:
                            mv2[0] -= 1
                        if event.key== pg.K_RSHIFT and player.bomb_cnt < player.bomb_max:  # シフトキーが押されたかチェック
                            new_bomb = Bomb(player)
                            player.bomb_cnt += 1
                            bombs.add(new_bomb)
                        if event.key == pg.K_i and player.hyper_count > 0:
                            player.hyper_life = 10000
                            if player.hyper_life > 0:
                                player.invincible("hyper", screen)
                            player.hyper_count -= 1
                    
        
        players[0].invi_time()
        players[0].update(mv1, screen,map_lst)
        players[1].invi_time()
        players[1].update(mv2, screen,map_lst)
        
        for bomb in bombs:  # 爆弾をイテレート
            bomb.update(screen,map_lst)
            if bomb.timer >= 180:
                map_lst,explosion,new_item = bomb.explode(screen,map_lst)
                items.add(new_item)
                if explosion:
                    explosions.add(explosion)
                    
        for explosion in explosions:  # 爆発をイテレート
            explosion.update(screen,map_lst)
        
        for player in players:
            for i in pg.sprite.spritecollide(player,items,True):
                i.get_item(player,screen)
        for item in items:
            item.update(screen)
        pg.display.update()


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()