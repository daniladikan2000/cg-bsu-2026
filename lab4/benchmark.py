#!/usr/bin/env python3
"""
Скрипт контрольного исследования алгоритмов отсечения (Лабораторная работа №4)
Автор: Дикан Данила (4 группа, 3 курс ФПМИ БГУ)

Выполняет:
1. Отсечение контрольного набора отрезков прямоугольным окном [0, 20] x [0, 20] (алгоритм средней точки).
2. Отсечение контрольного набора отрезков выпуклым шестиугольником (алгоритм Кируса-Бека).
3. Замер времени выполнения обоих методов на 1000 отрезках.
"""

import math
import random
import time
from processing import clip_midpoint, clip_cyrus_beck


def run_benchmark():
    print("=" * 70)
    print("  ИССЛЕДОВАНИЕ АЛГОРИТМОВ ОТСЕЧЕНИЯ (ЛАБА №4)")
    print("=" * 70)

    # Контрольный набор отрезков из задания
    rect = (0.0, 0.0, 20.0, 20.0)
    control_lines = [
        (-15.0, -15.0, 15.0, 15.0),
        (-5.0, 25.0, 25.0, -5.0),
        (2.0, 5.0, 18.0, 5.0),
        (-25.0, 0.0, -5.0, 0.0),
        (25.0, 25.0, 35.0, 35.0),
    ]

    print("1. РЕЗУЛЬТАТЫ ОТСЕЧЕНИЯ ПРЯМОУГОЛЬНЫМ ОКНОМ [0, 20] x [0, 20]:")
    print("-" * 65)
    print(f"  {'#':<3} {'Исходный отрезок':<26} {'Результат отсечения':<30}")
    print("-" * 65)
    for i, line in enumerate(control_lines, 1):
        res = clip_midpoint(*line, *rect)
        orig_str = f"({line[0]:.0f}, {line[1]:.0f}) -> ({line[2]:.0f}, {line[3]:.0f})"
        if res and res.get("clipped"):
            c = res["clipped"]
            res_str = f"({c[0][0]:.1f}, {c[0][1]:.1f}) -> ({c[1][0]:.1f}, {c[1][1]:.1f})"
        else:
            res_str = "Полностью отброшен"
        print(f"  {i:<3} {orig_str:<26} {res_str:<30}")
    print("-" * 65 + "\n")

    # Контрольный выпуклый шестиугольник
    polygon = [
        (-15.0, -10.0),
        (0.0, -18.0),
        (15.0, -10.0),
        (15.0, 10.0),
        (0.0, 18.0),
        (-15.0, 10.0),
    ]
    print("2. РЕЗУЛЬТАТЫ ОТСЕЧЕНИЯ ВЫПУКЛЫМ ШЕСТИУГОЛЬНИКОМ (КИРУС-БЕК):")
    print("-" * 65)
    for i, line in enumerate(control_lines, 1):
        res = clip_cyrus_beck(*line, polygon)
        orig_str = f"({line[0]:.0f}, {line[1]:.0f}) -> ({line[2]:.0f}, {line[3]:.0f})"
        if res and res.get("clipped"):
            c = res["clipped"]
            res_str = f"({c[0][0]:.1f}, {c[0][1]:.1f}) -> ({c[1][0]:.1f}, {c[1][1]:.1f})"
        else:
            res_str = "Полностью отброшен"
        print(f"  {i:<3} {orig_str:<26} {res_str:<30}")
    print("-" * 65 + "\n")

    # Сравнение времени на 1000 линий
    random.seed(42)
    test_lines = []
    for _ in range(1000):
        x1 = random.uniform(-40, 60)
        y1 = random.uniform(-40, 60)
        x2 = random.uniform(-40, 60)
        y2 = random.uniform(-40, 60)
        test_lines.append((x1, y1, x2, y2))

    t0 = time.perf_counter()
    for l in test_lines:
        clip_midpoint(*l, *rect)
    time_midpoint = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    for l in test_lines:
        clip_cyrus_beck(*l, polygon)
    time_cyrus = (time.perf_counter() - t0) * 1000.0

    print("3. ВРЕМЯ РАБОТЫ НА 1000 ЛИНИЯХ:")
    print("-" * 50)
    print(f"  Алгоритм средней точки : {time_midpoint:6.2f} мс (~16 делений на отрезок)")
    print(f"  Алгоритм Кируса-Бека   : {time_cyrus:6.2f} мс (прямой расчет параметров t)")
    print("-" * 50)
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
