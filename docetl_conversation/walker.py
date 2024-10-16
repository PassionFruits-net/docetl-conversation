def Tree(object):
    def __init__(self, items):
        tree = {"children": {}}
        for i in items:
            t = tree["children"]
            for j in reversed(i["categories"]):
                c = j["concept"]
                if c not in t:
                    t[c] = dict(j)
                    t[c]["children"] = {}
                t = t[c]["children"]
            c = i["concept"]
            if c not in t:
                t[c] = dict(i)
                t[c]["children"] = {}
        self.tree = tree

    def get_node_path(self, node, tree=None, prefix = ()):
        if tree is None: tree = self.tree
        if tree["concept"] == node:
            return prefix + (tree,)
        if "children" not in tree:
            return None
        for child in tree["children"]:
            path = self.get_node_path(node, tree=child, prefix=prefix + (tree,))
            if path is not None:
                return path
        return None

    def get_leaves(self, t=None):
        if t is None: t = self.tree
        if "children" not in t:
            yield t
        else:
            for c in t["children"]:
                for leaf in self.get_leaves(c):
                    yield leaf

class WalkItem(object):
    def __init__(self, text, **kw):
        self.text = text
        for k, v in kw.items():
            setattr(self, k, v)

    def __str__(self): return self.text
    def __repr__(self): return self.text
                    
class DepthFirstGraphWithTreeBackupWalker(object):
    def __init__(self, items, pool = None):
        self.items = {item["concept"]: item for item in items}
        self.tree = Tree(items)
        self.all = set(self.items.keys())
        self.visited = set()
        self.pool = pool or [items[0]["concept"]]
        self.reason = ("initial",)

    def __iter__(self): return self

    def __next__(self):
        if not self.pool:
            raise StopIteration
            
        res = self.pool.pop()
        reason = self.reason
        self.visited.add(res)

        # The intersection with all is because the LLM generates links to concepts never described elsewhere with
        #the exact same name; need to merge these somewhere
        related = (set(self.items[res]["relatedt_to"]) - self.visited - set(self.pool)).intersection(self.all)
        self.pool.extend(list(sorted(related)))
        self.reason = ("graph",)
        
        if not self.pool:
            path = reversed(self.tree.get_node_path(self.current))
            for item in path:
                leaves = set([l["concept"] for l in self.get_leaves(item)])
                remaining = leaves - self.visited
                if remaining:
                    self.pool = [next(iter(remaining))]
                    self.reason = ("tree",)
                    break
            
        return WalkItem(res, reason=reason)
