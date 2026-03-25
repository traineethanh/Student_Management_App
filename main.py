"""
Ứng dụng Quản Lý Sinh Viên
Giao diện: CustomTkinter
Index:      B-Tree bậc 3
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from database import StudentDB, Student
from visualizer import TreeVisualizer

# ── THEME ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK_BG    = "#0f172a"
PANEL_BG   = "#1e293b"
CARD_BG    = "#1e2a3a"
ACCENT     = "#3b82f6"
ACCENT2    = "#22c55e"
DANGER     = "#ef4444"
TEXT       = "#e2e8f0"
TEXT2      = "#94a3b8"
BORDER     = "#334155"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quản Lý Sinh Viên  ·  B-Tree Index")
        self.geometry("1300x780")
        self.minsize(1100, 680)
        self.configure(fg_color=DARK_BG)

        self.db = StudentDB()
        self._build_ui()
        self._refresh_table()
        self._refresh_trees()

    # ════════════════════════════════════════════════
    #   BUILD UI
    # ════════════════════════════════════════════════
    def _build_ui(self):
        # ── Header ──────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=PANEL_BG, height=56, corner_radius=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="🎓  Quản Lý Sinh Viên",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=TEXT).pack(side="left", padx=24, pady=12)

        self.lbl_count = ctk.CTkLabel(hdr, text="0 sinh viên",
                                      font=ctk.CTkFont("Segoe UI", 13),
                                      text_color=TEXT2)
        self.lbl_count.pack(side="right", padx=24)

        # ── Main body (left panel + right panel) ────
        body = ctk.CTkFrame(self, fg_color=DARK_BG)
        body.pack(fill="both", expand=True, padx=10, pady=8)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=4)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    # ── LEFT PANEL ──────────────────────────────────
    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # --- Tabs: Thêm / Xóa / Tìm
        tab = ctk.CTkTabview(left, fg_color=CARD_BG,
                             segmented_button_fg_color=PANEL_BG,
                             segmented_button_selected_color=ACCENT)
        tab.pack(fill="x", padx=12, pady=(12, 4))
        tab.add("➕ Thêm")
        tab.add("🗑 Xóa")
        tab.add("🔍 Tìm")

        self._build_tab_add(tab.tab("➕ Thêm"))
        self._build_tab_delete(tab.tab("🗑 Xóa"))
        self._build_tab_search(tab.tab("🔍 Tìm"))

        # --- Bảng sinh viên
        tbl_frame = ctk.CTkFrame(left, fg_color=CARD_BG, corner_radius=10)
        tbl_frame.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        ctk.CTkLabel(tbl_frame, text="📋  Bảng Dữ Liệu Gốc",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=12, pady=(10, 4))

        cols = ("Mã SV", "Họ và Tên", "Giới tính", "Ngày sinh", "Khoa", "GPA")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                        background=CARD_BG, foreground=TEXT,
                        fieldbackground=CARD_BG, rowheight=28,
                        font=("Segoe UI", 11))
        style.configure("Dark.Treeview.Heading",
                        background=PANEL_BG, foreground=TEXT2,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Dark.Treeview", background=[("selected", ACCENT)])

        tree_wrap = tk.Frame(tbl_frame, bg=CARD_BG)
        tree_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.tree_tbl = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                                     style="Dark.Treeview",
                                     yscrollcommand=vsb.set,
                                     xscrollcommand=hsb.set)
        vsb.config(command=self.tree_tbl.yview)
        hsb.config(command=self.tree_tbl.xview)
        self.tree_tbl.pack(fill="both", expand=True)

        widths = [80, 150, 80, 90, 120, 50]
        for col, w in zip(cols, widths):
            self.tree_tbl.heading(col, text=col)
            self.tree_tbl.column(col, width=w, anchor="center")

    def _build_tab_add(self, parent):
        fields = [
            ("Mã SV *",    "entry_masv"),
            ("Họ và Tên *","entry_hoten"),
            ("Giới tính",  "entry_gioitinh"),
            ("Ngày sinh",  "entry_ngaysinh"),
            ("Khoa",       "entry_khoa"),
            ("GPA",        "entry_gpa"),
        ]
        for label, attr in fields:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, width=100, anchor="w",
                         font=ctk.CTkFont("Segoe UI", 12),
                         text_color=TEXT2).pack(side="left")
            entry = ctk.CTkEntry(row, height=30,
                                 fg_color=PANEL_BG, border_color=BORDER,
                                 text_color=TEXT)
            entry.pack(side="left", fill="x", expand=True)
            setattr(self, attr, entry)

        # Combobox cho giới tính
        self.entry_gioitinh.destroy()
        row_gt = parent.winfo_children()[2]
        self.entry_gioitinh = ctk.CTkComboBox(
            row_gt, values=["Nam", "Nữ", "Khác"],
            fg_color=PANEL_BG, border_color=BORDER, text_color=TEXT,
            button_color=ACCENT, height=30)
        self.entry_gioitinh.set("Nam")
        self.entry_gioitinh.pack(side="left", fill="x", expand=True)

        btn = ctk.CTkButton(parent, text="➕  Thêm Sinh Viên",
                            fg_color=ACCENT2, hover_color="#16a34a",
                            font=ctk.CTkFont("Segoe UI", 13, "bold"),
                            height=36, command=self._on_add)
        btn.pack(fill="x", pady=(8, 4))

    def _build_tab_delete(self, parent):
        ctk.CTkLabel(parent, text="Nhập Mã SV cần xóa:",
                     text_color=TEXT2, font=ctk.CTkFont("Segoe UI", 12)
                     ).pack(anchor="w", pady=(8, 2))
        self.entry_del = ctk.CTkEntry(parent, height=34,
                                      fg_color=PANEL_BG, border_color=BORDER,
                                      text_color=TEXT,
                                      placeholder_text="Ví dụ: SV001")
        self.entry_del.pack(fill="x", pady=4)

        btn = ctk.CTkButton(parent, text="🗑  Xóa Sinh Viên",
                            fg_color=DANGER, hover_color="#b91c1c",
                            font=ctk.CTkFont("Segoe UI", 13, "bold"),
                            height=36, command=self._on_delete)
        btn.pack(fill="x", pady=(8, 4))

    def _build_tab_search(self, parent):
        ctk.CTkLabel(parent, text="Tìm theo Mã SV:",
                     text_color=TEXT2, font=ctk.CTkFont("Segoe UI", 12)
                     ).pack(anchor="w", pady=(8, 2))
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x")
        self.entry_search_masv = ctk.CTkEntry(
            row1, height=32, fg_color=PANEL_BG, border_color=BORDER,
            text_color=TEXT, placeholder_text="Mã SV chính xác")
        self.entry_search_masv.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row1, text="Tìm", width=60, height=32,
                      fg_color=ACCENT, command=self._on_search_masv
                      ).pack(side="left")

        ctk.CTkLabel(parent, text="Tìm theo Họ Tên (tiền tố):",
                     text_color=TEXT2, font=ctk.CTkFont("Segoe UI", 12)
                     ).pack(anchor="w", pady=(10, 2))
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x")
        self.entry_search_hoten = ctk.CTkEntry(
            row2, height=32, fg_color=PANEL_BG, border_color=BORDER,
            text_color=TEXT, placeholder_text="Họ tên hoặc tiền tố...")
        self.entry_search_hoten.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row2, text="Tìm", width=60, height=32,
                      fg_color=ACCENT, command=self._on_search_hoten
                      ).pack(side="left")

        ctk.CTkButton(parent, text="↺  Hiện tất cả", height=30,
                      fg_color=PANEL_BG, hover_color=BORDER,
                      text_color=TEXT2, command=self._clear_search
                      ).pack(fill="x", pady=(10, 0))

        # Kết quả tìm
        self.lbl_result = ctk.CTkLabel(parent, text="",
                                       text_color=ACCENT2,
                                       font=ctk.CTkFont("Segoe UI", 11),
                                       wraplength=260)
        self.lbl_result.pack(anchor="w", pady=(8, 0))

    # ── RIGHT PANEL ─────────────────────────────────
    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.rowconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        # --- Log / status bar
        self.lbl_log = ctk.CTkLabel(right, text="Sẵn sàng.",
                                    fg_color=CARD_BG, corner_radius=6,
                                    text_color=TEXT2,
                                    font=ctk.CTkFont("Consolas", 11),
                                    anchor="w", padx=10)
        self.lbl_log.pack(fill="x", padx=12, pady=(10, 6))

        # --- Index Mã SV
        ctk.CTkLabel(right,
                     text="🌲  Index B-Tree theo Mã SV  (bậc 3)",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=14, pady=(4, 2))

        canvas_frame1 = tk.Frame(right, bg="#0f172a", bd=0)
        canvas_frame1.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.canvas_masv = tk.Canvas(canvas_frame1, bg="#0f172a",
                                     highlightthickness=0)
        vsb1 = ttk.Scrollbar(canvas_frame1, orient="vertical",
                              command=self.canvas_masv.yview)
        hsb1 = ttk.Scrollbar(canvas_frame1, orient="horizontal",
                              command=self.canvas_masv.xview)
        self.canvas_masv.configure(yscrollcommand=vsb1.set,
                                   xscrollcommand=hsb1.set)
        vsb1.pack(side="right", fill="y")
        hsb1.pack(side="bottom", fill="x")
        self.canvas_masv.pack(fill="both", expand=True)
        self.viz_masv = TreeVisualizer(self.canvas_masv)

        # --- Index Họ Tên
        ctk.CTkLabel(right,
                     text="🌲  Index B-Tree theo Họ Tên  (bậc 3)",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=14, pady=(2, 2))

        canvas_frame2 = tk.Frame(right, bg="#0f172a", bd=0)
        canvas_frame2.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.canvas_hoten = tk.Canvas(canvas_frame2, bg="#0f172a",
                                      highlightthickness=0)
        vsb2 = ttk.Scrollbar(canvas_frame2, orient="vertical",
                              command=self.canvas_hoten.yview)
        hsb2 = ttk.Scrollbar(canvas_frame2, orient="horizontal",
                              command=self.canvas_hoten.xview)
        self.canvas_hoten.configure(yscrollcommand=vsb2.set,
                                    xscrollcommand=hsb2.set)
        vsb2.pack(side="right", fill="y")
        hsb2.pack(side="bottom", fill="x")
        self.canvas_hoten.pack(fill="both", expand=True)
        self.viz_hoten = TreeVisualizer(self.canvas_hoten)

    # ════════════════════════════════════════════════
    #   ACTIONS
    # ════════════════════════════════════════════════
    def _on_add(self):
        ma_sv     = self.entry_masv.get().strip()
        ho_ten    = self.entry_hoten.get().strip()
        gioitinh  = self.entry_gioitinh.get().strip()
        ngaysinh  = self.entry_ngaysinh.get().strip()
        khoa      = self.entry_khoa.get().strip()
        gpa_str   = self.entry_gpa.get().strip()

        try:
            gpa = float(gpa_str) if gpa_str else 0.0
        except ValueError:
            self._log("⚠  GPA phải là số!", "warn")
            return

        s = Student(ma_sv, ho_ten, gioitinh, ngaysinh, khoa, gpa)
        ok, msg = self.db.add(s)
        self._log(("✅  " if ok else "❌  ") + msg, "ok" if ok else "err")

        if ok:
            self._clear_add_form()
            self._refresh_table()
            # Highlight node vừa thêm
            result_masv = self.db.index_masv.search(ma_sv)
            result_hoten = self.db.index_hoten.search(ho_ten.lower())
            hl_masv  = [id(result_masv[0])]  if result_masv  else []
            hl_hoten = [id(result_hoten[0])] if result_hoten else []
            self.viz_masv.set_highlight(hl_masv, "highlight_add")
            self.viz_hoten.set_highlight(hl_hoten, "highlight_add")
            self._refresh_trees()
            self.after(1500, self._clear_hl)

    def _on_delete(self):
        ma_sv = self.entry_del.get().strip().upper()
        if not ma_sv:
            self._log("⚠  Vui lòng nhập Mã SV cần xóa!", "warn")
            return

        # Lấy họ tên trước khi xóa (để tìm node trên cây họ tên)
        student = self.db.find_by_masv(ma_sv)
        ho_ten_lower = student.ho_ten.lower() if student else None

        ok, msg = self.db.delete(ma_sv)
        self._log(("✅  " if ok else "❌  ") + msg, "ok" if ok else "err")

        if ok:
            self.entry_del.delete(0, "end")
            self._refresh_table()
            self._refresh_trees()

    def _on_search_masv(self):
        ma_sv = self.entry_search_masv.get().strip().upper()
        if not ma_sv:
            return
        result = self.db.index_masv.search(ma_sv)
        if result:
            node, _ = result
            self.viz_masv.set_highlight([id(node)], "highlight_found")
            self.viz_hoten.clear_highlight()
            self._refresh_trees()
            s = self.db.table.get(ma_sv)
            self.lbl_result.configure(
                text=f"✅ Tìm thấy: {s.ho_ten} | {s.khoa} | GPA {s.gpa}",
                text_color=ACCENT2)
            self._highlight_row(ma_sv)
        else:
            self.viz_masv.clear_highlight()
            self._refresh_trees()
            self.lbl_result.configure(
                text=f"❌ Không tìm thấy Mã SV: {ma_sv}", text_color=DANGER)
        self._log(f"🔍 Tìm Mã SV '{ma_sv}': {'Thấy' if result else 'Không thấy'}")
        self.after(2000, self._clear_hl)

    def _on_search_hoten(self):
        keyword = self.entry_search_hoten.get().strip()
        if not keyword:
            return
        results = self.db.find_by_hoten(keyword)
        if results:
            # Highlight tất cả node khớp trên cây họ tên
            node_ids = []
            for s in results:
                r = self.db.index_hoten.search(s.ho_ten.lower())
                if r:
                    node_ids.append(id(r[0]))
            self.viz_hoten.set_highlight(node_ids, "highlight_found")
            self.viz_masv.clear_highlight()
            self._refresh_trees()
            names = ", ".join(s.ho_ten for s in results[:5])
            self.lbl_result.configure(
                text=f"✅ {len(results)} kết quả: {names}{'...' if len(results)>5 else ''}",
                text_color=ACCENT2)
            self._refresh_table(results)
        else:
            self.viz_hoten.clear_highlight()
            self._refresh_trees()
            self.lbl_result.configure(
                text=f"❌ Không tìm thấy họ tên: '{keyword}'", text_color=DANGER)
        self._log(f"🔍 Tìm họ tên '{keyword}': {len(results)} kết quả")
        self.after(2500, self._clear_hl)

    def _clear_search(self):
        self.lbl_result.configure(text="")
        self.viz_masv.clear_highlight()
        self.viz_hoten.clear_highlight()
        self._refresh_table()
        self._refresh_trees()

    # ════════════════════════════════════════════════
    #   REFRESH
    # ════════════════════════════════════════════════
    def _refresh_table(self, students=None):
        for row in self.tree_tbl.get_children():
            self.tree_tbl.delete(row)
        data = students if students is not None else self.db.all_students()
        for s in data:
            self.tree_tbl.insert("", "end", iid=s.ma_sv,
                                 values=(s.ma_sv, s.ho_ten, s.gioi_tinh,
                                         s.ngay_sinh, s.khoa, s.gpa))
        self.lbl_count.configure(text=f"{self.db.count()} sinh viên")

    def _refresh_trees(self):
        self.update_idletasks()
        self.viz_masv.draw(self.db.index_masv)
        self.viz_hoten.draw(self.db.index_hoten)

    def _highlight_row(self, ma_sv):
        try:
            self.tree_tbl.selection_set(ma_sv)
            self.tree_tbl.see(ma_sv)
        except Exception:
            pass

    def _clear_hl(self):
        self.viz_masv.clear_highlight()
        self.viz_hoten.clear_highlight()
        self._refresh_trees()

    def _clear_add_form(self):
        for attr in ("entry_masv", "entry_hoten", "entry_ngaysinh",
                     "entry_khoa", "entry_gpa"):
            getattr(self, attr).delete(0, "end")
        self.entry_gioitinh.set("Nam")

    def _log(self, msg, kind="info"):
        colors = {"ok": ACCENT2, "err": DANGER, "warn": "#f59e0b", "info": TEXT2}
        self.lbl_log.configure(text=msg, text_color=colors.get(kind, TEXT2))


# ════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
