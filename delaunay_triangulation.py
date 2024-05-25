import numpy as np

from edge import Edge

edges_list = []


def compute_delaunay_edges(points):
    """Повертає список ребер, які утворюють триангуляцію Делоне для набору точок"""
    if len(points) < 2:
        print("Має бути щонайменше дві точки.")  # Перевірка, що набір точок містить щонайменше дві точки
        return

    global edges_list
    edges_list = []  # Ініціалізація порожнього списку для зберігання ребер
    points = np.asarray(points, dtype=np.float64)  # Перетворення списку точок у масив numpy з типом даних float64

    # Сортуємо точки за координатою x, координата y є вирішувачем при рівних x
    points.view(dtype=[('f0', points.dtype), ('f1', points.dtype)]).sort(order=['f0', 'f1'], axis=0)

    # Видаляємо дублікати
    duplicate_indices = [i for i in range(1, len(points)) if points[i - 1][0] == points[i][0] and points[i - 1][1] == points[i][1]]
    if duplicate_indices:
        points = np.delete(points, duplicate_indices, 0)  # Видалення дублікатів точок

    delaunay_triangulate(points)  # Виклик функції для виконання триангуляції Делоне
    edges_list = [edge for edge in edges_list if edge.to_be_deleted is None]  # Очищення сміття, видалення зайвих ребер
    return edges_list  # Повернення списку ребер


def delaunay_triangulate(points):
    """Обчислює триангуляцію Делоне для набору точок і повертає два ребра (left_edge і right_edge).
    left_edge: перше ребро проти годинникової стрілки, що належить ОО та виходить з найлівішої точки ОО
    right_edge: перше ребро за годинниковою стрілкою, що належить ОО та виходить з найправішої точки ОО"""

    if len(points) == 2:
        # Якщо у нас дві точки, створюємо одне ребро між ними
        edge_a = create_new_edge(points[0], points[1])
        return edge_a, edge_a.symmetric_edge  # Повертаємо ребро та його симетричне ребро

    elif len(points) == 3:
        return triangulate_three_points(points)  # Виклик функції для обробки випадку з трьома точками

    else:
        # Розділяємо список points на дві частини
        midpoint = (len(points) + 1) // 2  # Обчислення середини масиву
        left_points, right_points = points[:midpoint], points[midpoint:]  # Розділення масиву на ліву (left_points) та праву (right_points) частини
        left_outer_edge, left_inner_edge = delaunay_triangulate(left_points)  # Рекурсивний виклик для лівої частини
        right_inner_edge, right_outer_edge = delaunay_triangulate(right_points)  # Рекурсивний виклик для правої частини

        # Обчислюємо верхню спільну опорну лівих і правих точок
        left_inner_edge, right_inner_edge = compute_upper_common_tangent(left_inner_edge, right_inner_edge)

        # Створюємо перше ребро base_edge, яке з'єднує right_inner_edge.start_point з left_inner_edge.start_point
        base_edge = connect_edges(left_inner_edge.symmetric_edge, right_inner_edge)

        # Коригуємо left_outer_edge і right_outer_edge, якщо необхідно
        if left_inner_edge.start_point[0] == left_outer_edge.start_point[0] and left_inner_edge.start_point[1] == left_outer_edge.start_point[1]:
            left_outer_edge = base_edge
        if right_inner_edge.start_point[0] == right_outer_edge.start_point[0] and right_inner_edge.start_point[1] == right_outer_edge.start_point[1]:
            right_outer_edge = base_edge.symmetric_edge

        # Об'єднуємо дві частини за допомогою нового ребра base_edge
        merge(left_outer_edge, right_outer_edge, base_edge)
        return left_outer_edge, right_outer_edge  # Повертаємо результуючі ребра лівої та правої частин


def triangulate_three_points(point_set):
    """Обчислює триангуляцію для трьох точок point_set і повертає два ребра"""
    point1, point2, point3 = point_set[0], point_set[1], point_set[2]  # Отримуємо три точки з point_set
    edge_a = create_new_edge(point1, point2)  # Створюємо ребро між point1 та point2
    edge_b = create_new_edge(point2, point3)  # Створюємо ребро між point2 та point3
    splice_edges(edge_a.symmetric_edge, edge_b)  # З'єднуємо симетричне ребро edge_a з edge_b

    # Замкнемо трикутник
    if is_right_of(point3, edge_a):  # Якщо point3 праворуч від ребра edge_a
        connect_edges(edge_b, edge_a)  # З'єднуємо edge_b з edge_a
        return edge_a, edge_b.symmetric_edge  # Повертаємо ребро edge_a та симетричне edge_b
    elif is_left_of(point3, edge_a):  # Якщо point3 ліворуч від ребра edge_a
        edge_c = connect_edges(edge_b, edge_a)  # З'єднуємо edge_b з edge_a і повертаємо нове ребро edge_c
        return edge_c.symmetric_edge, edge_c  # Повертаємо симетричне edge_c і edge_c
    else:  # Якщо три точки колінеарні
        return edge_a, edge_b.symmetric_edge  # Повертаємо ребро edge_a та симетричне edge_b


