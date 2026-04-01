"""
B-Tree bậc 3 (Order = 3 = max children per node):
  - max_keys = 2  (order - 1)
  - min_keys = 1  (ceil(order/2) - 1)
  - Chiến lược: insert-then-fix (cho node tràn 3 keys rồi split)
    đảm bảo sau split: left=1 key, up=1 key, right=1 key.
"""


class BTreeNode:
    def __init__(self, leaf=True):
        self.keys     = []   
        self.children = []   
        self.leaf     = leaf

    def __repr__(self):
        return "[" + " | ".join(k for k, _ in self.keys) + "]"


class BTree:
    ORDER    = 3
    MAX_KEYS = ORDER - 1   # = 2

    def __init__(self):
        self.root = BTreeNode(leaf=True)

    # ── SEARCH ───────────────────────────────────────────────────────────────
    def search(self, key: str, node=None):
        """Trả về (node, index) nếu tìm thấy, else None."""
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i][0]:
            i += 1
        if i < len(node.keys) and node.keys[i][0] == key:
            return (node, i)
        if node.leaf:
            return None
        return self.search(key, node.children[i])

    def search_prefix(self, prefix: str, node=None, results=None):
        if results is None: results = []
        if node is None: node = self.root
        
        prefix = prefix.lower()
        i = 0
        while i < len(node.keys) and node.keys[i][0].lower() < prefix:
            i += 1

        for j in range(i, len(node.keys)):
            # Nếu key hiện tại bắt đầu bằng prefix -> thêm vào kết quả
            if node.keys[j][0].lower().startswith(prefix):
                results.append(node.keys[j])
            elif node.keys[j][0].lower() > prefix:
                if not node.leaf:
                    self.search_prefix(prefix, node.children[j], results)
                return results

        # Duyệt các nhánh con có khả năng
        if not node.leaf:
            for k in range(i, len(node.children)):
                self.search_prefix(prefix, node.children[k], results)
        return results

    # ── INSERT ───────────────────────────────────────────────────────────────
    def insert(self, key: str, sid: str = ""):
        """
        Chèn key vào cây. Dùng chiến lược insert-then-fix:
        1. Chèn key vào đúng vị trí trong lá (có thể làm tràn lên 3 keys).
        2. Sau đó fix overflow từ dưới lên trên (bottom-up).
        """
        # Chèn thẳng vào lá
        new_mid = self._insert_leaf(self.root, key, sid)

        # Nếu root bị tràn -> tạo root mới
        if new_mid is not None:
            mid_key, right_child = new_mid
            new_root = BTreeNode(leaf=False)
            new_root.keys = [mid_key]
            new_root.children = [self.root, right_child]
            self.root = new_root

    def _insert_leaf(self, node, key, sid):
        """
        Đệ quy chèn key vào lá phù hợp.
        Trả về (mid_key, right_node) nếu node bị overflow, else None.
        """
        i = 0
        while i < len(node.keys) and key > node.keys[i][0]:
            i += 1

        if node.leaf:
            # Chèn thẳng vào lá
            node.keys.insert(i, (key, sid))
            # Kiểm tra overflow
            if len(node.keys) > self.MAX_KEYS:
                return self._split_node(node)
            return None
        else:
            # Đệ quy xuống con
            overflow = self._insert_leaf(node.children[i], key, sid)
            if overflow is not None:
                mid_key, right_child = overflow
                # Chèn mid_key vào node hiện tại
                node.keys.insert(i, mid_key)
                node.children.insert(i + 1, right_child)
                # Kiểm tra overflow
                if len(node.keys) > self.MAX_KEYS:
                    return self._split_node(node)
            return None

    def _split_node(self, node):
        """
        Node đang có MAX_KEYS+1 = 3 keys (overflow).
        Tách thành: left (1 key) | mid_key (lên cha) | right (1 key).
        Trả về (mid_key_tuple, right_node).
        """
        mid = len(node.keys) // 2   

        mid_key = node.keys[mid]

        right = BTreeNode(leaf=node.leaf)
        right.keys = node.keys[mid + 1:]   
        node.keys  = node.keys[:mid]        

        if not node.leaf:
            right.children = node.children[mid + 1:]
            node.children  = node.children[:mid + 1]

        return (mid_key, right)

    # ── DELETE ───────────────────────────────────────────────────────────────
    def delete(self, key: str):
        self._delete(self.root, key)
        # Nếu root trở thành rỗng và có con -> con trở thành root mới
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i][0]:
            i += 1

        if i < len(node.keys) and node.keys[i][0] == key:
            if node.leaf:
                node.keys.pop(i)
            else:
                pred = self._predecessor(node.children[i])
                node.keys[i] = pred
                self._delete(node.children[i], pred[0])
                self._fix_underflow(node, i) 
        else:
            if node.leaf: return
            self._delete(node.children[i], key)
            self._fix_underflow(node, i)

    def _predecessor(self, node):
        """Tìm key lớn nhất trong subtree (phần tử ngoài cùng bên phải)."""
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _fix_underflow(self, parent, i):
        """Sửa underflow tại parent.children[i] nếu có."""
        child = parent.children[i]
        if len(child.keys) >= 1:   
            return

        left_sib  = parent.children[i - 1] if i > 0 else None
        right_sib = parent.children[i + 1] if i < len(parent.children) - 1 else None

        if left_sib and len(left_sib.keys) > 1:
            # Mượn từ anh em trái
            child.keys.insert(0, parent.keys[i - 1])
            parent.keys[i - 1] = left_sib.keys.pop()
            if not left_sib.leaf:
                child.children.insert(0, left_sib.children.pop())

        elif right_sib and len(right_sib.keys) > 1:
            # Mượn từ anh em phải
            child.keys.append(parent.keys[i])
            parent.keys[i] = right_sib.keys.pop(0)
            if not right_sib.leaf:
                child.children.append(right_sib.children.pop(0))

        elif left_sib:
            # Merge child vào left_sib
            left_sib.keys.append(parent.keys.pop(i - 1))
            left_sib.keys.extend(child.keys)
            if not child.leaf:
                left_sib.children.extend(child.children)
            parent.children.pop(i)

        elif right_sib:
            # Merge right_sib vào child
            child.keys.append(parent.keys.pop(i))
            child.keys.extend(right_sib.keys)
            if not right_sib.leaf:
                child.children.extend(right_sib.children)
            parent.children.pop(i + 1)

    # ── UTILITY ──────────────────────────────────────────────────────────────
    def inorder(self, node=None):
        if node is None:
            node = self.root
        if node.leaf:
            return [k for k, _ in node.keys]
        result = []
        for i, child in enumerate(node.children):
            result.extend(self.inorder(child))
            if i < len(node.keys):
                result.append(node.keys[i][0])
        return result

    def get_all_nodes_by_level(self, node=None, level=0, acc=None):
        if acc is None:
            acc = {}
        if node is None:
            node = self.root
        acc.setdefault(level, []).append(node)
        if not node.leaf:
            for child in node.children:
                self.get_all_nodes_by_level(child, level + 1, acc)
        return acc

    def get_edges(self, node=None, acc=None):
        if acc is None:
            acc = []
        if node is None:
            node = self.root
        if not node.leaf:
            for child in node.children:
                acc.append((id(node), id(child)))
                self.get_edges(child, acc)
        return acc