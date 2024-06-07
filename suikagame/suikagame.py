import pygame
import pymunk
import pymunk.pygame_util
import random

# 初期化
pygame.init()

# 画面サイズ
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Falling Balls")

# 背景画像の読み込み
background_image = pygame.image.load('background.webp')

# 色の定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
    (0, 0, 128), (128, 128, 0)
]

# フォントの定義
horror_font_path = "fonts/hakidame.TTF"  # フォントファイルのパスを指定
horror_font = pygame.font.Font(horror_font_path, 36)
large_font = pygame.font.Font(horror_font_path, 100)

# 物理空間の作成
space = pymunk.Space()
space.gravity = (0, 900)  # 重力の設定

# スコア変数
score = 0

# ボールの情報を格納するリスト
balls = []

def create_static_walls(space):
    static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    
    # 壁の厚さ
    wall_thickness = 10
    
    # 床
    floor = pymunk.Segment(static_body, (190, 550), (610, 550), wall_thickness)
    floor.friction = 0.1  # 摩擦係数を低く設定
    floor.elasticity = 0.9  # 弾性係数を高く設定
    
    # 左の壁
    left_wall = pymunk.Segment(static_body, (190, 550), (190, 140), wall_thickness)
    left_wall.friction = 0.1
    left_wall.elasticity = 0.9
    
    # 右の壁
    right_wall = pymunk.Segment(static_body, (610, 550), (610, 140), wall_thickness)
    right_wall.friction = 0.1
    right_wall.elasticity = 0.9

    # コーナー
    corners = [
        pymunk.Circle(static_body, wall_thickness, (190, 140)),
        pymunk.Circle(static_body, wall_thickness, (610, 140)),
        pymunk.Circle(static_body, wall_thickness, (190, 550)),
        pymunk.Circle(static_body, wall_thickness, (610, 550))
    ]
    for corner in corners:
        corner.elasticity = 0.9
        corner.friction = 0.1
    
    # 各コーナーを個別に追加
    space.add(static_body, floor, left_wall, right_wall)
    space.add(*corners)

    return corners  # コーナーを返す

# ボールの作成
next_ball_radius = random.choice([ 10,  20,  30,  40, 50])
next_ball_color = COLORS[[10,  20, 30,  40, 50].index(next_ball_radius)]

def create_ball(space, pos):
    global score, next_ball_radius, next_ball_color
    radius = next_ball_radius
    color = next_ball_color
    mass = radius  # 半径に基づいて質量を設定
    body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.9
    shape.friction = 0.1 
    space.add(body, shape)
    
    balls.append((shape, color))  # ボールとその色をリストに追加
    
    next_ball_radius = random.choice([ 10,  20,  30,  40, 50,60,70])
    next_ball_color = COLORS[[ 10,  20,  30,  40, 50,60,70].index(next_ball_radius)]
    
    return shape

# 衝突ハンドラの設定
def setup_collision_handler(space):
    handler = space.add_collision_handler(0, 0)
    handler.begin = combine_balls  # 衝突開始時にcombine_balls関数を呼び出す

def combine_balls(arbiter, space, data):
    global score
    shapes = arbiter.shapes
    ball1 = shapes[0]
    ball2 = shapes[1]

    # ボールのリストから対応する色を見つけます
    color1 = None
    color2 = None
    for shape, color in balls:
        if shape == ball1:
            color1 = color
        if shape == ball2:
            color2 = color

    if isinstance(ball1, pymunk.Circle) and isinstance(ball2, pymunk.Circle):
        radius1 = ball1.radius
        radius2 = ball2.radius

        if radius1 == radius2 and color1 == color2:
            # 古いボールを削除
            space.remove(ball1, ball1.body)
            space.remove(ball2, ball2.body)

            # リストから削除
            balls[:] = [(shape, color) for shape, color in balls if shape != ball1 and shape != ball2]

            # 新しい大きなボールを作成
            new_radius = radius1 * 1.6  # 半径を20%増加
            new_radius = min(new_radius, 70)  # 最大半径50に制限

            # 新しい半径に基づいて色を決定
            new_color = COLORS[int(new_radius // 10) - 1]

            mass = new_radius
            body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, new_radius))
            body.position = arbiter.contact_point_set.points[0].point_a
            new_ball = pymunk.Circle(body, new_radius)
            new_ball.elasticity = 0.9
            new_ball.friction = 0.1
            space.add(body, new_ball)
            
            balls.append((new_ball, new_color))  # 新しいボールをリストに追加

            score += 50  # ボールが合体するたびにスコアを50増やす

    return True


