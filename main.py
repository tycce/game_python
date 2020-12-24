import pygame
import random
import sys

pygame.init()
pygame.font.init()

# Размер окна
win_width = 1640
win_height = 950

win = pygame.display.set_mode((win_width, win_height))
clock = pygame.time.Clock()


# Наш игрок
class Player:
    heart = 4
    key = 0
    # размер спрайта игрока
    width = 27
    height = 35
    # скорость игрока
    speed = 5
    # координаты игрока
    x = 60
    y = 920 - height
    # состояние игрока
    color = (155, 22, 255)
    is_fallen = False
    fallen_scale = 1
    is_jump = False
    jump_count = 9
    jump_scale = 0
    last_move = 1  # 1 == right | -1 == left
    pos_anim = 7
    is_anim_gd = False
    enemy_radius = 3

    # куда идет наш персонаж
    left = False
    right = False
    animation_walk = 0

    # загружаем спрайты
    walk_left = [pygame.image.load("img/walk_left_1.png"), pygame.image.load("img/walk_left_2.png"),
                 pygame.image.load("img/walk_left_3.png"),
                 pygame.image.load("img/walk_left_4.png"), pygame.image.load("img/walk_left_5.png"),
                 pygame.image.load("img/walk_left_6.png")]

    walk_right = [pygame.image.load("img/walk_right_1.png"), pygame.image.load("img/walk_right_2.png"),
                  pygame.image.load("img/walk_right_3.png"),
                  pygame.image.load("img/walk_right_4.png"), pygame.image.load("img/walk_right_5.png"),
                  pygame.image.load("img/walk_right_6.png")]

    stay_sprite = [pygame.image.load("img/stay_1.png"), pygame.image.load("img/stay_2.png"),
                   pygame.image.load("img/stay_3.png")]

    # прыжок
    def jump(self):
        if self.jump_count >= 0 and not self.is_fallen:
            for block in blocks:
                if (
                        block.x < self.x < block.x + block.width or block.x < self.x + self.width < block.x + block.width) and self.y - (
                        self.jump_count ** 2) // 3 < block.y + block.height < self.y:
                    self.y = block.y + block.height
                    self.is_fallen = True
                    self.jump_count = 9
                    return
            self.y -= (self.jump_count ** 2) // 3
            self.jump_count -= 1
        elif not self.is_fallen:
            self.is_fallen = True
            self.jump_count = 9

    # падение
    def fallen(self):
        for block in blocks:
            if (
                    block.x < self.x < block.x + block.width or block.x < self.x + self.width < block.x + block.width) and self.y + self.height >= block.y > self.y:
                self.y = block.y - self.height
                self.fallen_scale = 1
                self.is_fallen = False
                self.is_jump = False
                return

        if self.y + self.height < win_height:
            if self.y + self.height + (self.fallen_scale * 2) // 2 >= win_height:
                self.y = win_height - self.height
            else:
                self.y += (self.fallen_scale * 2) // 2
                self.fallen_scale += 1
        else:
            self.fallen_scale = 1
            self.is_fallen = False
            self.is_jump = False

    # Левая стенка блока
    def check_block_left(self):
        for block in blocks:
            if block.x <= self.x + self.width < block.x + block.width and self.y + self.height > block.y and self.y < block.y + block.height:
                if not self.is_fallen:
                    self.x = block.x - self.width
                return False
        return True

    # Правая стенка блока
    def check_block_right(self):
        for block in blocks:
            if block.x < self.x <= block.x + block.width and self.y + self.height > block.y and self.y < block.y + block.height:
                if not self.is_fallen:
                    self.x = block.x + block.width
                return False
        return True

    # Падаем если не на блоке
    def check_floor(self):
        if not self.is_fallen and not self.is_jump:
            for block in blocks:
                if self.x > block.x + block.width or self.x + self.width < block.x and self.y + self.height > block.y:
                    if self.y + self.height != win_height:
                        self.is_fallen = True
                        self.fallen()
                        return

    # проверяем коснулся ли персонаж монстра справа
    def check_enemy_right(self):
        for enemy_cur in enemy_arr:
            if enemy_cur.x < self.x + self.width + self.enemy_radius < enemy_cur.x + enemy_cur.width and (
                    enemy_cur.y < self.y < enemy_cur.y + enemy_cur.height or enemy_cur.y < self.y + self.height < enemy_cur.y + enemy_cur.height):
                self.is_anim_gd = True
                return
        for enemy_bl in enemy_block:
            if enemy_bl.x < self.x + self.width < enemy_bl.x + enemy_bl.width and (
                    enemy_bl.y <= self.y <= enemy_bl.y + enemy_bl.height or enemy_bl.y <= self.y + self.height <= enemy_bl.y + enemy_bl.height):
                self.is_fallen = False
                self.is_anim_gd = True
                self.jump()
                self.is_jump = True
                return

    # проверяем коснулся ли персонаж монстра слева
    def check_enemy_left(self):
        for enemy_cur in enemy_arr:
            if enemy_cur.x < self.x - self.enemy_radius < enemy_cur.x + enemy_cur.width and (
                    enemy_cur.y < self.y < enemy_cur.y + enemy_cur.height or enemy_cur.y < self.y + self.height < enemy_cur.y + enemy_cur.height):
                self.is_anim_gd = True
                return
        for enemy_bl in enemy_block:
            if enemy_bl.x < self.x < enemy_bl.x + enemy_bl.width and (
                    enemy_bl.y <= self.y <= enemy_bl.y + enemy_bl.height or enemy_bl.y <= self.y + self.height <= enemy_bl.y + enemy_bl.height):
                self.is_fallen = False
                self.is_anim_gd = True
                self.jump()
                self.is_jump = True
                return

    # получаем урон
    def get_damage(self):
        if self.is_anim_gd:
            if self.pos_anim != 0:
                self.x -= 10 * self.last_move
                self.pos_anim -= 1
            else:
                self.pos_anim = 7
                self.is_anim_gd = False
                self.heart -= 1

    # устанавливаем позицию игрока
    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def draw(self, win):
        if self.animation_walk + 1 >= 30:
            self.animation_walk = 0
        if self.left:
            win.blit(self.walk_left[self.animation_walk // 5], (self.x, self.y))
            self.animation_walk += 1
        elif self.right:
            win.blit(self.walk_right[self.animation_walk // 5], (self.x, self.y))
            self.animation_walk += 1
        else:
            win.blit(self.stay_sprite[self.animation_walk // 10], (self.x, self.y))
            self.animation_walk += 1


# Ключи для выхода
class Key:
    width = 40
    height = 40
    color = (15, 163, 127)

    def __init__(self, x, y):
        self.x = x
        self.y = y

    # проверяем коснулся ли игрок ключа
    def check_player(self):
        if (self.x + self.width > player.x > self.x or self.x < player.x + player.width < self.x + self.width) \
                and (
                self.y < player.y < self.y + self.height or self.y < player.y + player.height < self.y + self.height):
            player.key += 1
            key_exit.pop(key_exit.index(self))


# Дверь для завершения уровня
class Door:
    x = 0
    y = 0
    width = 40
    height = 50
    color = (1, 1, 1)

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    # проверяем коснулся ли игрок двери и наличие 3 ключей
    def check_player(self):
        if player.key == 3 and (
                self.x + self.width > player.x > self.x or self.x < player.x + player.width < self.x + self.width) \
                and (
                self.y < player.y < self.y + self.height or self.y < player.y + player.height < self.y + self.height):
            show_menu("Выход")
            global run
            run = False


img_block_is_damage = pygame.image.load("img/block_is_damage.png")


# Блоки
class Block:
    global img_block_is_damage
    width = 40
    height = 40
    hits = 3
    is_damage = False
    current_sprite = img_block_is_damage

    def __init__(self, x, y):
        self.x = x
        self.y = y


# Пули
class Bullet:
    color = (255, 0, 0)
    speed = 20
    radius = 5
    hits = 5

    def __init__(self, x, y, route):
        self.x = x
        self.y = y
        self.route = route
        if route == -1:
            self.speed = -20
        else:
            self.speed = 20


# проверяем попала ли пуля в блок
def bullet_check_block():
    for bullet_cur in bullets:
        for block in blocks:
            if block.x < bullet_cur.x < block.x + block.width and block.y < bullet_cur.y < block.y + block.height:
                if block.hits == 1:
                    blocks.pop(blocks.index(block))
                elif block.is_damage:
                    global img_block_is_damage
                    block.current_sprite = img_block_is_damage_hit
                    block.hits -= 1
                bullets.pop(bullets.index(bullet_cur))
                return


# проверяем попала ли пуля в монстра
def bullet_check_enemy():
    for bullet_cur in bullets:
        for enemy_cur in enemy_arr:
            if enemy_cur.x < bullet_cur.x < enemy_cur.x + enemy_cur.width and enemy_cur.y < bullet_cur.y < enemy_cur.y + enemy_cur.height:
                if enemy_cur.hits == 1:
                    enemy_arr.pop(enemy_arr.index(enemy_cur))
                else:
                    enemy_cur.color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
                    enemy_cur.hits -= 1
                bullets.pop(bullets.index(bullet_cur))
                return


# Движущиеся блоки
class EnemyBlock:
    width = 30
    height = 30
    color = (124, 255, 122)
    speed = 10
    is_run = False

    def __init__(self, x, y):
        self.x = x
        self.start_x = self.x
        self.y = y

    # Движение блока
    def run(self):
        if self.is_run:
            self.x -= self.speed
            for block in blocks:
                if (
                        block.x < self.x < block.x + block.width or block.x + block.width > self.x + self.width > block.x) and (
                        block.y < self.y < block.y + block.height or block.y < self.y + self.height < block.y + block.height):
                    self.x = self.start_x
                    self.y = random.randint(830, 900)
                    return


# Враги
class Enemy:
    width = 25
    height = 30
    hits = 3
    color = (124, 65, 12)
    counter = 0.1
    sprite = [pygame.image.load("img/skull_v2_1.png"), pygame.image.load("img/skull_v2_2.png"),
              pygame.image.load("img/skull_v2_3.png"), pygame.image.load("img/skull_v2_4.png")]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation = random.randint(0, 16)

    def draw(self):
        if self.animation + 0.5 >= 16:
            self.animation = 0

        win.blit(self.sprite[round(self.animation // 4)], (self.x, self.y))
        self.animation += 0.5


# Читаем карту из файла
def create_map():
    map_file = open("levels.txt", 'r')
    content = map_file.readlines() + ['\r\n']
    map_file.close()

    map_obj = []
    map_text_lines = []
    for line_num in range(len(content)):
        line = content[line_num].rstrip('\r\n')

        if '1' in line:  # не читаем номер уровня
            line = line[:line.find('1')]

        if line != '':  # Пустая строка
            map_text_lines.append(line)
        elif line == '' and len(map_text_lines) > 0:
            max_width = -1  # кол-во блоков
            for i in range(len(map_text_lines)):
                if len(map_text_lines[i]) > max_width:
                    max_width = len(map_text_lines[i])
            for x in range(len(map_text_lines[0])):
                map_obj.append([])
            for y in range(len(map_text_lines)):
                for x in range(max_width):
                    map_obj[x].append(map_text_lines[y][x])
    return map_obj


# Телепорт
class Teleport:
    width = 40
    height = 40
    color = (125, 125, 125)
    tp_x = 0
    tp_y = 0
    tp_save_time = 100

    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Коснулся ли игрок телепорта
    def check_player(self):
        if player.is_jump and (
                self.x + self.width > player.x > self.x or self.x < player.x + player.width < self.x + self.width) \
                and (
                self.y < player.y < self.y + self.height or self.y < player.y + player.height < self.y + self.height):
            player.x = self.tp_x
            player.y = self.tp_y + self.height + 5
            player.is_jump = False
            player.jump_count = 9
            for bl_enemy in enemy_block:
                bl_enemy.is_run = True


# заполняем массивы элементами карты
def get_map(game_map):
    bl_size = 40
    pos_x = 0
    pos_y = 0
    for y in game_map:
        for x in y:
            if x == "#":
                block = Block(pos_x, pos_y)
                blocks.append(block)
            if x == "H":
                block = Block(pos_x, pos_y)
                block.is_damage = True
                blocks.append(block)
            elif x == "*":
                player.set_pos(pos_x, pos_y - 40)
            elif x == "@":
                enemy_arr.append(Enemy(pos_x, pos_y))
            elif x == "^":
                teleport.append(Teleport(pos_x, pos_y))
            elif x == "&":
                enemy_block.append(EnemyBlock(pos_x, pos_y))
            elif x == "k":
                key_exit.append(Key(pos_x, pos_y))
            elif x == "!":
                door.set_pos(pos_x, pos_y)
            pos_y += bl_size
        pos_y = 0
        pos_x += bl_size


# Кнопка
class Button:
    width = 200
    height = 40

    def __init__(self, x, y, message):
        self.x = x - self.width // 2
        self.y = y - self.height // 2
        self.message = message
        self.font_type = pygame.font.Font("RussoOne-Regular.ttf", 32)
        self.text = self.font_type.render(message, True, (0, 0, 0))
        self.place_text = self.text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))

    def draw(self, win):

        if self.check_pos():
            pygame.draw.rect(win, (60, 196, 175), (self.x, self.y, self.width, self.height))
            win.blit(self.text, self.place_text)
        else:
            pygame.draw.rect(win, (93, 196, 175), (self.x, self.y, self.width, self.height))
            win.blit(self.text, self.place_text)

    def check_pos(self):
        mouse = pygame.mouse.get_pos()
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            return True
        else:
            return False


# игровое меню
def show_menu(message):
    menu_background = pygame.image.load("img/menu_back.png")

    start_btn = Button(win_width // 2, win_height // 2, message)

    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and message == "Играть" and start_btn.check_pos():
                if event.button == 1:
                    show = False
            if event.type == pygame.MOUSEBUTTONDOWN and message == "Выход" and start_btn.check_pos():
                sys.exit()
        pygame.time.delay(50)
        win.blit(menu_background, (0, 0))
        start_btn.draw(win)
        pygame.display.update()


background = pygame.image.load("img/back2.png")
img_block = pygame.image.load("img/floor.png")
img_block_is_damage_hit = pygame.image.load("img/block_is_damage_hit.png")
img_bullet = pygame.image.load("img/bullet.png")
img_open_door = pygame.image.load("img/door_open.png")
img_close_door = pygame.image.load("img/door_close.png")
img_key = pygame.image.load("img/key.png")
img_portal = pygame.image.load("img/portal.png")
img_enemy_block = pygame.image.load("img/enemy_block.png")
img_heart = pygame.image.load("img/heart.png")


# Отрисовываем все что у нас есть
def draw_window():
    for i in range(38):
        for j in range(21):
            win.blit(background, (42 * i + 40, 42 * j + 40))

    win.blit(img_close_door, (door.x, door.y))
    player.draw(win)

    for en_block in enemy_block:
        win.blit(img_enemy_block, (en_block.x, en_block.y))
    for tp in teleport:
        win.blit(img_portal, (tp.x + 10, tp.y + 10))
    for block in blocks:
        if not block.is_damage:
            win.blit(img_block, (block.x, block.y))
        else:
            win.blit(block.current_sprite, (block.x, block.y))
    for bullet in bullets:
        win.blit(img_bullet, (bullet.x, bullet.y))
    for enemy in enemy_arr:
        enemy.draw()
    for key in key_exit:
        win.blit(img_key, (key.x, key.y))
    i = 10
    for heart in range(player.heart):
        win.blit(img_heart, (30 + i, 5))
        i += 40


# Инициализаация
game_map = create_map()
key_exit = []
teleport = []
player = Player()
blocks = []
enemy_block = []
door = Door()
bullets = []
side = 1
enemy_arr = []
get_map(game_map)
teleport[0].tp_x = teleport[1].x
teleport[0].tp_y = teleport[1].y
teleport[1].tp_x = teleport[0].x
teleport[1].tp_y = teleport[0].y

run = True
pygame.display.set_caption("Подземелье")

show_menu("Играть")
while run:
    clock.tick(30)
    if player.heart == 0:
        pygame.quit()
        print("Вы проиграли")
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            bullets.append(
                Bullet(round(player.x + player.width // 2), round(player.y + player.height // 2) + -10,
                       player.last_move))

    for bullet in bullets:
        if win_width > bullet.x > 0:
            bullet.x += bullet.speed
        else:
            bullets.pop(bullets.index(bullet))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.x > 0:
        player.last_move = -1
        player.left = True
        player.right = False
        if player.check_block_right():
            player.x -= player.speed
    elif keys[pygame.K_RIGHT] and player.x < win_width - player.width:
        player.last_move = 1
        player.left = False
        player.right = True
        if player.check_block_left():
            player.x += player.speed
    else:
        player.left = False
        player.right = False
    if not player.is_jump and not player.is_fallen:
        if keys[pygame.K_SPACE]:
            player.is_jump = True

    else:
        player.jump()

    if player.is_fallen:
        player.fallen()

    for bl_enemy in enemy_block:
        if bl_enemy.is_run:
            bl_enemy.run()

    for tp in teleport:
        tp.check_player()

    for k in key_exit:
        k.check_player()

    if door is not None:
        door.check_player()
    player.check_enemy_right()
    player.check_enemy_left()
    player.get_damage()
    bullet_check_enemy()
    bullet_check_block()
    player.check_floor()
    draw_window()

    pygame.display.update()

pygame.quit()
