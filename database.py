"""
Mô hình dữ liệu Sinh Viên và lớp Database quản lý dữ liệu + index.
"""
import json
import os
from btree import BTree


class Student:
    def __init__(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, khoa, gpa=0.0):
        self.ma_sv = ma_sv.strip().upper()
        self.ho_ten = ho_ten.strip()
        self.gioi_tinh = gioi_tinh.strip()
        self.ngay_sinh = ngay_sinh.strip()
        self.khoa = khoa.strip()
        self.gpa = float(gpa)

    def to_dict(self):
        return {
            "ma_sv": self.ma_sv,
            "ho_ten": self.ho_ten,
            "gioi_tinh": self.gioi_tinh,
            "ngay_sinh": self.ngay_sinh,
            "khoa": self.khoa,
            "gpa": self.gpa,
        }

    @staticmethod
    def from_dict(d):
        return Student(
            d["ma_sv"], d["ho_ten"], d["gioi_tinh"],
            d["ngay_sinh"], d["khoa"], d.get("gpa", 0.0)
        )

    def __repr__(self):
        return f"Student({self.ma_sv}, {self.ho_ten})"


class StudentDB:
    """
    Bảng gốc: dict  ma_sv -> Student
    Index 1 : BTree theo Mã SV
    Index 2 : BTree theo Họ Tên (chữ thường)
    """

    DATA_FILE = "students.json"

    def __init__(self):
        self.table: dict[str, Student] = {}   # bảng gốc
        self.index_masv = BTree()              # index theo mã SV
        self.index_hoten = BTree()             # index theo họ tên
        self._load()

    # ── PERSISTENCE ─────────────────────────────────
    def _load(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for d in data:
                s = Student.from_dict(d)
                self.table[s.ma_sv] = s
                self.index_masv.insert(s.ma_sv, s.ma_sv)
                self.index_hoten.insert(s.ho_ten.lower(), s.ma_sv)

    def _save(self):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.table.values()], f,
                      ensure_ascii=False, indent=2)

    # ── THÊM ────────────────────────────────────────
    def add(self, student: Student) -> tuple[bool, str]:
        if student.ma_sv in self.table:
            return False, f"Mã SV '{student.ma_sv}' đã tồn tại!"
        if not student.ma_sv:
            return False, "Mã SV không được để trống!"
        if not student.ho_ten:
            return False, "Họ tên không được để trống!"

        # 1. Thêm vào bảng gốc
        self.table[student.ma_sv] = student
        # 2. Cập nhật index
        self.index_masv.insert(student.ma_sv, student.ma_sv)
        self.index_hoten.insert(student.ho_ten.lower(), student.ma_sv)
        self._save()
        return True, f"Đã thêm sinh viên '{student.ho_ten}' thành công!"

    # ── XÓA ─────────────────────────────────────────
    def delete(self, ma_sv: str) -> tuple[bool, str]:
        ma_sv = ma_sv.strip().upper()
        if ma_sv not in self.table:
            return False, f"Không tìm thấy Mã SV '{ma_sv}'!"

        student = self.table[ma_sv]
        # 1. Xóa khỏi bảng gốc
        del self.table[ma_sv]
        # 2. Xóa khỏi index
        self.index_masv.delete(ma_sv)
        self.index_hoten.delete(student.ho_ten.lower())
        self._save()
        return True, f"Đã xóa sinh viên '{student.ho_ten}' (Mã: {ma_sv})!"

    # ── TÌM KIẾM ────────────────────────────────────
    def find_by_masv(self, ma_sv: str):
        """Tìm qua index_masv, trả về Student hoặc None."""
        ma_sv = ma_sv.strip().upper()
        result = self.index_masv.search(ma_sv)
        if result:
            return self.table.get(ma_sv)
        return None

    def find_by_hoten(self, keyword: str):
        """Tìm prefix qua index_hoten, trả về list Student."""
        matches = self.index_hoten.search_prefix(keyword.lower())
        students = []
        for _, sid in matches:
            if sid in self.table:
                students.append(self.table[sid])
        return students

    # ── DANH SÁCH ───────────────────────────────────
    def all_students(self):
        return list(self.table.values())

    def count(self):
        return len(self.table)