# 描画関数
def draw(space, screen, corners):
    screen.blit(background_image, (0, 0))  # 背景画像を描画

    for shape, color in balls:
        pygame.draw.circle(screen, color, (int(shape.body.position.x), int(shape.body.position.y)), int(shape.radius))
    for shape in space.shapes:
        if isinstance(shape, pymunk.Segment):
            pygame.draw.line(screen, COLORS[0], shape.a, shape.b, 5)
    
    # コーナーを描画
    for corner in corners:
        pygame.draw.circle(screen, COLORS[0], (int(corner.offset.x), int(corner.offset.y)), int(corner.radius))
    
    # スコアを描画
    score_text = horror_font.render(f"Score: {score}", True, COLORS[0])
    screen.blit(score_text, (10, 30))
    
    # 次に落ちてくるボールを壁の外に描画
    next_ball_x = screen_width - 70
    next_ball_y = 70
    pygame.draw.circle(screen, next_ball_color, (next_ball_x, next_ball_y), next_ball_radius)
    
    # [next]という文字を追加
    next_text = horror_font.render("next", True, COLORS[0])
    screen.blit(next_text, (next_ball_x - 34, next_ball_y + 50))
    
    pygame.display.flip()

def draw_game_over(screen):
    screen.blit(background_image, (0, 0))  # 背景画像を描画
    
    # "GAME OVER"テキストを大きく表示
    game_over_text = large_font.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(screen_width / 2, screen_height / 2 - 50))
    screen.blit(game_over_text, text_rect)
    
    # コンティニューボタンを表示
    button_text = horror_font.render("Continue", True, WHITE)
    button_rect = pygame.Rect(screen_width / 2 - 100, screen_height / 2 + 50, 200, 50)
    pygame.draw.rect(screen, RED, button_rect)
    screen.blit(button_text, button_rect.move(30, 10))
    
    pygame.display.flip()
    return button_rect

# メインループ
def main():
    global score, balls, screen_width, screen_height, screen
    clock = pygame.time.Clock()
    corners = create_static_walls(space)  # 床と壁の作成
    setup_collision_handler(space)  # 衝突ハンドラの設定を追加
    
    running = True
    game_over = False
    button_rect = None
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # ウィンドウのサイズが変更されたときに対応
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                # すべてのゲーム要素のサイズや位置を再計算
                recreate_all_game_elements(space)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if game_over:
                    if button_rect and button_rect.collidepoint(pos):
                        game_over = False
                        score = 0
                        recreate_all_game_elements(space)
                else:
                    can_create_ball = False  # ここで初期化
                    if pos[1] <= 100:  # y座標が100以下の場合
                        can_create_ball = True
                        for shape, _ in balls:
                            if (shape.body.position - pymunk.Vec2d(pos[0], pos[1])).length < shape.radius * 2:
                                can_create_ball = False
                                break
                        if can_create_ball:
                            create_ball(space, pos)
        
        if not game_over:
            space.step(1/60.0)
            for shape, _ in balls:
                if shape.body.position.y > screen_height:
                    game_over = True
                    break
        
        if game_over:
            button_rect = draw_game_over(screen)
        else:
            draw(space, screen, corners)  # コーナーを描画関数に渡す

        clock.tick(60)
    
    pygame.quit()


# すべてのゲーム要素の再生成
# すべてのゲーム要素の再生成
def recreate_all_game_elements(space):
    global balls
    balls = []
    for body in space.bodies:
        space.remove(body)
    for shape in space.shapes:
        space.remove(shape)
    corners = create_static_walls(space)
    setup_collision_handler(space)


if __name__ == "__main__":
    main()

