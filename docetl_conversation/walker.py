class Tree(object):
    def __init__(self, items, cluster_key="clusters", title_key="concept"):
        self.cluster_key = cluster_key
        self.title_key = title_key
        
        tree = {"children": {}}
        for i in items:
            t = tree["children"]
            for j in reversed(i[self.cluster_key]):
                c = j[self.title_key]
                if c not in t:
                    t[c] = dict(j)
                    t[c]["children"] = {}
                t = t[c]["children"]
            c = i[self.title_key]
            if c not in t:
                t[c] = dict(i)
                t[c]["children"] = {}
        self.tree = tree

    def get_node_path(self, node, tree=None, prefix = ()):
        if tree is None: tree = self.tree
        if tree[self.title_key] == node:
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
    def __init__(self, items, pool = None,
                 title_key = "concept",
                 cluster_key = "clusters",
                 link_key = "related_to",
                 **kw
                 ):
        self.cluster_key = cluster_key
        self.title_key = title_key
        self.link_key = link_key
        
        self.items = {item[self.title_key]: item for item in items}
        self.tree = Tree(
            items,
            title_key = title_key,
            cluster_key = cluster_key)
        self.all = set(self.items.keys())
        self.visited = set()
        self.pool = pool or [items[0][self.title_key]]
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
        related = (set(self.items[res][self.link_key]) - self.visited - set(self.pool)).intersection(self.all)
        self.pool.extend(list(sorted(related)))
        self.reason = ("graph",)
        
        if not self.pool:
            path = reversed(self.tree.get_node_path(res))
            for item in path:
                leaves = set([l[self.title_key] for l in self.get_leaves(item)])
                remaining = leaves - self.visited
                if remaining:
                    self.pool = [next(iter(remaining))]
                    self.reason = ("tree",)
                    break
            
        return WalkItem(res, reason=reason)
