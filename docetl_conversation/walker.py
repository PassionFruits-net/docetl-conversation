class Tree(object):
    def __init__(self, items, cluster_key="clusters", id_key="concept", **kw):
        self.cluster_key = cluster_key
        self.id_key = id_key
        
        tree = {"children": {}}
        self.items = items
        for i in items.values():
            t = tree["children"]
            for j in reversed(i[self.cluster_key]):
                c = j[self.id_key]
                if c not in t:
                    t[c] = dict(j)
                    t[c]["children"] = {}
                t = t[c]["children"]
            c = i[self.id_key]
            if c not in t:
                t[c] = dict(i)
                t[c]["children"] = {}
        self.tree = tree

    def get_node_path(self, node):
        res = []
        t = self.tree
        res.append(t)
        for i in reversed(self.items[node][self.cluster_key]):
            t = t["children"][i[self.id_key]]
            res.append(t)
        return res
        
    def get_leaves(self, t=None):
        if t is None: t = self.tree
        if "children" not in t:
            yield t
        else:
            for c in t["children"].values():
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
                 id_key = "concept",
                 cluster_key = "clusters",
                 link_key = "related_to",
                 **kw
                 ):
        self.cluster_key = cluster_key
        self.id_key = id_key
        self.link_key = link_key
        
        self.items = {item[self.id_key]: item for item in items}
        self.tree = Tree(
            self.items,
            id_key = id_key,
            cluster_key = cluster_key)
        self.all = set(self.items.keys())
        self.visited = set()
        self.pool = pool or [items[0][self.id_key]]
        self.path = None
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
        if res in self.items:
            self.path = self.tree.get_node_path(res)
            related = set(self.items[res][self.link_key]) - self.visited - set(self.pool)
            # related = related.intersection(self.all)
            self.pool.extend(list(sorted(related)))
            self.reason = ("graph",)
        
        if not self.pool:
            path = reversed(self.path)
            for item in path:
                leaves = set([l[self.id_key] for l in self.tree.get_leaves(item)])
                remaining = leaves - self.visited
                if remaining:
                    self.pool = [next(iter(remaining))]
                    self.reason = ("tree",)
                    break
            else:
                self.pool = [next(iter((self.all - self.visited)))]
                
        return WalkItem(res, reason=reason)
