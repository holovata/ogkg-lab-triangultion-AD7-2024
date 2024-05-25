import numpy as np
import pygame

from visualisation_configuration import *
import visualisation_configuration as vis_config


class TriangulationVisualizer:
    def __init__(self):
        self.points_list = []  # Список для зберігання точок
        self.edges_list = []  # Список для зберігання ребер
        self.add_corner_points()  # Додаємо точки по кутах області

    def add_corner_points(self):
        """Додає точки по кутах області"""
        self.points_list = [
            (0, 0),
            (0, vis_config.window_height),  # Нижній лівий кут
            (vis_config.window_width - 250, 0),  # Верхній правий кут (враховуємо ширину панелі)
            (vis_config.window_width - 250, vis_config.window_height)  # Нижній правий кут (враховуємо ширину панелі)
        ]
        self.edges_list = []  # Очищуємо список ребер

    def draw(self, window_surface):
        """Малює точки та ребра на екрані"""
        window_surface.fill(BACKGROUND_COLOR)  # Заповнюємо фон світло-сірим кольором

        # Малюємо ребра
        for edge in self.edges_list:
            pygame.draw.line(window_surface, LINE_COLOR, edge.start_point, edge.end_point, 1)  # Чорні лінії

        # Малюємо точки
        for point in self.points_list:
            pygame.draw.circle(window_surface, POINT_COLOR, (int(point[0]), int(point[1])), POINT_SIZE)  # Червоні точки

        pygame.display.flip()  # Оновлюємо дисплей

    def remove_point(self, position):
        """Видаляє точку, найближчу до позиції (position), якщо вона існує"""
        removal_threshold = POINT_SIZE * 2  # Допустима область для видалення точки
        for point in self.points_list:
            if abs(point[0] - position[0]) < removal_threshold and abs(point[1] - position[1]) < removal_threshold:
                self.points_list.remove(point)
                break
