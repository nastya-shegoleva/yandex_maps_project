import os
import sys

import pygame
import requests


def draw_map(size, dir=(0, 0), map_layers='sat'):
    global map_file, coords
    current_lattitude, current_longitude = coords

    x_move, y_move = dir
    rect = 2 ** (17 - size) * 0.002
    current_lattitude += (x_move * rect / 2) / (1 + (current_lattitude) / 90)
    current_longitude += y_move * rect / 2
    if current_longitude > 85:
        current_longitude = 85
    if current_longitude < -85:
        current_longitude = -85
    if current_lattitude > 180:
        current_lattitude -= 360
    if current_lattitude < -180:
        current_lattitude += 360
    coords = f'{current_lattitude},{current_longitude}'
    map_request = "https://static-maps.yandex.ru/1.x/?ll=" + coords + "&"
    map_request += "z=" + str(size) + f"&l={map_layers}"
    response = requests.get(map_request)
    coords = (current_lattitude, current_longitude)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()


def move_map(z, m_l):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # !!!!!!!!!!!! Change key
                if event.key == pygame.K_1:
                    z += 1
                    if z > 19:
                        z = 19
                    draw_map(z, map_layers=m_l)
                if event.key == pygame.K_2:
                    z -= 1
                    if z < 1:
                        z = 1
                    draw_map(z, map_layers=m_l)
                if event.key == pygame.K_UP:
                    draw_map(z, (0, 1), map_layers=m_l)
                if event.key == pygame.K_DOWN:
                    draw_map(z, (0, -1), map_layers=m_l)
                if event.key == pygame.K_LEFT:
                    draw_map(z, (-1, 0), map_layers=m_l)
                if event.key == pygame.K_RIGHT:
                    draw_map(z, (1, 0), map_layers=m_l)

                if event.key == pygame.K_m:
                    m_l = 'map'
                    draw_map(z, map_layers=m_l)
                if event.key == pygame.K_s:
                    m_l = 'sat'
                    draw_map(z, map_layers=m_l)
                if event.key == pygame.K_h:
                    m_l = 'sat,skl'
                    draw_map(z, map_layers=m_l)
    pygame.quit()

    # Удаляем за собой файл с изображением.
    os.remove(map_file)


if __name__ == '__main__':
    coords = (37.601735, 55.729949)
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    size_map = 10
    layer_name = 'sat'
    draw_map(size_map, map_layers=layer_name)
    move_map(size_map, m_l=layer_name)