def compute_upper_common_tangent(leftmost_edge, rightmost_edge):
    """Обчислює верхню спільну опорну двох множин ребер"""
    while True:
        if is_right_of(rightmost_edge.start_point, leftmost_edge):  # Якщо rightmost_edge.start_point праворуч від leftmost_edge
            leftmost_edge = leftmost_edge.symmetric_edge.next_edge_ccw  # Переходимо до наступного ребра з лівого боку
        elif is_left_of(leftmost_edge.start_point, rightmost_edge):  # Якщо leftmost_edge.start_point ліворуч від rightmost_edge
            rightmost_edge = rightmost_edge.symmetric_edge.prev_edge_cw  # Переходимо до попереднього ребра з правого боку
        else:
            break  # Виходимо з циклу, якщо більше немає руху
    return leftmost_edge, rightmost_edge  # Повертаємо скориговані leftmost_edge та rightmost_edge


def merge(leftmost_delaunay_edge, rightmost_delaunay_edge, base_edge):
    """Об'єднує два набори ребер з новим ребром base_edge"""
    while True:
        # Визначаємо перші точки для перевірки правого і лівого кандидатів.
        right_candidate, left_candidate = base_edge.symmetric_edge.next_edge_ccw, base_edge.prev_edge_cw

        # Якщо лівий і правий кандидати недійсні, тоді base_edge є нижньою спільною опорною.
        valid_right_candidate, valid_left_candidate = is_right_of(right_candidate.end_point, base_edge), is_right_of(left_candidate.end_point, base_edge)
        if not (valid_right_candidate or valid_left_candidate):
            break

        # Видаляємо ребра правого кандидата, які не пройшли тест кола.
        if valid_right_candidate:
            while is_right_of(right_candidate.next_edge_ccw.end_point, base_edge) and \
                    is_point_in_circumcircle(base_edge.end_point, base_edge.start_point, right_candidate.end_point, right_candidate.next_edge_ccw.end_point):
                next_right_candidate = right_candidate.next_edge_ccw
                remove_edge(right_candidate)
                right_candidate = next_right_candidate

        # Аналогічно, видаляємо ребра лівого кандидата.
        if valid_left_candidate:
            while is_right_of(left_candidate.prev_edge_cw.end_point, base_edge) and \
                    is_point_in_circumcircle(base_edge.end_point, base_edge.start_point, left_candidate.end_point, left_candidate.prev_edge_cw.end_point):
                next_left_candidate = left_candidate.prev_edge_cw
                remove_edge(left_candidate)
                left_candidate = next_left_candidate

        # Наступне перехресне ребро має бути з'єднано або з left_candidate.end_point, або з right_candidate.end_point.
        # Якщо обидва дійсні, тоді обираємо відповідне використовуючи тест кола.
        if not valid_right_candidate or \
                (valid_left_candidate and is_point_in_circumcircle(right_candidate.end_point, right_candidate.start_point, left_candidate.start_point, left_candidate.end_point)):
            # Додаємо перехресне ребро base_edge від left_candidate до base_edge.end_point.
            base_edge = connect_edges(left_candidate, base_edge.symmetric_edge)
        else:
            # Додаємо перехресне ребро base_edge від base_edge.start_point до right_candidate.end_point
            base_edge = connect_edges(base_edge.symmetric_edge, right_candidate.symmetric_edge)


