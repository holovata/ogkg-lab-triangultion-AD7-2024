class Edge:
    """Орієнтоване ребро: start_point -> end_point"""

    def __init__(self, start_point, end_point):
        self.start_point = start_point  # Початкова точка ребра
        self.end_point = end_point  # Кінцева точка ребра
        self.next_edge_ccw = None  # Наступне ребро в кільці (проти годинникової стрілки)
        self.prev_edge_cw = None  # Попереднє ребро в кільці (за годинниковою стрілкою)
        self.symmetric_edge = None  # Симетричний відповідник цього ребра
        self.to_be_deleted = None

    def __str__(self):
        s = str(self.start_point) + ', ' + str(self.end_point)  # Формуємо рядок з координатами початкової та кінцевої точок
        if self.to_be_deleted is None:
            return s  # Якщо немає додаткових даних, повертаємо рядок з координатами
        else:
            return s + ' ' + str(self.to_be_deleted)  # Якщо є додаткові дані, додаємо їх до рядка

