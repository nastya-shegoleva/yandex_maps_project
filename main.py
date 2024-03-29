import pygame
import requests
import os

# Константы для окна отображения карты
WIDTH = 1000
HEIGHT = 450

# Константы для серверов поиска и отображения карты Yandex
GEOCODE_SERVER = "http://geocode-maps.yandex.ru/1.x/"
STATIC_MAP_SERVER = "https://static-maps.yandex.ru/1.x/"

# Константы для API ключа и размера экрана
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
SCREEN_SIZE = (WIDTH, HEIGHT)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class MapWindow:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.fine_print = pygame.font.Font(None, 20)
        self.search_text = ""
        self.full_address = []
        self.lst_coords = {'pt=': []}
        self.latitude = 55.755864
        self.longitude = 37.617698
        self.zoom = 10
        self.map_type = "sat"
        self.flag_mailing_address = False
        self.value_mailing_address = ''
        self.flag = False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.zoom_in()
                    elif event.key == pygame.K_2:
                        self.zoom_out()
                    elif event.key == pygame.K_UP:
                        self.move_up()
                    elif event.key == pygame.K_DOWN:
                        self.move_down()
                    elif event.key == pygame.K_LEFT:
                        self.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.move_right()

                    elif event.key == pygame.K_RETURN:
                        self.search()

                if event.type == pygame.KEYDOWN and event.key != pygame.K_RETURN:
                    if event.key == pygame.K_BACKSPACE:
                        self.search_text = self.search_text[:-1]
                    else:
                        self.search_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # смена отображения типов карты
                    if 880 <= event.pos[0] <= 910 and 10 <= event.pos[1] <= 40:
                        self.map_type_scheme()
                    elif 920 <= event.pos[0] <= 950 and 10 <= event.pos[1] <= 40:
                        self.map_type_satellite()
                    elif 960 <= event.pos[0] <= 990 and 10 <= event.pos[1] <= 40:
                        self.map_type_hybrid()

                    # сброс точки и адреса объекта
                    elif 340 <= event.pos[0] <= 370 and 20 <= event.pos[1] <= 50:
                        self.reset_coords()

                    # отображение почтового адреса объекта
                    elif 230 <= event.pos[0] <= 260 and 65 <= event.pos[1] <= 95:
                        self.mailing_address()

            self.draw_map()
            self.draw_search_input()
            pygame.display.flip()
            self.clock.tick(40)

        pygame.quit()

    def search(self):
        self.full_address = []
        self.lst_coords['pt='] = []
        # Отправляем запрос для поиска объекта по API карт
        params = {
            "geocode": self.search_text,
            "apikey": API_KEY,
            "format": "json"
        }

        response = requests.get(GEOCODE_SERVER, params=params)

        if response.status_code == 200:
            data = response.json()

            if data["response"]["GeoObjectCollection"]["featureMember"]:
                # Проверяем, есть ли результаты поиска
                result = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                self.full_address.append(f'{result["metaDataProperty"]["GeocoderMetaData"]["text"]}')

                try:
                    self.value_mailing_address = result["metaDataProperty"]["GeocoderMetaData"]['Address'][
                        'postal_code']
                    self.flag = True
                except:
                    self.flag = False

                pos = result["Point"]["pos"]
                self.longitude, self.latitude = map(float, pos.split())
                self.lst_coords['pt='].append(
                    (pos.split()[0] + ',', pos.split()[1] + ',', 'pm2rdl'))
                # Позиционируем карту на центральную точку объекта
                self.update_map()

    def zoom_in(self):
        # Увеличиваем масштаб отображения карты
        self.zoom += 1
        self.update_map()

        if self.zoom > 19:
            self.zoom = 19

    def zoom_out(self):
        # Уменьшаем масштаб отображения карты
        self.zoom -= 1
        self.update_map()
        if self.zoom < 2.5:
            self.zoom = 2.5

    def move_up(self):
        if self.latitude > 180:
            self.latitude -= 360
        # Перемещаем карту вверх
        self.latitude += self.get_coordinate_step()
        self.update_map()

    def move_down(self):
        if self.latitude < -180:
            self.latitude += 360
        # Перемещаем карту вниз
        self.latitude -= self.get_coordinate_step()
        self.update_map()

    def move_left(self):
        # Перемещаем карту влево
        if self.longitude < -85:
            self.longitude = -85
        self.longitude -= self.get_coordinate_step()
        self.update_map()

    def move_right(self):
        # Перемещаем карту вправо
        if self.longitude > 85:
            self.longitude = 85
        self.longitude += self.get_coordinate_step()
        self.update_map()

    def map_type_scheme(self):
        self.map_type = 'map'
        self.update_map()

    def map_type_satellite(self):
        self.map_type = 'sat'
        self.update_map()

    def map_type_hybrid(self):
        self.map_type = 'sat,skl'
        self.update_map()

    def img(self, path_img):
        return pygame.transform.scale(pygame.image.load(f'image/{path_img}'), (30, 30))

    def addMetcyToMap(self):
        res = ''
        if self.lst_coords['pt=']:
            res += '&pt=' + ''.join(list(map(''.join, self.lst_coords['pt='])))
        return res

    def reset_coords(self):
        self.lst_coords['pt='] = []
        self.search_text = ''
        self.full_address.clear()
        self.update_map()

    def mailing_address(self):
        self.flag_mailing_address = not self.flag_mailing_address
        if self.flag:
            if self.flag_mailing_address:
                self.full_address.append(', ' + self.value_mailing_address)
            else:
                self.full_address = self.full_address[:-1]
        else:
            pass

    def update_map(self):
        # Обновляем отображение карты
        map_url = f"{STATIC_MAP_SERVER}?ll={self.longitude},{self.latitude}&z={self.zoom}&l={self.map_type}" + \
                  f'{self.addMetcyToMap()}'

        response = requests.get(map_url)
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)

        self.screen.fill('darkseagreen2')

        self.screen.blit(pygame.image.load(map_file), (400, 0))

        self.screen.blit(self.img('scheme.png'), (880, 10))
        self.screen.blit(self.img('sat.png'), (920, 10))
        self.screen.blit(self.img('hubrid.png'), (960, 10))
        os.remove(map_file)

    def draw_search_input(self):
        input_rect = pygame.Rect(20, 20, 350, 32)
        text_surface = self.font.render(self.search_text, True, (0, 0, 0))
        pygame.draw.rect(self.screen, WHITE, input_rect)
        self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 9))
        self.screen.blit(self.img('close.png'), (340, 20))

        text = self.font.render('Полный адрес объекта:', True, (0, 0, 0))
        self.screen.blit(text, (20, 70))

        address = ' '.join(self.full_address)
        text_full_address_b_50_sumbol = self.fine_print.render(address[:50], True, (0, 0, 0))
        text_full_address_a_50_sumbol = self.fine_print.render(address[50:], True, (0, 0, 0))
        self.screen.blit(text_full_address_b_50_sumbol, (20, 100))
        self.screen.blit(text_full_address_a_50_sumbol, (20, 130))

        self.screen.blit(self.img('mail_box.png'), (230, 65))

        input_rect.w = max(100, text_surface.get_width() + 10)

    def draw_map(self):
        if hasattr(self, 'map_surface'):
            self.screen.blit(self.map_surface, (0, 0))

    def get_coordinate_step(self):
        # Вычисляем шаг смещения координат в зависимости от масштаба
        return (2 ** (19 - self.zoom)) * 0.002


if __name__ == '__main__':
    map_window = MapWindow()
    map_window.update_map()
    map_window.run()