def is_point_in_circumcircle(point_a, point_b, point_c, point_d):
    """Чи лежить point_d всередині описаного кола навколо трикутника, утвореного точками point_a, point_b, point_c"""
    # Обчислюємо відстані між точкою point_d та точками point_a, point_b, point_c
    distance_a1, distance_a2 = point_a[0] - point_d[0], point_a[1] - point_d[1]
    distance_b1, distance_b2 = point_b[0] - point_d[0], point_b[1] - point_d[1]
    distance_c1, distance_c2 = point_c[0] - point_d[0], point_c[1] - point_d[1]
    # Обчислюємо квадрати відстаней
    squared_distance_a = distance_a1 ** 2 + distance_a2 ** 2
    squared_distance_b = distance_b1 ** 2 + distance_b2 ** 2
    squared_distance_c = distance_c1 ** 2 + distance_c2 ** 2
    # Обчислюємо визначник
    determinant = (distance_a1 * distance_b2 * squared_distance_c +
                   distance_a2 * squared_distance_b * distance_c1 +
                   squared_distance_a * distance_b1 * distance_c2 -
                   (squared_distance_a * distance_b2 * distance_c1 +
                    distance_a1 * squared_distance_b * distance_c2 +
                    distance_a2 * distance_b1 * squared_distance_c))
    return determinant < 0  # Повертаємо True, якщо точка point_d лежить всередині кола


def is_right_of(point, edge):
    """Чи лежить точка point праворуч від лінії, утвореної ребром edge"""
    start_point, end_point = edge.start_point, edge.end_point  # Початкова і кінцева точки ребра edge
    # Обчислюємо визначник для перевірки розташування точки point відносно лінії
    determinant = (start_point[0] - point[0]) * (end_point[1] - point[1]) - (start_point[1] - point[1]) * (end_point[0] - point[0])
    return determinant > 0  # Повертаємо True, якщо точка point праворуч від лінії


def is_left_of(point, edge):
    """Чи лежить точка point ліворуч від лінії, утвореної ребром edge"""
    start_point, end_point = edge.start_point, edge.end_point  # Початкова і кінцева точки ребра edge
    # Обчислюємо визначник для перевірки розташування точки point відносно лінії
    determinant = (start_point[0] - point[0]) * (end_point[1] - point[1]) - (start_point[1] - point[1]) * (end_point[0] - point[0])
    return determinant < 0  # Повертаємо True, якщо точка point ліворуч від лінії


def create_new_edge(start_point, end_point):
    """Створює нове ребро"""
    global edges_list
    edge = Edge(start_point, end_point)  # Створюємо нове ребро від start_point до end_point
    symmetric_edge = Edge(end_point, start_point)  # Створюємо симетричне ребро від end_point до start_point
    edge.symmetric_edge, symmetric_edge.symmetric_edge = symmetric_edge, edge  # Робимо ребра взаємно симетричними
    edge.next_edge_ccw, edge.prev_edge_cw = edge, edge  # Встановлюємо зв'язки для нового ребра
    # Встановлюємо зв'язки для симетричного ребра
    symmetric_edge.next_edge_ccw, symmetric_edge.prev_edge_cw = symmetric_edge, symmetric_edge
    edges_list.append(edge)  # Додаємо нове ребро до списку ребер
    return edge  # Повертаємо нове ребро


def splice_edges(edge_a, edge_b):
    """Об'єднує різні кільця ребер або розриває одне кільце на дві частини"""
    if edge_a == edge_b:
        return  # Об'єднання ребра з самим собою

    # З'єднуємо edge_a.next_edge_ccw з edge_b, і edge_b.next_edge_ccw з edge_a
    edge_a.next_edge_ccw.prev_edge_cw, edge_b.next_edge_ccw.prev_edge_cw = edge_b, edge_a
    # З'єднуємо edge_a з edge_b.next_edge_ccw, і edge_b з edge_a.next_edge_ccw
    edge_a.next_edge_ccw, edge_b.next_edge_ccw = edge_b.next_edge_ccw, edge_a.next_edge_ccw


def connect_edges(edge_a, edge_b):
    """Додає нове ребро new_edge, що з'єднує end_point edge_a зі start_point edge_b"""
    new_edge = create_new_edge(edge_a.end_point, edge_b.start_point)  # Створюємо нове ребро від edge_a.end_point до edge_b.start_point
    splice_edges(new_edge, edge_a.symmetric_edge.prev_edge_cw)  # З'єднуємо нове ребро new_edge з попереднім симетричним ребром edge_a
    splice_edges(new_edge.symmetric_edge, edge_b)  # З'єднуємо симетричне ребро new_edge з edge_b
    return new_edge  # Повертаємо нове ребро


def remove_edge(edge):
    """Видаляє ребро"""
    splice_edges(edge, edge.prev_edge_cw)  # Від'єднуємо ребро edge від його попереднього ребра
    splice_edges(edge.symmetric_edge, edge.symmetric_edge.prev_edge_cw)  # Від'єднуємо симетричне ребро edge від його попереднього ребра
    edge.to_be_deleted, edge.symmetric_edge.to_be_deleted = True, True  # Позначаємо ребро edge і його симетричне ребро як видалені
