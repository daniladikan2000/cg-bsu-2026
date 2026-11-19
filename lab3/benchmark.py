import math
import random
import time
from typing import List, Tuple
from processing import algo_step, algo_dda, algo_bresenham_line


def generate_test_lines(count: int = 1000, coord_range: Tuple[int, int] = (-100, 100), seed: int = 42) -> List[Tuple[int, int, int, int]]:
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
    lines = generate_test_lines(count=1000)

    timing = {}
    algos = [
        ("Алгоритм Брезенхема", algo_bresenham_line),
        ("Пошаговый алгоритм", algo_step),
        ("Алгоритм ЦДА", algo_dda),
    ]

    results = {}
    for name, func in algos:
        for l in lines[:50]:
            func(*l)

        start = time.perf_counter()
        res = [func(*l)[0] for l in lines]
        elapsed = (time.perf_counter() - start) * 1000.0
        timing[name] = elapsed
        results[name] = res

    print("ВРЕМЕННЫЕ ХАРАКТЕРИСТИКИ (1000 линий):")
    for name, ms in timing.items():
        print(f"  {name:<25} : {ms:6.2f} мс")
    print()

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

        A = y2 - y1
        B = -(x2 - x1)
        C = x2 * y1 - x1 * y2
        norm = math.hypot(A, B)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        for px, py in pts_bres:
            dist_perp = abs(A * px + B * py + C) / norm
            if dist_perp > max_d_perp:
                max_d_perp = dist_perp
            sum_d_perp += dist_perp

            if dx >= dy:
                y_math = y1 + (y2 - y1) * (px - x1) / (x2 - x1)
                dev_axis = abs(py - y_math)
            else:
                x_math = x1 + (x2 - x1) * (py - y1) / (y2 - y1)
                dev_axis = abs(px - x_math)

            if dev_axis > max_d_axis:
                max_d_axis = dev_axis
            sum_d_axis += dev_axis

        set_bres = set(tuple(p) for p in pts_bres)
        set_step = set(tuple(p) for p in pts_step)
        set_dda = set(tuple(p) for p in pts_dda)

        diff_step_bres += len(set_bres ^ set_step) // 2
        diff_dda_bres += len(set_bres ^ set_dda) // 2

    avg_d_perp = sum_d_perp / total_pixels
    avg_d_axis = sum_d_axis / total_pixels
    match_step = (total_pixels - diff_step_bres) / total_pixels * 100.0
    match_dda = (total_pixels - diff_dda_bres) / total_pixels * 100.0

    print(f"АНАЛИЗ ТОЧНОСТИ (всего пикселей: {total_pixels}):")
    print(f"  Максимальное отклонение по оси: {max_d_axis:.4f} пкс")
    print(f"  Среднее отклонение по оси:      {avg_d_axis:.4f} пкс")
    print(f"  Среднее перпендикулярное:       {avg_d_perp:.4f} пкс")
    print(f"  Максимальное перпендикулярное:  {max_d_perp:.4f} пкс\n")

    print("СРАВНЕНИЕ РАСТРОВЫХ МАССИВОВ:")
    print(f"  Пошаговый vs Брезенхем: {match_step:.2f}% (несовпадений: {diff_step_bres})")
    print(f"  ЦДА vs Брезенхем:       {match_dda:.2f}% (несовпадений: {diff_dda_bres})")


if __name__ == "__main__":
    run_benchmark()
