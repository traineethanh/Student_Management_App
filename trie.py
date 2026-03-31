class TrieNode:
    def __init__(self):
        self.children = {}  # {ký_tự: TrieNode}
        self.is_end_of_word = False
        self.student_ids = [] # Lưu danh sách Mã SV (vì tên có thể trùng)

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, name: str, ma_sv: str):
        node = self.root
        for char in name.lower():
            if char not in self.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        if ma_sv not in node.student_ids:
            node.student_ids.append(ma_sv)

    def search_prefix(self, prefix: str):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Từ node cuối của prefix, duyệt lấy tất cả các Mã SV ở các nhánh con
        results = []
        self._collect_all_ids(node, results)
        return list(set(results)) # Loại bỏ trùng lặp

    def _collect_all_ids(self, node, results):
        if node.is_end_of_word:
            results.extend(node.student_ids)
        for child in node.children.values():
            self._collect_all_ids(child, results)