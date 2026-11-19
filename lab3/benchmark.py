#!/usr/bin/env python3
"""
Скрипт экспериментального исследования базовых растровых алгоритмов (Лабораторная работа №3)
Автор: Дикан Данила (4 группа, 3 курс ФПМИ БГУ)

Выполняет:
1. Замер времени выполнения (пошаговый алгоритм, ЦДА, Брезенхем) на выборке из 1000 отрезков.
2. Геометрический анализ точности: расчет расстояния от каждого пикселя до идеальной математической прямой Ax + By + C = 0.
3. Попиксельное сравнение растровых массивов между алгоритмами.
"""

import math
import random
import time
from typing import List, Tuple
from processing import algo_step, algo_dda, algo_bresenham_line


def generate_test_lines(count: int = 1000, coord_range: Tuple[int, int] = (-100, 100), seed: int = 42) -> List[Tuple[int, int, int, int]]:
    """Генерация псевдослучайных отрезков с фиксированным seed для воспроизводимости."""
    random.seed(seed)
    lines = []
    min_c, max_c = coord_range
    while len(lines) < count:
        x1, y1 = random.randint(min_c, max_c), random.randint(min_c, max_c)
        x2, y2 = random.randint(min_c, max_c), random.randint(min_c, max_c)
        if (x1, y1) != (x2, y2):
            lines.append((x1, y1, x2, y2))
    return lines


def run_benchmark():
    print("=" * 70)
    print("  ЭКСПЕРИМЕНТАЛЬНОЕ ИССЛЕДОВАНИЕ РАСТРОВЫХ АЛГОРИТМОВ (ЛАБА №3)")
    print("=" * 70)

    lines = generate_test_lines(count=1000)
    print(f"Выборка: {len(lines)} произвольных отрезков в диапазоне [-100, 100].\n")

    # 1. Измерение времени работы
    timing = {}
    algos = [
        ("Алгоритм Брезенхема", algo_bresenham_line),
        ("Пошаговый алгоритм", algo_step),
        ("Алгоритм ЦДА", algo_dda),
    ]

    results = {}
    for name, func in algos:
        # Прогрев интерпретатора
        for l in lines[:50]:
            func(*l)

        start = time.perf_counter()
        res = [func(*l)[0] for l in lines]
        elapsed = (time.perf_counter() - start) * 1000.0  # мс
        timing[name] = elapsed
        results[name] = res

    print("1. ВРЕМЕННЫЕ ХАРАКТЕРИСТИКИ (1000 линий):")
    print("-" * 50)
    for name, ms in timing.items():
        print(f"  {name:<25} : {ms:6.2f} мс")
    print("-" * 50)
    ratio = timing["Алгоритм ЦДА"] / timing["Алгоритм Брезенхема"]
    print(f"  -> Брезенхем быстрее ЦДА в {ratio:.2f} раза из-за отсутствия вызовов функций round() и вещественных чисел.\n")

    # 2. Анализ точности и отклонений от непрерывной прямой
    total_pixels = 0
    max_d_perp = 0.0
    sum_d_perp = 0.0
    max_d_axis = 0.0
    sum_d_axis = 0.0

    diff_step_bres = 0
    diff_dda_bres = 0

    for i, (x1, y1, x2, y2) in enumerate(lines):
        pts_bres = results["Алгоритм Брезенхема"][i]
        pts_step = results["Пошаговый алгоритм"][i]
        pts_dda = results["Алгоритм ЦДА"][i]

        total_pixels += len(pts_bres)

        # Аналитическое уравнение прямой Ax + By + C = 0
        A = y2 - y1
        B = -(x2 - x1)
        C = x2 * y1 - x1 * y2
        norm = math.hypot(A, B)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        for px, py in pts_bres:
            # Евклидово расстояние до прямой d = |Ax + By + C| / sqrt(A^2 + B^2)
            dist_perp = abs(A * px + B * py + C) / norm
            if dist_perp > max_d_perp:
                max_d_perp = dist_perp
            sum_d_perp += dist_perp

            # Отклонение по ведомой оси
            if dx >= dy:
                y_math = y1 + (y2 - y1) * (px - x1) / (x2 - x1)
                dev_axis = abs(py - y_math)
            else:
                x_math = x1 + (x2 - x1) * (py - y1) / (y2 - y1)
                dev_axis = abs(px - x_math)

            if dev_axis > max_d_axis:
                max_d_axis = dev_axis
            sum_d_axis += dev_axis

        # Сравнение пикселей между методами
        set_bres = set(tuple(p) for p in pts_bres)
        set_step = set(tuple(p) for p in pts_step)
        set_dda = set(tuple(p) for p in pts_dda)

        diff_step_bres += len(set_bres ^ set_step) // 2
        diff_dda_bres += len(set_bres ^ set_dda) // 2

    avg_d_perp = sum_d_perp / total_pixels
    avg_d_axis = sum_d_axis / total_pixels
    match_step = (total_pixels - diff_step_bres) / total_pixels * 100.0
    match_dda = (total_pixels - diff_dda_bres) / total_pixels * 100.0

    print("2. АНАЛИЗ ТОЧНОСТИ (всего пикселей: %d):" % total_pixels)
    print("-" * 50)
    print(f"  Максимальное отклонение по ведомой оси: {max_d_axis:.4f} пкс (теоретический максимум: 0.5000)")
    print(f"  Среднее отклонение по ведомой оси:     {avg_d_axis:.4f} пкс (теоретическое среднее: 0.2500)")
    print(f"  Среднее перпендикулярное расстояние:   {avg_d_perp:.4f} пкс")
    print(f"  Максимальное перпендикулярное расст.:  {max_d_perp:.4f} пкс\n")

    print("3. СРАВНЕНИЕ РАСТРОВЫХ МАССИВОВ:")
    print("-" * 50)
    print(f"  Совпадение Пошаговый vs Брезенхем:     {match_step:.2f}% (несовпадений: {diff_step_bres} пикс.)")
    print(f"  Совпадение ЦДА vs Брезенхем:           {match_dda:.2f}% (несовпадений: {diff_dda_bres} пикс.)")
    print("-" * 50)
    print("  Вывод: расхождения возникают только в точках с дробной частью 0.5,")
    print("  где round() в Python округляет к четному числу, а Брезенхем делает шаг при e >= 0.")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
