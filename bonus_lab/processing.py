import base64
import io
import math
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw

Vec3 = Tuple[float, float, float]
Quad2D = List[Tuple[float, float]]
Mat4 = List[List[float]]


def mat4_identity() -> Mat4:
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_mul(a: Mat4, b: Mat4) -> Mat4:
    res = [[0.0, 0.0, 0.0, 0.0] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            res[i][j] = (
                a[i][0] * b[0][j]
                + a[i][1] * b[1][j]
                + a[i][2] * b[2][j]
                + a[i][3] * b[3][j]
            )
    return res


def mat4_translate(tx: float, ty: float, tz: float) -> Mat4:
    return [
        [1.0, 0.0, 0.0, float(tx)],
        [0.0, 1.0, 0.0, float(ty)],
        [0.0, 0.0, 1.0, float(tz)],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_scale(sx: float, sy: float, sz: float) -> Mat4:
    return [
        [float(sx), 0.0, 0.0, 0.0],
        [0.0, float(sy), 0.0, 0.0],
        [0.0, 0.0, float(sz), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_rotate_x(deg: float) -> Mat4:
    rad = math.radians(float(deg))
    c, s = math.cos(rad), math.sin(rad)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_rotate_y(deg: float) -> Mat4:
    rad = math.radians(float(deg))
    c, s = math.cos(rad), math.sin(rad)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_rotate_z(deg: float) -> Mat4:
    rad = math.radians(float(deg))
    c, s = math.cos(rad), math.sin(rad)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_transform_point(m: Mat4, p: Vec3) -> List[float]:
    x, y, z = p
    nx = m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]
    ny = m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]
    nz = m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]
    nw = m[3][0] * x + m[3][1] * y + m[3][2] * z + m[3][3]
    if abs(nw) > 1e-9 and abs(nw - 1.0) > 1e-9:
        nx, ny, nz = nx / nw, ny / nw, nz / nw
    return [round(nx, 3), round(ny, 3), round(nz, 3)]


def _rect(x0: float, y0: float, x1: float, y1: float) -> Quad2D:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _face_normal(p0: Vec3, p1: Vec3, p2: Vec3) -> List[float]:
    ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return [round(nx / length, 6), round(ny / length, 6), round(nz / length, 6)]


def build_dikan_mesh(depth: float = 1.6) -> Dict[str, Any]:
    """Build the 3D extruded mesh for 'ДИКАН' using an explicit vertex coordinate array."""
    prisms: List[Quad2D] = []

    # Д
    prisms.extend([
        _rect(0.00, -0.80, 0.85, 0.00),
        _rect(3.45, -0.80, 4.30, 0.00),
        _rect(0.00, 0.00, 4.30, 0.90),
        [(0.55, 0.90), (1.45, 0.90), (1.75, 4.10), (0.85, 4.10)],
        _rect(2.85, 0.90, 3.75, 4.10),
        _rect(0.85, 4.10, 3.75, 5.00),
    ])
    # И
    ix = 5.15
    prisms.extend([
        _rect(ix + 0.0, 0.00, ix + 0.90, 5.00),
        _rect(ix + 2.90, 0.00, ix + 3.80, 5.00),
        [(ix + 0.90, 0.00), (ix + 2.90, 3.35), (ix + 2.90, 5.00), (ix + 0.90, 1.65)],
    ])
    # К
    kx = 9.80
    prisms.extend([
        _rect(kx + 0.0, 0.00, kx + 0.90, 5.00),
        _rect(kx + 0.90, 2.05, kx + 2.05, 2.95),
        [(kx + 0.90, 2.95), (kx + 2.05, 2.95), (kx + 3.90, 5.00), (kx + 2.70, 5.00)],
        [(kx + 0.90, 2.05), (kx + 2.70, 0.00), (kx + 3.90, 0.00), (kx + 2.05, 2.05)],
    ])
    # А
    ax = 14.55
    prisms.extend([
        [(ax + 0.00, 0.00), (ax + 0.95, 0.00), (ax + 2.00, 5.00), (ax + 1.30, 5.00)],
        [(ax + 3.05, 0.00), (ax + 4.00, 0.00), (ax + 2.70, 5.00), (ax + 2.00, 5.00)],
        [(ax + 1.223, 1.30), (ax + 2.777, 1.30), (ax + 2.5985, 2.15), (ax + 1.4015, 2.15)],
    ])
    # Н
    nx = 19.40
    prisms.extend([
        _rect(nx + 0.0, 0.00, nx + 0.90, 5.00),
        _rect(nx + 2.90, 0.00, nx + 3.80, 5.00),
        _rect(nx + 0.90, 2.05, nx + 2.90, 2.95),
    ])

    cx, cy = 11.60, 2.10
    z_front = round(depth * 0.5, 4)
    z_back = round(-depth * 0.5, 4)
    uv_scale = 0.28

    vertices: List[List[float]] = []
    triangles: List[Dict[str, Any]] = []
    edges: List[List[int]] = []

    def add_vertex(x: float, y: float, z: float) -> int:
        vertices.append([round(x - cx, 4), round(y - cy, 4), round(z, 4)])
        return len(vertices) - 1

    def add_tri(i0: int, i1: int, i2: int, uv0: List[float], uv1: List[float], uv2: List[float]) -> None:
        n = _face_normal(tuple(vertices[i0]), tuple(vertices[i1]), tuple(vertices[i2]))  # type: ignore[arg-type]
        triangles.append({"v": [i0, i1, i2], "uv": [uv0, uv1, uv2], "normal": n})

    for q2d in prisms:
        f_idx = [add_vertex(px, py, z_front) for px, py in q2d]
        b_idx = [add_vertex(px, py, z_back) for px, py in q2d]

        for i in range(4):
            j = (i + 1) % 4
            edges.append([f_idx[i], f_idx[j]])
            edges.append([b_idx[i], b_idx[j]])
            edges.append([f_idx[i], b_idx[i]])

        f_uv = [[round(px * uv_scale, 4), round(1.0 - py * uv_scale, 4)] for px, py in q2d]
        add_tri(f_idx[0], f_idx[1], f_idx[2], f_uv[0], f_uv[1], f_uv[2])
        add_tri(f_idx[0], f_idx[2], f_idx[3], f_uv[0], f_uv[2], f_uv[3])

        b_uv = [[round((24.0 - px) * uv_scale, 4), round(1.0 - py * uv_scale, 4)] for px, py in q2d]
        add_tri(b_idx[0], b_idx[2], b_idx[1], b_uv[0], b_uv[2], b_uv[1])
        add_tri(b_idx[0], b_idx[3], b_idx[2], b_uv[0], b_uv[3], b_uv[2])

        depth_uv = round((z_front - z_back) * 0.42, 4)
        for i in range(4):
            j = (i + 1) % 4
            side_len = round(math.hypot(q2d[j][0] - q2d[i][0], q2d[j][1] - q2d[i][1]) * uv_scale, 4)
            add_tri(b_idx[i], b_idx[j], f_idx[j], [0.0, 0.0], [side_len, 0.0], [side_len, depth_uv])
            add_tri(b_idx[i], f_idx[j], f_idx[i], [0.0, 0.0], [side_len, depth_uv], [0.0, depth_uv])

    return {
        "label": "ДИКАН",
        "vertices": vertices,
        "triangles": triangles,
        "edges": edges,
    }


def compute_transformation(params: Dict[str, Any], vertices: List[List[float]]) -> Dict[str, Any]:
    m_s = mat4_scale(float(params.get("sx", 1.0)), float(params.get("sy", 1.0)), float(params.get("sz", 1.0)))
    m_rx = mat4_rotate_x(float(params.get("rx", 0.0)))
    m_ry = mat4_rotate_y(float(params.get("ry", 0.0)))
    m_rz = mat4_rotate_z(float(params.get("rz", 0.0)))
    m_t = mat4_translate(float(params.get("tx", 0.0)), float(params.get("ty", 0.0)), float(params.get("tz", 0.0)))

    m = mat4_mul(m_rx, m_s)
    m = mat4_mul(m_ry, m)
    m = mat4_mul(m_rz, m)
    m = mat4_mul(m_t, m)

    transformed = [mat4_transform_point(m, tuple(v)) for v in vertices]  # type: ignore[arg-type]
    return {
        "matrix": [[round(val, 4) for val in row] for row in m],
        "transformed_vertices": transformed,
    }


TEXTURE_NAMES = {
    "wood": "Дерево",
    "brick": "Кирпич",
    "checker": "Шахматка",
    "marble": "Мрамор",
    "cyber": "Техно-сетка",
}


def _pil_to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def generate_procedural_texture(key: str, size: int = 256) -> str:
    img = Image.new("RGB", (size, size))
    pixels: List[Tuple[int, int, int]] = []

    if key == "wood":
        for y in range(size):
            v = y / size
            for x in range(size):
                u = x / size
                ring = math.sin((u * 8.0 + math.sin(v * 2.0 * math.pi) * 0.42) * 2.0 * math.pi) * 0.5 + 0.5
                grain = math.sin(u * 96.0 + v * 10.0) * 0.08
                t = max(0.0, min(1.0, ring * 0.72 + grain + 0.16))
                pixels.append((int(105 + 108 * t), int(54 + 74 * t), int(24 + 36 * t)))
        img.putdata(pixels)
    elif key == "brick":
        brick_h, brick_w = size // 8, size // 4
        mortar = max(3, size // 64)
        for y in range(size):
            row = y // brick_h
            by = y % brick_h
            offset = (brick_w // 2) if (row % 2 == 1) else 0
            for x in range(size):
                bx = (x + offset) % brick_w
                if bx < mortar or by < mortar:
                    pixels.append((202, 198, 190))
                else:
                    noise = int(10 * math.sin(x * 0.35 + y * 0.5))
                    pixels.append((max(0, min(255, 180 + noise)), max(0, min(255, 74 + noise // 2)), max(0, min(255, 56 + noise // 2))))
        img.putdata(pixels)
    elif key == "marble":
        for y in range(size):
            v = y / size
            for x in range(size):
                u = x / size
                warp = math.sin(u * 4.0 * math.pi + v * 2.0 * math.pi) * 0.28
                vein = abs(math.sin((u * 3.0 + v * 2.0 + warp) * math.pi))
                t = vein ** 0.42
                pixels.append((int(90 + 152 * t), int(104 + 142 * t), int(126 + 122 * t)))
        img.putdata(pixels)
    elif key == "checker":
        cell = size // 8
        for y in range(size):
            for x in range(size):
                if ((x // cell) + (y // cell)) % 2 == 0:
                    pixels.append((240, 244, 250))
                else:
                    pixels.append((42, 98, 210))
        img.putdata(pixels)
    else:
        step = size // 8
        for y in range(size):
            for x in range(size):
                if x % step < 3 or y % step < 3:
                    pixels.append((56, 189, 248))
                elif (x // step + y // step) % 2 == 0:
                    pixels.append((24, 34, 52))
                else:
                    pixels.append((34, 46, 68))
        img.putdata(pixels)
        draw = ImageDraw.Draw(img)
        for gx in range(0, size, step):
            for gy in range(0, size, step):
                draw.rectangle([gx, gy, gx + 4, gy + 4], fill=(96, 165, 250))

    return _pil_to_data_url(img)


def process_uploaded_texture(file_bytes: bytes, target_size: int = 512) -> str:
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return _pil_to_data_url(img)
