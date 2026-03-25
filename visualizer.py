"""
Module vẽ B-Tree lên tkinter Canvas.
Hỗ trợ highlight node khi tìm kiếm / thêm / xóa.
"""
import tkinter as tk


# ── MÀU SẮC ─────────────────────────────────────────────────────────────────
COLORS = {
    "node_bg":      "#1e2a3a",
    "node_border":  "#3b82f6",
    "node_text":    "#e2e8f0",
    "highlight_add":    "#22c55e",   # xanh lá - thêm
    "highlight_del":    "#ef4444",   # đỏ - xóa
    "highlight_found":  "#f59e0b",   # vàng - tìm thấy
    "highlight_search": "#a78bfa",   # tím - đang duyệt
    "edge":         "#475569",
    "bg":           "#0f172a",
    "key_sep":      "#3b82f6",
    "root_border":  "#f59e0b",
}

NODE_W = 90     # chiều rộng mỗi ô key trong node
NODE_H = 36
H_GAP  = 20    # khoảng cách ngang giữa các node
V_GAP  = 70    # khoảng cách dọc giữa các tầng
PAD_X  = 40


class TreeVisualizer:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.highlights: dict[int, str] = {}  # node_id -> color key

    def set_highlight(self, node_ids: list, color_key: str):
        self.highlights = {nid: color_key for nid in node_ids}

    def clear_highlight(self):
        self.highlights = {}

    def draw(self, btree):
        c = self.canvas
        c.delete("all")

        if not btree.root.keys:
            c.create_text(
                int(c.winfo_width()) // 2 or 300, 80,
                text="(Cây rỗng)", fill="#64748b", font=("Consolas", 13)
            )
            return

        # Tính vị trí từng node
        positions = {}   # id(node) -> (cx, cy)
        levels = btree.get_all_nodes_by_level()
        edges = btree.get_edges()

        # Tính chiều rộng của mỗi subtree để căn giữa
        node_width = {}
        self._calc_width(btree.root, node_width)

        canvas_w = max(int(c.winfo_width()), 600)
        self._calc_pos(btree.root, PAD_X, canvas_w - PAD_X, 60, positions)

        # Vẽ cạnh trước
        for pid, cid in edges:
            if pid in positions and cid in positions:
                px, py = positions[pid]
                cx, cy = positions[cid]
                c.create_line(px, py + NODE_H // 2, cx, cy - NODE_H // 2,
                              fill=COLORS["edge"], width=1.5, smooth=True)

        # Vẽ nodes
        is_root = True
        for level in sorted(levels.keys()):
            for node in levels[level]:
                if id(node) in positions:
                    self._draw_node(node, positions[id(node)], is_root)
                is_root = False

        # Cập nhật scroll region
        bbox = c.bbox("all")
        if bbox:
            c.configure(scrollregion=(bbox[0]-20, bbox[1]-20,
                                      bbox[2]+20, bbox[3]+20))

    def _calc_pos(self, node, x_min, x_max, y, positions):
        cx = (x_min + x_max) / 2
        positions[id(node)] = (cx, y)

        if not node.leaf and node.children:
            n = len(node.children)
            slot = (x_max - x_min) / n
            for i, child in enumerate(node.children):
                self._calc_pos(child,
                               x_min + i * slot,
                               x_min + (i + 1) * slot,
                               y + NODE_H + V_GAP, positions)

    def _calc_width(self, node, cache):
        if node.leaf or not node.children:
            cache[id(node)] = max(len(node.keys), 1)
            return cache[id(node)]
        w = sum(self._calc_width(c, cache) for c in node.children)
        cache[id(node)] = w
        return w

    def _draw_node(self, node, pos, is_root=False):
        c = self.canvas
        cx, cy = pos
        n = len(node.keys)
        total_w = n * NODE_W + (n - 1) * 2
        x0 = cx - total_w / 2
        y0 = cy - NODE_H / 2
        y1 = cy + NODE_H / 2

        # Màu viền
        hl = self.highlights.get(id(node))
        if hl:
            border_color = COLORS[hl]
            border_w = 3
        elif is_root:
            border_color = COLORS["root_border"]
            border_w = 2
        else:
            border_color = COLORS["node_border"]
            border_w = 1.5

        # Vẽ từng ô key
        for i, (key, _) in enumerate(node.keys):
            kx0 = x0 + i * (NODE_W + 2)
            kx1 = kx0 + NODE_W

            # Nền
            fill = COLORS["node_bg"]
            if hl:
                # Nhạt hơn để dễ nhìn
                fill = self._lighten(COLORS[hl])

            c.create_rectangle(kx0, y0, kx1, y1,
                                fill=fill,
                                outline=border_color,
                                width=border_w)

            # Key text
            display = str(key)
            if len(display) > 10:
                display = display[:9] + "…"
            c.create_text((kx0 + kx1) / 2, cy,
                          text=display,
                          fill=COLORS["node_text"],
                          font=("Consolas", 11, "bold"))

        # Separator giữa các key
        for i in range(1, n):
            sx = x0 + i * (NODE_W + 2) - 1
            c.create_line(sx, y0 + 4, sx, y1 - 4,
                          fill=COLORS["key_sep"], width=1)

        # Tag "ROOT"
        if is_root:
            c.create_text(cx, y0 - 10,
                          text="ROOT", fill=COLORS["root_border"],
                          font=("Consolas", 9, "bold"))

    @staticmethod
    def _lighten(hex_color):
        """Trả về phiên bản tối hơn của màu để làm nền node highlight."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, int(r * 0.35 + 10))
        g = min(255, int(g * 0.35 + 10))
        b = min(255, int(b * 0.35 + 10))
        return f"#{r:02x}{g:02x}{b:02x}"
