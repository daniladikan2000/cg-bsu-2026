import time
from typing import List, Dict, Any, Tuple


def algo_step(x1: int, y1: int, x2: int, y2: int) -> Tuple[List[List[int]], List[Dict[str, Any]]]:
    points = []
    trace = []
    dx, dy = x2 - x1, y2 - y1
    step_num = 0

    if abs(dx) >= abs(dy):
        if dx == 0:
            return [[x1, y1]], [{"step": 0, "x": x1, "y": y1, "calc": f"y={y1:.2f}"}]
        k = dy / dx
        b = y1 - k * x1
        step = 1 if dx > 0 else -1
        x = x1
        while True:
            y_float = k * x + b
            y_int = int(round(y_float))
            points.append([x, y_int])
            trace.append({"step": step_num, "x": x, "y": y_int, "calc": f"y={y_float:.2f}"})
            if x == x2:
                break
            x += step
            step_num += 1
    else:
        if dy == 0:
            return [[x1, y1]], [{"step": 0, "x": x1, "y": y1, "calc": f"x={x1:.2f}"}]
        k = dx / dy
        b = x1 - k * y1
        step = 1 if dy > 0 else -1
        y = y1
        while True:
            x_float = k * y + b
            x_int = int(round(x_float))
            points.append([x_int, y])
            trace.append({"step": step_num, "x": x_int, "y": y, "calc": f"x={x_float:.2f}"})
            if y == y2:
                break
            y += step
            step_num += 1

    return points, trace


def algo_dda(x1: int, y1: int, x2: int, y2: int) -> Tuple[List[List[int]], List[Dict[str, Any]]]:
    points = []
    trace = []
    dx, dy = x2 - x1, y2 - y1
    length = max(abs(dx), abs(dy))
    if length == 0:
        return [[x1, y1]], [{"step": 0, "x": x1, "y": y1, "calc": f"({x1:.1f}, {y1:.1f})"}]

    sx, sy = dx / length, dy / length
    x, y = float(x1), float(y1)
    for i in range(int(length) + 1):
        xi, yi = int(round(x)), int(round(y))
        points.append([xi, yi])
        trace.append({"step": i, "x": xi, "y": yi, "calc": f"({x:.2f}, {y:.2f})"})
        x += sx
        y += sy

    return points, trace


def algo_bresenham_line(x1: int, y1: int, x2: int, y2: int) -> Tuple[List[List[int]], List[Dict[str, Any]]]:
    points = []
    trace = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    cx, cy = x1, y1
    err = dx - dy
    step = 0

    while True:
        points.append([cx, cy])
        if len(trace) < 50:
            trace.append({"step": step, "x": cx, "y": cy, "err": err, "calc": f"err={err}"})
        if cx == x2 and cy == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy
        step += 1

    return points, trace


def algo_bresenham_circle(xc: int, yc: int, r: int) -> Tuple[List[List[int]], List[Dict[str, Any]]]:
    points = []
    trace = []
    x, y = 0, abs(r)
    d = 3 - 2 * abs(r)
    step = 0

    def add_sym(px: int, py: int):
        pts = [
            [xc + px, yc + py], [xc + px, yc - py],
            [xc - px, yc + py], [xc - px, yc - py],
            [xc + py, yc + px], [xc + py, yc - px],
            [xc - py, yc + px], [xc - py, yc - px]
        ]
        for p in pts:
            if p not in points:
                points.append(p)

    while x <= y:
        add_sym(x, y)
        if len(trace) < 50:
            trace.append({"step": step, "x": x, "y": y, "d": d, "calc": f"d={d}"})
        if d >= 0:
            d += 4 * (x - y) + 10
            y -= 1
        else:
            d += 4 * x + 6
        x += 1
        step += 1

    return points, trace


def rasterize(algo: str, params: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    trace = []

    if algo == "step":
        pts, trace = algo_step(params["x1"], params["y1"], params["x2"], params["y2"])
    elif algo == "dda":
        pts, trace = algo_dda(params["x1"], params["y1"], params["x2"], params["y2"])
    elif algo == "bresenham":
        pts, trace = algo_bresenham_line(params["x1"], params["y1"], params["x2"], params["y2"])
    elif algo == "circle":
        pts, trace = algo_bresenham_circle(params["xc"], params["yc"], params["r"])
    else:
        raise ValueError(f"Неизвестный алгоритм: {algo}")

    dt_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "points": pts,
        "count": len(pts),
        "trace": trace,
        "time_ms": round(dt_ms, 4)
    }
