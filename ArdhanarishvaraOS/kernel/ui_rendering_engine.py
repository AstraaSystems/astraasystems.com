#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  UI Rendering Engine — SovereignOS Virtual DOM, Diffing & Render Pipeline Core
#  File: ui_rendering_engine.py
#===============================================================================

import time
import uuid
import json
from typing import Dict, Any, List, Optional

class UIRenderingEngine:
    """
    Provides:
      • virtual DOM generation
      • diffing & patch computation
      • render pipeline orchestration
      • component tree resolution
      • kernel-driven UI update propagation
    """

    def __init__(self):
        self.vdom_trees: Dict[str, Dict[str, Any]] = {}
        self.render_history: List[Dict[str, Any]] = {}

    #---------------------------------------------------------------------------
    #  CREATE VIRTUAL NODE
    #---------------------------------------------------------------------------
    def _vnode(self, tag: str, props: Dict[str, Any], children: List[Any]) -> Dict[str, Any]:
        return {
            "tag": tag,
            "props": props,
            "children": children
        }

    #---------------------------------------------------------------------------
    #  BUILD VIRTUAL DOM TREE
    #---------------------------------------------------------------------------
    def build_tree(self, name: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        def build(node):
            tag = node.get("tag", "div")
            props = node.get("props", {})
            children = [build(c) for c in node.get("children", [])]
            return self._vnode(tag, props, children)

        tree = build(structure)
        self.vdom_trees[name] = tree

        return {
            "tree_id": f"VDM-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "tree": tree
        }

    #---------------------------------------------------------------------------
    #  DIFF TWO VDOM TREES
    #---------------------------------------------------------------------------
    def diff(self, old: Dict[str, Any], new: Dict[str, Any]) -> List[Dict[str, Any]]:
        patches = []

        def walk(o, n, path="root"):
            if o["tag"] != n["tag"]:
                patches.append({"op": "replace", "path": path, "node": n})
                return

            if o["props"] != n["props"]:
                patches.append({"op": "props", "path": path, "props": n["props"]})

            oc = o.get("children", [])
            nc = n.get("children", [])

            for i in range(max(len(oc), len(nc))):
                p = f"{path}/{i}"
                if i >= len(oc):
                    patches.append({"op": "add", "path": p, "node": nc[i]})
                elif i >= len(nc):
                    patches.append({"op": "remove", "path": p})
                else:
                    walk(oc[i], nc[i], p)

        walk(old, new)
        return patches

    #---------------------------------------------------------------------------
    #  APPLY PATCHES
    #---------------------------------------------------------------------------
    def apply_patches(self, tree: Dict[str, Any], patches: List[Dict[str, Any]]) -> Dict[str, Any]:
        def get_node(path):
            parts = path.split("/")[1:]
            node = tree
            for p in parts:
                if p.isdigit():
                    node = node["children"][int(p)]
            return node

        for p in patches:
            op = p["op"]
            path = p["path"]

            if op == "replace":
                parent_path = "/".join(path.split("/")[:-1])
                idx = int(path.split("/")[-1])
                parent = get_node(parent_path)
                parent["children"][idx] = p["node"]

            elif op == "props":
                node = get_node(path)
                node["props"] = p["props"]

            elif op == "add":
                parent_path = "/".join(path.split("/")[:-1])
                parent = get_node(parent_path)
                parent["children"].append(p["node"])

            elif op == "remove":
                parent_path = "/".join(path.split("/")[:-1])
                idx = int(path.split("/")[-1])
                parent = get_node(parent_path)
                parent["children"].pop(idx)

        return tree

    #---------------------------------------------------------------------------
    #  RENDER PIPELINE
    #---------------------------------------------------------------------------
    def render(self, name: str, new_structure: Dict[str, Any]) -> Dict[str, Any]:
        new_tree = self.build_tree(name, new_structure)["tree"]
        old_tree = self.vdom_trees.get(name)

        if not old_tree:
            self.vdom_trees[name] = new_tree
            return {
                "render_id": f"RND-{uuid.uuid4().hex[:10].upper()}",
                "timestamp": time.time(),
                "patches": [],
                "tree": new_tree
            }

        patches = self.diff(old_tree, new_tree)
        updated = self.apply_patches(old_tree, patches)
        self.vdom_trees[name] = updated

        return {
            "render_id": f"RND-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "patches": patches,
            "tree": updated
        }

#===============================================================================
#  END OF FILE — ui_rendering_engine.py
#===============================================================================
