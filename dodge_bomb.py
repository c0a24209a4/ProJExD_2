import os
import random 
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectまたは爆弾Rect
    戻り値：判定結果タプル（横方向，縦方向）
    画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH <rct.right:  # 横方向のはみ出しチェック
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向のはみ出しチェック
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    Docstring for gameover
    
    :param screen: pg.Surface
    """

    ov_img = pg.Surface((WIDTH, HEIGHT))
    ov_img.fill((0, 0, 0))
    ov_img.set_alpha(200)
    screen.blit(ov_img, (0, 0))

    font = pg.font.Font(None, 50)
    text_surf = font.render("Game Over", True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(text_surf, text_rect)

    kk_img_over = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    # 左側に配置
    kk_rect_left = kk_img_over.get_rect(midright=(text_rect.left - 20, text_rect.centery))
    screen.blit(kk_img_over, kk_rect_left)

    # 右側に配置
    kk_rect_right = kk_img_over.get_rect(midleft=(text_rect.right + 20, text_rect.centery))
    screen.blit(kk_img_over, kk_rect_right)

    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の大きさの爆弾Surfaceと加速度リストを作成して返す。

    :return: (bb_imgs, bb_accs)
        bb_imgs: 爆弾Surfaceのリスト
        bb_accs: 爆弾速度倍率のリスト
    """

    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]

    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    
    return bb_imgs, bb_accs



# ============= 演習3 ============
def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    こうかとんの移動方向に応じた画像Surfaceの辞書を返す

    :return: {(dx, dy): Surface, ...}
        dx, dyは横・縦の移動量
    """
    kk_imgs = {}
    
    # 元画像をロード
    kk_img_orig = pg.image.load("fig/3.png")
    
    # 移動方向ごとにrotozoomで回転
    # (dx, dy): (横移動, 縦移動)
    kk_imgs[(0, 0)] = pg.transform.rotozoom(kk_img_orig, 0, 0.9)     # 動かない
    kk_imgs[(5, 0)] = pg.transform.rotozoom(kk_img_orig, -90, 0.9)   # 右
    kk_imgs[(-5, 0)] = pg.transform.rotozoom(kk_img_orig, 90, 0.9)   # 左
    kk_imgs[(0, -5)] = pg.transform.rotozoom(kk_img_orig, 0, 0.9)    # 上
    kk_imgs[(0, 5)] = pg.transform.rotozoom(kk_img_orig, 180, 0.9)   # 下
    kk_imgs[(5, -5)] = pg.transform.rotozoom(kk_img_orig, -45, 0.9)  # 右上
    kk_imgs[(5, 5)] = pg.transform.rotozoom(kk_img_orig, -135, 0.9)  # 右下
    kk_imgs[(-5, -5)] = pg.transform.rotozoom(kk_img_orig, 45, 0.9)  # 左上
    kk_imgs[(-5, 5)] = pg.transform.rotozoom(kk_img_orig, 135, 0.9)  # 左下

    return kk_imgs

# =============/////============= 

# =============演習4===============
def follow_direction(org: pg.Rect, dst: pg.Rect, current_v: tuple[float,float]=(0,0)) -> tuple[float,float]:
    """
    爆弾(org)がこうかとん(dst)に追従する方向ベクトルを返す。

    :param org: 爆弾のRect
    :param dst: こうかとんのRect
    :param current_v: 現在の速度（慣性用）
    :return: (vx, vy)
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    distance = (dx**2 + dy**2) ** 0.5

    if distance < 300:  # 近すぎたら慣性で移動
        return current_v

    if distance == 0:  # 完全に重なった場合
        return (0, 0)

    norm = (dx**2 + dy**2) ** 0.5
    vx = dx / norm * (50**0.5)  # ノルム√50になるように正規化
    vy = dy / norm * (50**0.5)
    return (vx, vy)
# =============/////============= 

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 半径10の赤い円を描画
    bb_img.set_colorkey((0, 0, 0))  # 黒色を透過色に設定
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾横座標
    bb_rct.centery = random.randint(0, HEIGHT)  # 爆弾縦座標
    vx, vy = +5, +5  # 爆弾の横速度，縦速度
    clock = pg.time.Clock()
    tmr = 0

    # while文の前に呼び出してSurfaceリストと加速度リストを取得
    bb_imgs, bb_accs = init_bb_imgs()

    # ===========演習3============
    kk_imgs_dict = get_kk_imgs()
    # ===========////=============

     # ===========演習4=============
    current_v = (vx, vy)
     # ===========////=============
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾が衝突したら
            gameover(screen)
            return

        screen.blit(bg_img, [0, 0]) 

        # tmrはフレームタイマーなど
        idx = min(tmr // 500, 9)  # 0～9でSurfaceと加速度を選択
        bb_img = bb_imgs[idx]


        # 爆弾Rectのサイズ更新
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        # 追従方向を計算
        vx, vy = follow_direction(bb_rct, kk_rct, current_v)

        # 加速度を反映
        vx *= bb_accs[idx]
        vy *= bb_accs[idx]

        # 現在の速度を更新（慣性）
        current_v = (vx, vy)

        # 移動
        bb_rct.move_ip(vx, vy)
        # 移動

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]  # 横方向の移動量
                sum_mv[1] += mv[1]  # 縦方向の移動量
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外なら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動をなかったことにする
        screen.blit(kk_img, kk_rct)
        yoko, tate = check_bound(bb_rct)
        # 爆弾がこうかとんに追従する方向を計算
        
    
        # ==========演習3============
        sum_mv_tuple = tuple(sum_mv)  # sum_mv = [dx, dy]
        kk_img = kk_imgs_dict.get(sum_mv_tuple, kk_imgs_dict[(0, 0)])
        # ===========////============

        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()