import os
import sys

import pygame
import requests

coords = (55.530887, 55.703118)


def draw_map(size, dir=(0, 0)):
    global map_file, coords
    current_lattitude, current_longitude = coords

    zoom = size
    x_move, y_move = dir
    rect = 2 ** (17 - z) * 0.002
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
    map_request += "z=" + str(zoom) + "&l=sat"
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
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()


z = 5
draw_map(z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                z += 1
                if z > 20:
                    z = 20
                draw_map(z)
            if event.key == pygame.K_PAGEDOWN:
                z -= 1
                if z < 1:
                    z = 1
                draw_map(z)
            if event.key == pygame.K_UP:
                draw_map(z, (0, 1))
            if event.key == pygame.K_DOWN:
                draw_map(z, (0, -1))
            if event.key == pygame.K_LEFT:
                draw_map(z, (-1, 0))
            if event.key == pygame.K_RIGHT:
                draw_map(z, (1, 0))
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
