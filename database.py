"""
Mô hình dữ liệu Sinh Viên + Database quản lý bảng gốc và 2 index B-Tree.
  - index_masv:  key = mã SV   (vd: "SV001")
  - index_hoten: key = họ tên chữ thường (vd: "nguyen van a")
"""
import json, os, sys
from btree import BTree

def get_executable_dir():
    if getattr(sys, 'frozen', False):
        # Nếu đang chạy từ file EXE
        return os.path.dirname(sys.executable)
    else:
        # Nếu đang chạy code .py bình thường
        return os.path.dirname(os.path.abspath(__file__))

class Student:
    def __init__(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, khoa, gpa=0.0):
        self.ma_sv      = ma_sv.strip().upper()
        self.ho_ten     = ho_ten.strip()
        self.gioi_tinh  = gioi_tinh.strip()
        self.ngay_sinh  = ngay_sinh.strip()
        self.khoa       = khoa.strip()
        self.gpa        = float(gpa)

    def to_dict(self):
        return {"ma_sv": self.ma_sv, "ho_ten": self.ho_ten,
                "gioi_tinh": self.gioi_tinh, "ngay_sinh": self.ngay_sinh,
                "khoa": self.khoa, "gpa": self.gpa}

    @staticmethod
    def from_dict(d):
        return Student(d["ma_sv"], d["ho_ten"], d["gioi_tinh"],
                       d["ngay_sinh"], d["khoa"], d.get("gpa", 0.0))

    def __repr__(self):
        return f"Student({self.ma_sv}, {self.ho_ten})"


class StudentDB:
    DATA_FILE = os.path.join(get_executable_dir(), "students.json")

    def __init__(self):
        self.table:       dict[str, Student] = {}
        self.index_masv  = BTree()
        self.index_hoten = BTree()
        self._load()

    def _load(self):
        if not os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            return
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for d in data:
                s = Student.from_dict(d)
                self.table[s.ma_sv] = s
                self.index_masv.insert(s.ma_sv, s.ma_sv)
                self.index_hoten.insert(s.ho_ten.lower(), s.ma_sv)
        except json.JSONDecodeError:
            self.table = {}

    def _save(self):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.table.values()],
                      f, ensure_ascii=False, indent=2)

    def add(self, student: Student):
        if not student.ma_sv:
            return False, "Mã SV không được để trống!"
        if not student.ho_ten:
            return False, "Họ tên không được để trống!"
        if student.ma_sv in self.table:
            return False, f"Mã SV '{student.ma_sv}' đã tồn tại!"
        self.table[student.ma_sv] = student
        self.index_masv.insert(student.ma_sv, student.ma_sv)
        self.index_hoten.insert(student.ho_ten.lower(), student.ma_sv)
        self._save()
        return True, f"Đã thêm sinh viên {student.ma_sv} – {student.ho_ten}"

    def delete(self, ma_sv: str):
        ma_sv = ma_sv.strip().upper()
        if ma_sv not in self.table:
            return False, f"Không tìm thấy Mã SV '{ma_sv}'!"
        s = self.table.pop(ma_sv)
        self.index_masv.delete(ma_sv)
        self.index_hoten.delete(s.ho_ten.lower())
        self._save()
        return True, f"Đã xóa '{s.ho_ten}' (Mã: {ma_sv})"

    def find_by_masv(self, ma_sv: str):
        ma_sv = ma_sv.strip().upper()
        r = self.index_masv.search(ma_sv)
        return self.table.get(ma_sv) if r else None

    def find_by_hoten(self, keyword: str):
        matches = self.index_hoten.search_prefix(keyword.lower())
        return [self.table[sid] for _, sid in matches if sid in self.table]

    def all_students(self):
        return list(self.table.values())

    def count(self):
        return len(self.table)
    