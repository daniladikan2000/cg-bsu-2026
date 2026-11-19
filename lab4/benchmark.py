import math
import random
import time
from processing import clip_midpoint, clip_cyrus_beck


def run_benchmark():
    rect = (0.0, 0.0, 20.0, 20.0)
    control_lines = [
        (-15.0, -15.0, 15.0, 15.0),
        (-5.0, 25.0, 25.0, -5.0),
        (2.0, 5.0, 18.0, 5.0),
        (-25.0, 0.0, -5.0, 0.0),
        (25.0, 25.0, 35.0, 35.0),
    ]

    print("РЕЗУЛЬТАТЫ ОТСЕЧЕНИЯ ПРЯМОУГОЛЬНЫМ ОКНОМ [0, 20] x [0, 20]:")
    for i, line in enumerate(control_lines, 1):
        res = clip_midpoint(*line, *rect)
        orig_str = f"({line[0]:.0f}, {line[1]:.0f}) -> ({line[2]:.0f}, {line[3]:.0f})"
        if res and res.get("clipped"):
            c = res["clipped"]
            res_str = f"({c[0][0]:.1f}, {c[0][1]:.1f}) -> ({c[1][0]:.1f}, {c[1][1]:.1f})"
        else:
            res_str = "Полностью отброшен"
        print(f"  {i} {orig_str} -> {res_str}")
    print()

    polygon = [
        (-15.0, -10.0),
        (0.0, -18.0),
        (15.0, -10.0),
        (15.0, 10.0),
        (0.0, 18.0),
        (-15.0, 10.0),
    ]
    print("РЕЗУЛЬТАТЫ ОТСЕЧЕНИЯ ВЫПУКЛЫМ ШЕСТИУГОЛЬНИКОМ (КИРУС-БЕК):")
    for i, line in enumerate(control_lines, 1):
        res = clip_cyrus_beck(*line, polygon)
        orig_str = f"({line[0]:.0f}, {line[1]:.0f}) -> ({line[2]:.0f}, {line[3]:.0f})"
        if res and res.get("clipped"):
            c = res["clipped"]
            res_str = f"({c[0][0]:.1f}, {c[0][1]:.1f}) -> ({c[1][0]:.1f}, {c[1][1]:.1f})"
        else:
            res_str = "Полностью отброшен"
        print(f"  {i} {orig_str} -> {res_str}")
    print()

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

    print("ВРЕМЯ РАБОТЫ (1000 ЛИНИЙ):")
    print(f"  Алгоритм средней точки : {time_midpoint:6.2f} мс")
    print(f"  Алгоритм Кируса-Бека   : {time_cyrus:6.2f} мс")


if __name__ == "__main__":
    run_benchmark()
