"""
Ứng dụng Quản Lý Sinh Viên
Giao diện: CustomTkinter  |  Index: B-Tree bậc 3  |  Animation: từng bước
"""
import tkinter as tk
from tkinter import ttk
import copy
import customtkinter as ctk
from database import StudentDB, Student
from visualizer import AnimatedTreeVisualizer
from btree import BTree

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK_BG  = "#0f172a"
PANEL_BG = "#1e293b"
CARD_BG  = "#1e2a3a"
ACCENT   = "#3b82f6"
ACCENT2  = "#22c55e"
DANGER   = "#ef4444"
TEXT     = "#e2e8f0"
TEXT2    = "#94a3b8"
BORDER   = "#334155"


def clone_btree(src: BTree) -> BTree:
    """Tạo bản sao B-Tree từ danh sách keys hiện tại."""
    return copy.deepcopy(src)

def _collect(node):
    if node.leaf:
        return list(node.keys)
    result = []
    for i, child in enumerate(node.children):
        result.extend(_collect(child))
        if i < len(node.keys):
            result.append(node.keys[i])
    return result


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quản Lý Sinh Viên  ·  B-Tree Index  ·  Animation")
        self.geometry("1340x800")
        self.minsize(1100, 680)
        self.configure(fg_color=DARK_BG)

        self.db = StudentDB()
        self._build_ui()
        self._refresh_table()
        self._draw_static_both()

    #  BUILD UI

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=PANEL_BG, height=54, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🎓  Quản Lý Sinh Viên  —  B-Tree Bậc 3",
                     font=ctk.CTkFont("Segoe UI", 19, "bold"),
                     text_color=TEXT).pack(side="left", padx=22, pady=12)
        self.lbl_count = ctk.CTkLabel(hdr, text="0 sinh viên",
                                       font=ctk.CTkFont("Segoe UI", 12),
                                       text_color=TEXT2)
        self.lbl_count.pack(side="right", padx=22)

        body = ctk.CTkFrame(self, fg_color=DARK_BG)
        body.pack(fill="both", expand=True, padx=8, pady=6)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=8)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    # ── LEFT ────────────────────────────────────────
    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        tab = ctk.CTkTabview(left, fg_color=CARD_BG,
                             segmented_button_fg_color=PANEL_BG,
                             segmented_button_selected_color=ACCENT)
        tab.pack(fill="x", padx=10, pady=(10, 4))
        tab.add("➕ Thêm")
        tab.add("🗑 Xóa")
        tab.add("🔍 Tìm")

        self._build_tab_add(tab.tab("➕ Thêm"))
        self._build_tab_delete(tab.tab("🗑 Xóa"))
        self._build_tab_search(tab.tab("🔍 Tìm"))

        # Bảng gốc
        tbl_frame = ctk.CTkFrame(left, fg_color=CARD_BG, corner_radius=10)
        tbl_frame.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        ctk.CTkLabel(tbl_frame, text="📋  Bảng Dữ Liệu Gốc",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=10, pady=(8, 2))

        cols = ("Mã SV","Họ và Tên","Giới tính","Năm sinh","Khoa","GPA")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("D.Treeview",
                        background=CARD_BG, foreground=TEXT,
                        fieldbackground=CARD_BG, rowheight=26,
                        font=("Segoe UI", 10))
        style.configure("D.Treeview.Heading",
                        background=PANEL_BG, foreground=TEXT2,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("D.Treeview", background=[("selected", ACCENT)])

        wrap = tk.Frame(tbl_frame, bg=CARD_BG)
        wrap.pack(fill="both", expand=True, padx=6, pady=(0,6))
        vsb = ttk.Scrollbar(wrap, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(wrap, orient="horizontal")
        hsb.pack(side="bottom", fill="x")
        self.tbl = ttk.Treeview(wrap, columns=cols, show="headings",
                                style="D.Treeview",
                                yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set)
        
        def _on_treeview_wheel(event):
            # Windows: event.delta / -120
            # Linux: Button-4 (lên), Button-5 (xuống)
            if event.num == 4 or event.delta > 0:
                self.tbl.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.tbl.yview_scroll(1, "units")

        # Bind cho Windows và MacOS/Linux
        self.tbl.bind("<MouseWheel>", _on_treeview_wheel)
        self.tbl.bind("<Button-4>", _on_treeview_wheel)
        self.tbl.bind("<Button-5>", _on_treeview_wheel)

        vsb.config(command=self.tbl.yview)
        hsb.config(command=self.tbl.xview)
        self.tbl.pack(fill="both", expand=True)
        for col, w in zip(cols, [75,145,70,85,110,45]):
            self.tbl.heading(col, text=col)
            self.tbl.column(col, width=w, anchor="center")

    def _build_tab_add(self, parent):
        fields = [
            ("Mã SV *",    "e_masv"),
            ("Họ và Tên *","e_hoten"),
            ("Giới tính",  "e_gt"),
            ("Năm sinh",  "e_ns"),
            ("Khoa",       "e_khoa"),
            ("GPA",        "e_gpa"),
        ]
        for lbl, attr in fields:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=lbl, width=96, anchor="w",
                         font=ctk.CTkFont("Segoe UI", 11),
                         text_color=TEXT2).pack(side="left")
            e = ctk.CTkEntry(row, height=28,
                             fg_color=PANEL_BG, border_color=BORDER,
                             text_color=TEXT)
            e.pack(side="left", fill="x", expand=True)
            setattr(self, attr, e)

        # Giới tính dùng combobox
        self.e_gt.destroy()
        row_gt = parent.winfo_children()[2]
        self.e_gt = ctk.CTkComboBox(row_gt, values=["Nam","Nữ","Khác"],
                                    fg_color=PANEL_BG, border_color=BORDER,
                                    text_color=TEXT, button_color=ACCENT,
                                    height=28, state="readonly")
        self.e_gt.set("Nam")
        self.e_gt.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(parent, text="➕  Thêm Sinh Viên",
                      fg_color=ACCENT2, hover_color="#16a34a",
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      height=34, command=self._on_add).pack(fill="x", pady=(8,2))

    def _build_tab_delete(self, parent):
        ctk.CTkLabel(parent, text="Nhập Mã SV cần xóa:",
                     text_color=TEXT2, font=ctk.CTkFont("Segoe UI", 11)
                     ).pack(anchor="w", pady=(8,2))
        self.e_del = ctk.CTkEntry(parent, height=32,
                                  fg_color=PANEL_BG, border_color=BORDER,
                                  text_color=TEXT, placeholder_text="VD: SV001")
        self.e_del.pack(fill="x", pady=4)
        ctk.CTkButton(parent, text="🗑  Xóa Sinh Viên",
                      fg_color=DANGER, hover_color="#b91c1c",
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      height=34, command=self._on_delete).pack(fill="x", pady=(8,2))

    def _build_tab_search(self, parent):
        ctk.CTkLabel(parent, text="Tìm theo Mã SV:",
                     text_color=TEXT2, font=ctk.CTkFont("Segoe UI", 11)
                     ).pack(anchor="w", pady=(8,2))
        r1 = ctk.CTkFrame(parent, fg_color="transparent")
        r1.pack(fill="x")
        self.e_sm = ctk.CTkEntry(r1, height=30, fg_color=PANEL_BG,
                                 border_color=BORDER, text_color=TEXT,
                                 placeholder_text="Mã SV chính xác")
        self.e_sm.pack(side="left", fill="x", expand=True, padx=(0,4))
        ctk.CTkButton(r1, text="Tìm", width=56, height=30,
                      fg_color=ACCENT, command=self._on_search_masv).pack(side="left")

        ctk.CTkLabel(parent, text="Tìm theo Họ Tên (tiền tố):",
                     text_color=TEXT2, font=ctk.CTkFont("Segoe UI", 11)
                     ).pack(anchor="w", pady=(10,2))
        r2 = ctk.CTkFrame(parent, fg_color="transparent")
        r2.pack(fill="x")
        self.e_sh = ctk.CTkEntry(r2, height=30, fg_color=PANEL_BG,
                                 border_color=BORDER, text_color=TEXT,
                                 placeholder_text="Họ tên hoặc tiền tố...")
        self.e_sh.pack(side="left", fill="x", expand=True, padx=(0,4))
        ctk.CTkButton(r2, text="Tìm", width=56, height=30,
                      fg_color=ACCENT, command=self._on_search_hoten).pack(side="left")

        ctk.CTkButton(parent, text="↺  Hiện tất cả", height=28,
                      fg_color=PANEL_BG, hover_color=BORDER,
                      text_color=TEXT2, command=self._clear_search
                      ).pack(fill="x", pady=(8,0))
        self.lbl_result = ctk.CTkLabel(parent, text="", text_color=ACCENT2,
                                       font=ctk.CTkFont("Segoe UI", 10),
                                       wraplength=250)
        self.lbl_result.pack(anchor="w", pady=(6,0))

    # ── RIGHT ───────────────────────────────────────
    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(5,0))
        right.rowconfigure(2, weight=2)
        right.rowconfigure(4, weight=1)
        right.columnconfigure(0, weight=1)

        # Log bar
        self.lbl_log = ctk.CTkLabel(right, text="Sẵn sàng.",
                                    fg_color=CARD_BG, corner_radius=6,
                                    text_color=TEXT2,
                                    font=ctk.CTkFont("Consolas", 11),
                                    anchor="w", padx=10)
        self.lbl_log.pack(fill="x", padx=10, pady=(5,2))

        # Animation step label
        self.lbl_step = ctk.CTkLabel(right, text="",
                                     fg_color="transparent",
                                     text_color="#a78bfa",
                                     font=ctk.CTkFont("Consolas", 11),
                                     anchor="w", padx=10, wraplength=640)
        self.lbl_step.pack(fill="x", padx=10, pady=(0,2))

        # Canvas Mã SV
        ctk.CTkLabel(right, text="🌲  Index B-Tree — Mã SV  (bậc 3)",
                     font=ctk.CTkFont("Segoe UI", 11, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=12, pady=(2,1))
        cf1 = tk.Frame(right, bg="#0f172a")
        cf1.pack(fill="both", expand=True, padx=10, pady=(0,4))
        self.cv_masv = tk.Canvas(cf1, bg="#0f172a", highlightthickness=0)
        sb1v = ttk.Scrollbar(cf1, orient="vertical",   command=self.cv_masv.yview)
        sb1h = ttk.Scrollbar(cf1, orient="horizontal", command=self.cv_masv.xview)
        self.cv_masv.configure(yscrollcommand=sb1v.set, xscrollcommand=sb1h.set)
        sb1v.pack(side="right", fill="y"); sb1h.pack(side="bottom", fill="x")
        self.cv_masv.pack(fill="both", expand=True)
        self.viz_masv = AnimatedTreeVisualizer(self.cv_masv, self.lbl_step)

        # Canvas Họ Tên
        ctk.CTkLabel(right, text="🌲  Index B-Tree — Họ Tên  (bậc 3)",
                     font=ctk.CTkFont("Segoe UI", 11, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=12, pady=(2,1))
        cf2 = tk.Frame(right, bg="#0f172a")
        cf2.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.cv_hoten = tk.Canvas(cf2, bg="#0f172a", highlightthickness=0)
        sb2v = ttk.Scrollbar(cf2, orient="vertical",   command=self.cv_hoten.yview)
        sb2h = ttk.Scrollbar(cf2, orient="horizontal", command=self.cv_hoten.xview)
        self.cv_hoten.configure(yscrollcommand=sb2v.set, xscrollcommand=sb2h.set)
        sb2v.pack(side="right", fill="y"); sb2h.pack(side="bottom", fill="x")
        self.cv_hoten.pack(fill="both", expand=True)
        self.viz_hoten = AnimatedTreeVisualizer(self.cv_hoten)

    # ════════════════════════════════════════════════
    #  ACTIONS
    # ════════════════════════════════════════════════
    def _on_add(self):
        if self.viz_masv.is_animating():
            self._log("⏳ Đang animation, vui lòng chờ...", "warn")
            return

        ma_sv   = self.e_masv.get().strip()
        ho_ten  = self.e_hoten.get().strip()
        gt      = self.e_gt.get().strip()
        ns      = self.e_ns.get().strip()
        khoa    = self.e_khoa.get().strip()
        gpa_s   = self.e_gpa.get().strip()
        try:
            gpa = float(gpa_s) if gpa_s else 0.0
        except ValueError:
            self._log("⚠ GPA phải là số!", "warn"); return

        # Clone cây TRƯỚC khi thêm
        tree_masv_before  = clone_btree(self.db.index_masv)
        tree_hoten_before = clone_btree(self.db.index_hoten)

        s = Student(ma_sv, ho_ten, gt, ns, khoa, gpa)
        ok, msg = self.db.add(s)
        self._log(("✅  " if ok else "❌  ") + msg, "ok" if ok else "err")

        if ok:
            self._clear_add_form()
            self._refresh_table()

            # Cây SAU khi thêm
            tree_masv_after  = self.db.index_masv
            tree_hoten_after = self.db.index_hoten

            # Animation cây Mã SV
            self.viz_masv.animate_insert(
                tree_masv_before, s.ma_sv, tree_masv_after,
                on_done=lambda: [self.viz_hoten.animate_insert(
                    tree_hoten_before, s.ho_ten.lower(), tree_hoten_after),
                    self._draw_static_both()]
            )
            self._clear_add_form()

    def _on_delete(self):
        if self.viz_masv.is_animating():
            self._log("⏳ Đang animation, vui lòng chờ...", "warn"); return

        ma_sv = self.e_del.get().strip().upper()
        if not ma_sv:
            self._log("⚠ Vui lòng nhập Mã SV!", "warn"); return

        student = self.db.find_by_masv(ma_sv)
        ho_ten_lower = student.ho_ten.lower() if student else None

        # Clone trước
        tree_masv_before  = clone_btree(self.db.index_masv)
        tree_hoten_before = clone_btree(self.db.index_hoten)

        ok, msg = self.db.delete(ma_sv)
        self._log(("✅  " if ok else "❌  ") + msg, "ok" if ok else "err")

        if ok:
            self.e_del.delete(0, "end")
            self._refresh_table()

            tree_masv_after  = self.db.index_masv
            tree_hoten_after = self.db.index_hoten

            self.viz_masv.animate_delete(
                tree_masv_before, ma_sv, tree_masv_after,
                on_done=lambda: (
                    self.viz_hoten.animate_delete(
                        tree_hoten_before,
                        ho_ten_lower or "",
                        tree_hoten_after
                    ) if ho_ten_lower else None
                )
            )

    def _on_search_masv(self):
        if self.viz_masv.is_animating():
            self._log("⏳ Đang animation...", "warn"); return
        ma_sv = self.e_sm.get().strip().upper()
        if not ma_sv:
            return
        found = self.db.find_by_masv(ma_sv) is not None
        self.viz_masv.animate_search(self.db.index_masv, ma_sv, found)

        if found:
            s = self.db.table.get(ma_sv)
            self.lbl_result.configure(
                text=f"✅ {s.ho_ten} | {s.khoa} | GPA {s.gpa}", text_color=ACCENT2)
            try:
                self.tbl.selection_set(ma_sv)
                self.tbl.see(ma_sv)
            except Exception:
                pass
        else:
            self.lbl_result.configure(
                text=f"❌ Không tìm thấy: {ma_sv}", text_color=DANGER)

    def _on_search_hoten(self):
        if self.viz_hoten.is_animating():
            self._log("⏳ Đang animation...", "warn"); return
        keyword = self.e_sh.get().strip()
        if not keyword:
            return
        results = self.db.find_by_hoten(keyword)
        found = len(results) > 0
        self.viz_hoten.animate_search(self.db.index_hoten, keyword.lower(), found)
        if found:
            self.lbl_result.configure(
                text=f"✅ {len(results)} kết quả: {', '.join(s.ho_ten for s in results[:4])}",
                text_color=ACCENT2)
            self._refresh_table(results)
        else:
            self.lbl_result.configure(
                text=f"❌ Không tìm thấy: '{keyword}'", text_color=DANGER)

    def _clear_search(self):
        self.lbl_result.configure(text="")
        self._refresh_table()
        self._draw_static_both()

    # ════════════════════════════════════════════════
    #  HELPERS
    # ════════════════════════════════════════════════
    def _refresh_table(self, students=None):
        for row in self.tbl.get_children():
            self.tbl.delete(row)
        data = students or self.db.all_students()
        for s in data:
            self.tbl.insert("", "end", iid=s.ma_sv,
                            values=(s.ma_sv, s.ho_ten, s.gioi_tinh,
                                    s.ngay_sinh, s.khoa, s.gpa))
        self.lbl_count.configure(text=f"{self.db.count()} sinh viên")

    def _draw_static_both(self):
        self.update_idletasks()
        self.viz_masv.draw_static(self.db.index_masv)
        self.viz_hoten.draw_static(self.db.index_hoten)

    def _clear_add_form(self):
        for a in ("e_masv","e_hoten","e_ns","e_khoa","e_gpa"):
            getattr(self, a).delete(0, "end")
        self.e_gt.set("Nam")

    def _log(self, msg, kind="info"):
        colors = {"ok": ACCENT2, "err": DANGER, "warn": "#f59e0b", "info": TEXT2}
        self.lbl_log.configure(text=msg, text_color=colors.get(kind, TEXT2))


if __name__ == "__main__":
    app = App()
    app.mainloop()