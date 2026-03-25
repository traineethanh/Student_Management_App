"""
B-Tree bậc 3 (order = 3):
  - Mỗi node tối đa 2 keys, tối đa 3 children
  - Mỗi node (trừ root) tối thiểu 1 key
"""


class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []        # list of (key_value, student_id)
        self.children = []    # list of BTreeNode
        self.leaf = leaf

    def __repr__(self):
        return f"Node(keys={[k for k,_ in self.keys]}, leaf={self.leaf})"


class BTree:
    ORDER = 3          # bậc cây
    MAX_KEYS = ORDER - 1   # = 2
    MIN_KEYS = 1

    def __init__(self):
        self.root = BTreeNode(leaf=True)

    # ── SEARCH ──────────────────────────────────────
    def search(self, key, node=None):
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

    def search_prefix(self, prefix, node=None, results=None):
        """Tìm tất cả keys có giá trị bắt đầu bằng prefix."""
        if results is None:
            results = []
        if node is None:
            node = self.root
        for key, sid in node.keys:
            if str(key).lower().startswith(prefix.lower()):
                results.append((key, sid))
        if not node.leaf:
            for child in node.children:
                self.search_prefix(prefix, child, results)
        return results

    # ── INSERT ──────────────────────────────────────
    def insert(self, key, student_id):
        root = self.root
        if len(root.keys) == self.MAX_KEYS:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, student_id)

    def _insert_non_full(self, node, key, student_id):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i][0]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = (key, student_id)
        else:
            while i >= 0 and key < node.keys[i][0]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == self.MAX_KEYS:
                self._split_child(node, i)
                if key > node.keys[i][0]:
                    i += 1
            self._insert_non_full(node.children[i], key, student_id)

    def _split_child(self, parent, i):
        child = parent.children[i]
        mid = len(child.keys) // 2  # = 1

        new_node = BTreeNode(leaf=child.leaf)
        mid_key = child.keys[mid]

        new_node.keys = child.keys[mid + 1:]
        child.keys = child.keys[:mid]

        if not child.leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

        parent.keys.insert(i, mid_key)
        parent.children.insert(i + 1, new_node)

    # ── DELETE ──────────────────────────────────────
    def delete(self, key):
        self._delete(self.root, key)
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
                pred = self._get_predecessor(node, i)
                node.keys[i] = pred
                self._delete(node.children[i], pred[0])
        else:
            if node.leaf:
                return
            self._ensure_child(node, i)
            if i > len(node.keys):
                i -= 1
            self._delete(node.children[i], key)

    def _get_predecessor(self, node, i):
        cur = node.children[i]
        while not cur.leaf:
            cur = cur.children[-1]
        return cur.keys[-1]

    def _ensure_child(self, node, i):
        child = node.children[i]
        if len(child.keys) > self.MIN_KEYS:
            return
        if i > 0 and len(node.children[i - 1].keys) > self.MIN_KEYS:
            self._borrow_from_prev(node, i)
        elif i < len(node.children) - 1 and len(node.children[i + 1].keys) > self.MIN_KEYS:
            self._borrow_from_next(node, i)
        else:
            if i < len(node.children) - 1:
                self._merge(node, i)
            else:
                self._merge(node, i - 1)

    def _borrow_from_prev(self, node, i):
        child = node.children[i]
        sibling = node.children[i - 1]
        child.keys.insert(0, node.keys[i - 1])
        node.keys[i - 1] = sibling.keys.pop()
        if not sibling.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]
        child.keys.append(node.keys[i])
        node.keys[i] = sibling.keys.pop(0)
        if not sibling.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]
        mid_key = node.keys.pop(i)
        child.keys.append(mid_key)
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        node.children.pop(i + 1)

    # ── TRAVERSAL ───────────────────────────────────
    def inorder(self, node=None):
        if node is None:
            node = self.root
        result = []
        if node.leaf:
            return [k for k, _ in node.keys]
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
