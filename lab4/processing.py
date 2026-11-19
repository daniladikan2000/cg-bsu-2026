import math
from typing import List, Dict, Any

INSIDE = 0
LEFT   = 1
RIGHT  = 2
BOTTOM = 4
TOP    = 8


def get_code(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code


def clip_midpoint(x1: float, y1: float, x2: float, y2: float,
                  xmin: float, ymin: float, xmax: float, ymax: float,
                  eps: float = 1e-3) -> Dict[str, Any]:
    c1 = get_code(x1, y1, xmin, ymin, xmax, ymax)
    c2 = get_code(x2, y2, xmin, ymin, xmax, ymax)

    if (c1 | c2) == 0:
        return {"status": "inside", "clipped": [[x1, y1], [x2, y2]]}
    if (c1 & c2) != 0:
        return {"status": "outside", "clipped": None}

    p1 = [x1, y1]
    if c1 != INSIDE:
        a, b = [x1, y1], [x2, y2]
        while math.hypot(b[0] - a[0], b[1] - a[1]) > eps:
            m = [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]
            if (get_code(a[0], a[1], xmin, ymin, xmax, ymax) & get_code(m[0], m[1], xmin, ymin, xmax, ymax)) != 0:
                a = m
            else:
                b = m
        p1 = b

    p2 = [x2, y2]
    if c2 != INSIDE:
        a, b = [p1[0], p1[1]], [x2, y2]
        while math.hypot(b[0] - a[0], b[1] - a[1]) > eps:
            m = [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]
            if (get_code(b[0], b[1], xmin, ymin, xmax, ymax) & get_code(m[0], m[1], xmin, ymin, xmax, ymax)) != 0:
                b = m
            else:
                a = m
        p2 = a

    if get_code(p1[0], p1[1], xmin, ymin, xmax, ymax) != INSIDE or get_code(p2[0], p2[1], xmin, ymin, xmax, ymax) != INSIDE:
        return {"status": "outside", "clipped": None}

    return {
        "status": "clipped",
        "clipped": [[round(p1[0], 2), round(p1[1], 2)], [round(p2[0], 2), round(p2[1], 2)]]
    }


def clip_cyrus_beck(x1: float, y1: float, x2: float, y2: float,
                    poly: List[List[float]]) -> Dict[str, Any]:
    n = len(poly)
    if n < 3:
        return {"status": "outside", "clipped": None}

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += poly[i][0] * poly[j][1] - poly[j][0] * poly[i][1]
    if area < 0:
        poly = list(reversed(poly))

    dx = x2 - x1
    dy = y2 - y1
    tin, tout = 0.0, 1.0

    for i in range(n):
        v1 = poly[i]
        v2 = poly[(i + 1) % n]
        normal = [-(v2[1] - v1[1]), v2[0] - v1[0]]
        w = [x1 - v1[0], y1 - v1[1]]

        num = normal[0] * w[0] + normal[1] * w[1]
        den = normal[0] * dx + normal[1] * dy

        if den == 0:
            if num < 0:
                return {"status": "outside", "clipped": None}
        else:
            t = -num / den
            if den > 0:
                tin = max(tin, t)
            else:
                tout = min(tout, t)

    if tin > tout:
        return {"status": "outside", "clipped": None}

    cx1 = round(x1 + tin * dx, 2)
    cy1 = round(y1 + tin * dy, 2)
    cx2 = round(x1 + tout * dx, 2)
    cy2 = round(y1 + tout * dy, 2)

    return {"status": "clipped", "clipped": [[cx1, cy1], [cx2, cy2]], "tin": round(tin, 2), "tout": round(tout, 2)}


def parse_input_file(content: str) -> Dict[str, Any]:
    lines = [l.strip() for l in content.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    if not lines:
        raise ValueError("Пустой файл")
    n = int(lines[0].split()[0])
    segments = []
    for i in range(1, n + 1):
        vals = list(map(float, lines[i].split()))
        segments.append({"x1": vals[0], "y1": vals[1], "x2": vals[2], "y2": vals[3]})

    poly = None
    win = None
    if n + 1 < len(lines):
        rest = lines[n + 1].split()
        if rest[0].upper() == "POLYGON" or (len(rest) == 1 and int(rest[0]) > 2):
            k = int(rest[1]) if rest[0].upper() == "POLYGON" else int(rest[0])
            poly = []
            for j in range(n + 2, n + 2 + k):
                if j < len(lines):
                    poly.append(list(map(float, lines[j].split())))
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            win = {"xmin": min(xs), "ymin": min(ys), "xmax": max(xs), "ymax": max(ys)}
        else:
            w_vals = list(map(float, lines[n + 1].split()))
            win = {"xmin": min(w_vals[0], w_vals[2]), "ymin": min(w_vals[1], w_vals[3]),
                   "xmax": max(w_vals[0], w_vals[2]), "ymax": max(w_vals[1], w_vals[3])}
    else:
        win = {"xmin": 0.0, "ymin": 0.0, "xmax": 20.0, "ymax": 20.0}

    return {"segments": segments, "window": win, "polygon": poly}
