# rope_tree.py (persistent rope with small-leaf in-place optimization)

class RopeNode:
    MAX_LEAF = 64  # threshold for direct mutation (small leaves)

    def __init__(self, left=None, right=None, data=""):
        self.left = left
        self.right = right
        self.data = data
        self.weight = 0
        self.recalc_weight()

    def is_leaf(self):
        return self.left is None and self.right is None

    def recalc_weight(self):
        if self.is_leaf():
            self.weight = len(self.data)
        else:
            self.weight = self.left.length() if self.left else 0

    def length(self):
        if self.is_leaf():
            return len(self.data)
        l = self.left.length() if self.left else 0
        r = self.right.length() if self.right else 0
        return l + r

    def __repr__(self):
        if self.is_leaf():
            return f"Leaf({self.data!r})"
        return f"Node({repr(self.left)}, {repr(self.right)})"


class Rope:
    """Persistent Rope with small-leaf optimization and rebalancing."""

    def __init__(self, text=""):
        if isinstance(text, RopeNode):
            self.root = text
        else:
            self.root = RopeNode(data=str(text))

    # ---------- core utilities ----------
    def get_text(self):
        return self._report(self.root)

    def _report(self, node):
        if node is None:
            return ""
        if node.is_leaf():
            return node.data
        return self._report(node.left) + self._report(node.right)

    def __len__(self):
        return self.root.length()

    # ---------- traversal ----------
    def _collect_leaves(self, node, out):
        if node is None:
            return
        if node.is_leaf():
            out.append(RopeNode(data=node.data))
        else:
            self._collect_leaves(node.left, out)
            self._collect_leaves(node.right, out)

    def _build_balanced(self, leaves, l, r):
        if l >= r:
            return RopeNode(data="")
        if l + 1 == r:
            node = leaves[l]
            node.recalc_weight()
            return node
        mid = (l + r) // 2
        left = self._build_balanced(leaves, l, mid)
        right = self._build_balanced(leaves, mid, r)
        parent = RopeNode(left=left, right=right)
        parent.recalc_weight()
        return parent

    # ---------- split ----------
    def _split_node(self, node, index):
        if node is None:
            return None, None
        if node.is_leaf():
            return RopeNode(data=node.data[:index]), RopeNode(data=node.data[index:])

        left_len = node.left.length() if node.left else 0
        if index < left_len:
            lleft, lright = self._split_node(node.left, index)
            new_right = RopeNode(left=lright, right=node.right)
            new_right.recalc_weight()
            return lleft, new_right
        else:
            rleft, rright = self._split_node(node.right, index - left_len)
            new_left = RopeNode(left=node.left, right=rleft)
            new_left.recalc_weight()
            return new_left, rright

    def split(self, index):
        if index <= 0:
            return Rope(RopeNode(data="")), Rope(self.root)
        if index >= len(self):
            return Rope(self.root), Rope(RopeNode(data=""))
        left_node, right_node = self._split_node(self.root, index)
        return Rope(left_node), Rope(right_node)

    # ---------- concat ----------
    def concat(self, other):
        new_root = RopeNode(left=self.root, right=other.root)
        new_root.recalc_weight()
        return Rope(new_root)

    # ---------- insert ----------
    def insert(self, index, text):
        new_root = self._insert_node(self.root, index, text)
        return Rope(new_root)

    def _insert_node(self, node, index, text):
        if node.is_leaf():
            # in-place edit for small leaves
            if len(node.data) + len(text) <= RopeNode.MAX_LEAF:
                new_text = node.data[:index] + text + node.data[index:]
                return RopeNode(data=new_text)
            else:
                new_text = node.data[:index] + text + node.data[index:]
                mid = len(new_text) // 2
                return RopeNode(
                    left=RopeNode(data=new_text[:mid]),
                    right=RopeNode(data=new_text[mid:])
                )
        else:
            left_len = node.left.length() if node.left else 0
            if index < left_len:
                left = self._insert_node(node.left, index, text)
                return RopeNode(left=left, right=node.right)
            else:
                right = self._insert_node(node.right, index - left_len, text)
                return RopeNode(left=node.left, right=right)

    # ---------- delete ----------
    def delete(self, start, end):
        new_root = self._delete_node(self.root, start, end)
        return Rope(new_root)

    def _delete_node(self, node, start, end):
        if node.is_leaf():
            if end <= len(node.data):
                new_text = node.data[:start] + node.data[end:]
                return RopeNode(data=new_text)
            else:
                new_text = node.data[:start]
                return RopeNode(data=new_text)
        else:
            left_len = node.left.length() if node.left else 0
            right_len = node.right.length() if node.right else 0

            if end <= left_len:
                left = self._delete_node(node.left, start, end)
                return RopeNode(left=left, right=node.right)
            elif start >= left_len:
                right = self._delete_node(node.right, start - left_len, end - left_len)
                return RopeNode(left=node.left, right=right)
            else:
                left = self._delete_node(node.left, start, left_len)
                right = self._delete_node(node.right, 0, end - left_len)
                return RopeNode(left=left, right=right)

    # ---------- rebalance ----------
    def rebalance(self):
        leaves = []
        self._collect_leaves(self.root, leaves)
        if len(leaves) <= 1:
            if leaves:
                leaves[0].recalc_weight()
                return Rope(leaves[0])
            return Rope(RopeNode(data=""))
        new_root = self._build_balanced(leaves, 0, len(leaves))
        return Rope(new_root)
