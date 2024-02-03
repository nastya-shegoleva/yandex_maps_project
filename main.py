import os
import sys

import pygame
import requests


def draw_map(size):
    global map_file
    zoom = size
    coords = "55.530887,55.703118"
    map_request = "https://static-maps.yandex.ru/1.x/?ll=" + coords + "&"
    map_request += "z=" + str(zoom) + "&l=sat"
    response = requests.get(map_request)
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
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
