"""
Animated B-Tree Visualizer
Minh họa từng bước: duyệt cây → chèn → tách node → xóa → merge/borrow.
"""
import tkinter as tk
from btree import BTree, BTreeNode

# ── MÀU SẮC ──────────────────────────────────────────────────────────────────
C = {
    "bg":           "#0f172a",
    "node_bg":      "#1e2a3a",
    "node_border":  "#3b82f6",
    "node_text":    "#e2e8f0",
    "root_border":  "#f59e0b",
    "edge":         "#475569",
    "traverse":     "#a78bfa",
    "insert":       "#22c55e",
    "split_old":    "#f59e0b",
    "split_new":    "#fb923c",
    "delete":       "#ef4444",
    "found":        "#fbbf24",
    "borrow":       "#38bdf8",
    "merge":        "#e879f9",
    "faded":        "#2d3748",
}

NODE_W = 88
NODE_H = 34
V_GAP  = 72
PAD_X  = 50


class AnimatedTreeVisualizer:
    def __init__(self, canvas: tk.Canvas, label_widget=None):
        self.canvas = canvas
        self.label  = label_widget
        self._btree      = None
        self._highlights = {}        # id(node) -> state str
        self._positions  = {}        # id(node) -> (cx, cy)
        self._after_id   = None
        self._animating  = False
        self.canvas.bind("<Configure>", lambda e: self._redraw())

    # ════════════════════════════════════════════════
    #  PUBLIC
    # ════════════════════════════════════════════════
    def draw_static(self, btree: BTree):
        self._cancel()
        self._btree      = btree
        self._highlights = {}
        self._redraw()

    def animate_insert(self, btree_before: BTree, key: str,
                       btree_after: BTree, on_done=None):
        self._cancel()
        steps = self._steps_insert(btree_before, btree_after, key)
        self._run_steps(btree_before, steps, btree_after, on_done)

    def animate_delete(self, btree_before: BTree, key: str,
                       btree_after: BTree, on_done=None):
        self._cancel()
        steps = self._steps_delete(btree_before, key)
        self._run_steps(btree_before, steps, btree_after, on_done)

    def animate_search(self, btree: BTree, key: str,
                       found: bool, on_done=None):
        self._cancel()
        steps = self._steps_search(btree, key, found)
        self._run_steps(btree, steps, btree, on_done)

    def is_animating(self):
        return self._animating

    def stop(self):
        self._cancel()

    # ════════════════════════════════════════════════
    #  STEP BUILDERS
    # ════════════════════════════════════════════════
    def _steps_insert(self, tree_before, tree_after, key):
        steps = []
        all_before = self._all_nodes(tree_before)

        # 1. Duyệt đường đi
        path = self._insert_path(tree_before, key)
        for i, node in enumerate(path):
            hl = {id(n): "faded" for n in all_before}
            for n in path[:i]:
                hl[id(n)] = "traverse"
            hl[id(node)] = "traverse"
            lbl = (f"🔍 Duyệt: [{self._keys_str(node)}]  →  tìm vị trí chèn '{key}'"
                   if i < len(path)-1
                   else f"📌 Node lá [{self._keys_str(node)}]  →  chèn '{key}' tại đây")
            steps.append((hl, lbl, 600))

        # 2. Node lá đầy → cảnh báo split
        leaf = path[-1] if path else tree_before.root
        if len(leaf.keys) >= BTree.MAX_KEYS:
            hl = {id(n): "faded" for n in all_before}
            hl[id(leaf)] = "split_old"
            steps.append((hl,
                           f"⚠ Node [{self._keys_str(leaf)}] đầy (2 keys) → cần TÁCH NODE!",
                           900))

        # 3. Hiện cây sau insert, highlight node mới + node cha nếu có split
        result = tree_after.search(key)
        new_node = result[0] if result else None
        hl_after = {}
        if new_node:
            hl_after[id(new_node)] = "insert"
            if len(leaf.keys) >= BTree.MAX_KEYS:
                parent = self._find_parent(tree_after.root, new_node)
                if parent:
                    hl_after[id(parent)] = "split_new"

        lbl = (f"✂ Node tách → key giữa đẩy lên cha — '{key}' chèn thành công!"
               if len(leaf.keys) >= BTree.MAX_KEYS
               else f"✅ '{key}' đã chèn vào node lá!")
        steps.append((hl_after, lbl, 900, tree_after))  # tuple 4 = cây mới
        steps.append(({}, "", 400, tree_after))
        return steps

    def _steps_delete(self, tree_before, key):
        steps = []
        all_before = self._all_nodes(tree_before)

        # 1. Duyệt tìm node
        path = self._search_path(tree_before, key)
        for i, node in enumerate(path):
            hl = {id(n): "faded" for n in all_before}
            for n in path[:i]:
                hl[id(n)] = "traverse"
            hl[id(node)] = "traverse"
            lbl = (f"🔍 Duyệt: [{self._keys_str(node)}]"
                   if i < len(path)-1
                   else f"🎯 Tìm thấy '{key}' trong node [{self._keys_str(node)}]!")
            steps.append((hl, lbl, 550))

        # 2. Highlight đỏ - xóa
        if path:
            hl = {id(n): "faded" for n in all_before}
            hl[id(path[-1])] = "delete"
            steps.append((hl, f"🗑 Xóa '{key}' — kiểm tra cần rebalance không...", 800))

        return steps

    def _steps_search(self, btree, key, found):
        steps = []
        all_nodes = self._all_nodes(btree)
        path = self._search_path(btree, key)

        for i, node in enumerate(path):
            hl = {id(n): "faded" for n in all_nodes}
            for n in path[:i]: hl[id(n)] = "traverse"
            hl[id(node)] = "traverse"
            steps.append((hl, f"🔍 Kiểm tra: [{self._keys_str(node)}]", 500))

        if found:
            hl = {id(n): "faded" for n in all_nodes}
            # Highlight TẤT CẢ các node chứa key (hỗ trợ tìm theo tên trùng)
            count = 0
            for n in all_nodes:
                if any(key.lower() in k[0].lower() for k in n.keys):
                    hl[id(n)] = "found"
                    count += 1
            steps.append((hl, f"✅ Tìm thấy {count} node chứa kết quả khớp!", 1000))
        else:
            hl = {id(n): "faded" for n in all_nodes}
            if path: hl[id(path[-1])] = "delete"
            steps.append((hl, f"❌ Không tìm thấy '{key}'", 1000))

        steps.append(({}, "", 500))
        return steps

    # ════════════════════════════════════════════════
    #  STEP RUNNER
    # ════════════════════════════════════════════════
    def _run_steps(self, tree_start, steps, tree_end, on_done):
        self._animating = True
        self._btree     = tree_start
        self._highlights = {}
        self._redraw()

        idx = [0]

        def tick():
            if idx[0] >= len(steps):
                # Kết thúc: hiện cây cuối
                self._btree      = tree_end
                self._highlights = {}
                self._redraw()
                self._animating  = False
                if self.label:
                    self.label.configure(text="")
                if on_done:
                    on_done()
                return

            step = steps[idx[0]]
            idx[0] += 1

            hl  = step[0]
            lbl = step[1]
            dur = step[2]
            # Nếu step có cây riêng (tuple 4 phần tử) → chuyển sang cây đó
            if len(step) == 4:
                self._btree = step[3]

            self._highlights = hl
            if self.label:
                self.label.configure(text=lbl)
            self._redraw()
            self._after_id = self.canvas.after(dur, tick)

        tick()

    def _cancel(self):
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None
        self._animating = False

    # ════════════════════════════════════════════════
    #  DRAW
    # ════════════════════════════════════════════════
    def _redraw(self):
        c = self.canvas
        c.delete("all")
        if not self._btree or not self._btree.root.keys:
            cw = max(c.winfo_width() // 2, 200)
            c.create_text(cw, 70, text="(Cây rỗng)",
                          fill="#64748b", font=("Consolas", 13))
            return

        self._calc_positions()
        levels = self._btree.get_all_nodes_by_level()
        edges  = self._btree.get_edges()

        # Cạnh
        for pid, cid in edges:
            if pid in self._positions and cid in self._positions:
                px, py = self._positions[pid]
                cx, cy = self._positions[cid]
                c.create_line(px, py + NODE_H//2,
                              cx, cy - NODE_H//2,
                              fill=C["edge"], width=1.5, smooth=True)

        # Nodes
        is_root = True
        for lvl in sorted(levels):
            for node in levels[lvl]:
                if id(node) in self._positions:
                    self._draw_node(node, self._positions[id(node)], is_root)
                    is_root = False

        bbox = c.bbox("all")
        if bbox:
            c.configure(scrollregion=(bbox[0]-20, bbox[1]-20,
                                      bbox[2]+20, bbox[3]+20))

    def _calc_positions(self):
        if not self._btree:
            return
        self._positions = {}
        self._leaf_count_cache = {}
        w = max(self.canvas.winfo_width(), 600)
        self._place(self._btree.root, PAD_X, w - PAD_X, 52)

    def _leaf_count(self, node):
        """Đếm số lá trong subtree — dùng để chia không gian tỉ lệ."""
        if id(node) in self._leaf_count_cache:
            return self._leaf_count_cache[id(node)]
        if node.leaf:
            result = 1
        else:
            result = sum(self._leaf_count(c) for c in node.children)
        self._leaf_count_cache[id(node)] = result
        return result

    def _place(self, node, x_min, x_max, y):
        cx = (x_min + x_max) / 2
        self._positions[id(node)] = (cx, y)
        if not node.leaf and node.children:
            total_leaves = self._leaf_count(node)
            x_cursor = x_min
            for child in node.children:
                child_leaves = self._leaf_count(child)
                # Chia không gian tỉ lệ với số lá của từng subtree
                child_width = (x_max - x_min) * child_leaves / total_leaves
                self._place(child, x_cursor, x_cursor + child_width,
                            y + NODE_H + V_GAP)
                x_cursor += child_width

    def _draw_node(self, node, pos, is_root):
        c = self.canvas
        cx, cy = pos
        n = len(node.keys)
        if n == 0:
            return

        total_w = n * NODE_W + (n-1) * 2
        x0 = cx - total_w / 2
        y0 = cy - NODE_H / 2
        y1 = cy + NODE_H / 2

        state  = self._highlights.get(id(node))
        border, fill, text_c, bw = self._resolve_colors(state, is_root)

        for i, (key, _) in enumerate(node.keys):
            kx0 = x0 + i * (NODE_W + 2)
            kx1 = kx0 + NODE_W
            c.create_rectangle(kx0, y0, kx1, y1,
                                fill=fill, outline=border, width=bw)
            # Glow border nếu đang active
            if state and state not in ("faded",):
                c.create_rectangle(kx0-2, y0-2, kx1+2, y1+2,
                                   outline=border, width=1, fill="")

            disp = str(key)[:10] + ("…" if len(str(key)) > 10 else "")
            c.create_text((kx0+kx1)/2, cy,
                          text=disp, fill=text_c,
                          font=("Consolas", 10, "bold"))

        # Separator
        for i in range(1, n):
            sx = x0 + i*(NODE_W+2) - 1
            c.create_line(sx, y0+4, sx, y1-4, fill=border, width=1)

        # ROOT label
        if is_root:
            c.create_text(cx, y0-11, text="ROOT",
                          fill=C["root_border"],
                          font=("Consolas", 8, "bold"))

        # State badge
        badge = {"traverse":"duyệt","insert":"✦ mới","delete":"✕ xóa",
                 "found":"✔ thấy","split_old":"tách!","split_new":"từ tách",
                 "borrow":"mượn","merge":"gộp"}.get(state, "")
        if badge:
            c.create_text(cx, y1+12, text=badge,
                          fill=border, font=("Consolas", 8))

    def _resolve_colors(self, state, is_root):
        m = {
            "traverse":  (C["traverse"], "#2d1f4e", C["node_text"], 2.5),
            "insert":    (C["insert"],   "#14402a", C["node_text"], 2.5),
            "delete":    (C["delete"],   "#4a1a1a", C["node_text"], 2.5),
            "found":     (C["found"],    "#4a3a10", C["node_text"], 2.5),
            "split_old": (C["split_old"],"#4a3010", C["node_text"], 2.5),
            "split_new": (C["split_new"],"#3a2010", C["node_text"], 2.5),
            "borrow":    (C["borrow"],   "#0f2a3a", C["node_text"], 2.5),
            "merge":     (C["merge"],    "#3a0f3a", C["node_text"], 2.5),
            "faded":     ("#2d3748",     "#111827", "#4b5563",      1.0),
        }
        if state in m:
            return m[state]
        border = C["root_border"] if is_root else C["node_border"]
        return border, C["node_bg"], C["node_text"], 2 if is_root else 1.5

    # ════════════════════════════════════════════════
    #  HELPERS
    # ════════════════════════════════════════════════
    def _all_nodes(self, btree):
        return [n for lvl in btree.get_all_nodes_by_level().values() for n in lvl]

    def _keys_str(self, node):
        return ", ".join(k for k, _ in node.keys)

    def _insert_path(self, btree, key):
        path, node = [], btree.root
        while True:
            path.append(node)
            if node.leaf:
                break
            i = 0
            while i < len(node.keys) and key > node.keys[i][0]:
                i += 1
            if i < len(node.keys) and node.keys[i][0] == key:
                break
            node = node.children[i]
        return path

    def _search_path(self, btree, key):
        path, node = [], btree.root
        while True:
            path.append(node)
            i = 0
            while i < len(node.keys) and key > node.keys[i][0]:
                i += 1
            
            found_at_this_node = (i < len(node.keys) and node.keys[i][0] == key)
            
            if found_at_this_node or node.leaf:
                break
            node = node.children[i]
        return path

    def _find_parent(self, root, target):
        if root.leaf:
            return None
        for child in root.children:
            if child is target:
                return root
            p = self._find_parent(child, target)
            if p:
                return p
        return None