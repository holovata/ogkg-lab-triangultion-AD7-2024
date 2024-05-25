import numpy as np
import pygame
import pygame_gui
from pygame.locals import *

from visualisation_configuration import *
import visualisation_configuration as vis_config

from triangulation_visualizer import TriangulationVisualizer
from delaunay_triangulation import compute_delaunay_edges


def wrap_text(text, font, max_width):
    """ Wrap text to fit within a specified width when rendered with the given font. """
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] > max_width:
            lines.append(current_line)
            current_line = word + ' '
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    return lines


def generate_random_points(width, height, num_points):
    """Повертає масив випадково згенерованих точок"""
    points_x = np.random.randint(0, width, num_points, dtype=np.int64)  # Випадкові координати x
    points_y = np.random.randint(0, height, num_points, dtype=np.int64)  # Випадкові координати y
    return np.asarray(list(zip(points_x, points_y)), dtype=np.float64)  # Об'єднуємо координати в масив точок


def setup_pygame():
    """Налаштування основного вікна та параметрів pygame"""
    pygame.init()
    pygame.display.set_caption('Holovata MI-31 OGKG Lab')
    vis_config.window_width = WINDOW_WIDTH + 250  # Додаємо місце для панелі
    vis_config.window_height = WINDOW_HEIGHT
    vis_config.window_mode = WINDOW_MODE
    vis_config.window = pygame.display.set_mode([vis_config.window_width, vis_config.window_height], vis_config.window_mode)
    vis_config.window.fill(BACKGROUND_COLOR)  # Заповнюємо фон світло-сірим кольором
    vis_config.background = vis_config.window.copy()  # Копіюємо фон для подальшого використання

    return pygame_gui.UIManager((vis_config.window_width, vis_config.window_height)), pygame.time.Clock()


def create_ui_elements(manager):
    """Створення елементів інтерфейсу на боковій панелі"""
    panel_rect = pygame.Rect(vis_config.window_width - 250, 0, 250, vis_config.window_height)
    panel = pygame_gui.elements.UIPanel(relative_rect=panel_rect, manager=manager)

    gen_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, 50), (200, 50)),
                                              text='Згенерувати рандомні точки',
                                              manager=manager,
                                              container=panel)
    run_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, 120), (200, 50)),
                                              text='Запустити алгоритм',
                                              manager=manager,
                                              container=panel)
    clear_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, 190), (200, 50)),
                                                text='Очистити область',
                                                manager=manager,
                                                container=panel)

    point_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((25, 260), (200, 50)),
                                                      manager=manager,
                                                      container=panel)
    point_input.set_text("100")

    error_message = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((25, 320), (200, 100)),
                                                text='',
                                                manager=manager,
                                                container=panel,
                                                object_id='error_label')

    return panel, gen_button, run_button, clear_button, point_input, error_message


def handle_ui_events(event, gen_button, run_button, clear_button, point_input, error_message, mesh, auto_run, font):
    """Обробка подій інтерфейсу користувача"""
    if event.ui_element == gen_button:
        auto_run = False
        try:
            num_points = int(point_input.get_text())
            if num_points < 1 or num_points > 10000:
                raise ValueError("Кількість точок має бути між 1 та 10000")
            error_message.set_text('')
            mesh.add_corner_points()
            mesh.points_list += generate_random_points(vis_config.window_width - 250, vis_config.window_height, num_points).tolist()
            mesh.edges_list = []
            mesh.draw(vis_config.window)
        except ValueError as e:
            wrapped_text = '\n'.join(wrap_text(str(e), font, 200))  # Wrap text
            error_message.set_text(wrapped_text)
    elif event.ui_element == run_button or event.ui_element == clear_button:
        error_message.set_text('')
        if event.ui_element == run_button:
            auto_run = True
            if len(mesh.points_list) >= 2:
                mesh.edges_list = compute_delaunay_edges(np.array(mesh.points_list, dtype=np.float64))
                mesh.draw(vis_config.window)
            else:
                error_message.set_text("Недостатньо точок для запуску алгоритму")
        elif event.ui_element == clear_button:
            auto_run = False
            mesh.add_corner_points()
            mesh.draw(vis_config.window)
    return auto_run


def handle_mouse_events(event, mesh, auto_run):
    """Обробка подій миші"""
    pos = pygame.mouse.get_pos()
    if pos[0] < vis_config.window_width - 250:  # Перевірка, щоб точка не додавалась/видалялась на панелі
        if event.button == 1:  # Ліва кнопка миші
            mesh.points_list.append(pos)
        elif event.button == 3:  # Права кнопка миші
            mesh.remove_point(pos)
        if auto_run:
            if len(mesh.points_list) >= 2:
                mesh.edges_list = compute_delaunay_edges(np.array(mesh.points_list, dtype=np.float64))
            else:
                mesh.edges_list = []
        else:
            mesh.edges_list = []
        mesh.draw(vis_config.window)


def main():
    manager, clock = setup_pygame()
    panel, gen_button, run_button, clear_button, point_input, error_message = create_ui_elements(manager)

    # Define a font for text wrapping
    font = pygame.font.Font(None, 24)

    vis_config.mesh = TriangulationVisualizer()
    vis_config.mesh.draw(vis_config.window)

    auto_run = False

    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                return
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                auto_run = handle_ui_events(event, gen_button, run_button, clear_button, point_input, error_message, vis_config.mesh, auto_run, font)
            if event.type == MOUSEBUTTONDOWN:
                handle_mouse_events(event, vis_config.mesh, auto_run)

            manager.process_events(event)
        manager.update(time_delta)
        manager.draw_ui(vis_config.window)
        pygame.display.update()


if __name__ == '__main__':
    main()

