"""Differential test of the Output equations against the XSD over the WHOLE schema.

Usage: python fuzz.py [documents] [mutations per document] [seed]

validate.py only exercises what check.py fills. This script draws random atom
sets that cover every section of the schema and compares, for each of them,
"all 782 equations hold" with "the XSD validators accept the serialised XML":

  1. random_atoms() walks the node tree and builds atoms that are valid by
     construction (random optional nodes, row counts and choice alternatives,
     random valid values). Both verdicts must be positive.
  2. mutate() then damages the atoms at random (flip a presence entry, spoil or
     remove a value, add / duplicate / orphan / re-parent a row). Both verdicts
     must still coincide.

Atoms that are not a tree (a node present under an absent ancestor, a row
without parent) cannot be written as XML at all. prune() therefore reduces the
atoms to what the serialiser actually writes, and the equations are evaluated
on the pruned atoms; how often pruning changes the verdict is reported too.
"""
import copy
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import validate as V         # noqa: E402
import serialize             # noqa: E402
g = V.g

VECS_OF = {}
for _v in g.vectors:
    VECS_OF.setdefault(_v["relation_id"], []).append(_v)
CHOICE_OP = {k["path"]: ("<=" if " <= " in k["formula"] else "=") for k in g.constraints if k["kind"] == "choice"}
PRESENCE_PATH = {v["vector_id"]: v["path"] for v in g.vectors if v["kind"] == "presence"}


# ---------------------------------------------------------------- atoms as growing lists
class Builder:
    """Atoms under construction: one parent index and one entry per vector for every row."""

    def __init__(self):
        self.parent = {r["relation_id"]: [] for r in g.relations}
        self.x = {v["vector_id"]: [] for v in g.vectors if v["kind"] == "value"}
        self.pi = {v["vector_id"]: [] for v in g.vectors if v["kind"] == "presence"}

    def new_row(self, rel, parent_row):
        self.parent[rel].append(parent_row)
        for v in VECS_OF.get(rel, []):
            (self.pi if v["kind"] == "presence" else self.x)[v["vector_id"]].append(0 if v["kind"] == "presence" else None)
        return len(self.parent[rel]) - 1

    def atoms(self):
        n = {rid: len(p) for rid, p in self.parent.items()}
        P = {}
        for r in g.relations:
            rid, q = r["relation_id"], r["parent_relation_id"]
            if q:
                P[rid] = np.zeros((n[q], n[rid]), int)
                P[rid][self.parent[rid], np.arange(n[rid])] = 1
        return {"n": n, "P": P, "x": self.x, "pi": {k: np.array(v, int) for k, v in self.pi.items()}}


def own_presence(node):
    """vector_id of the node's own presence vector, or None if it only inherits its context."""
    ctx = node["context"]
    if ctx != g.ONE and PRESENCE_PATH[ctx[3:]] == node["path"] and not node["child_relation_id"]:
        return ctx[3:]
    return None


# ---------------------------------------------------------------- random valid atoms
def random_value(rng, type_id):
    t = g.type_rows[type_id]
    if type_id in serialize.ENUM:
        return rng.choice(serialize.ENUM[type_id])
    if "minLength" in t or "maxLength" in t:
        lo, hi = int(t.get("minLength", 0)), int(t.get("maxLength", 50))
        return "T" * rng.choice([lo, hi, rng.randint(lo, min(hi, lo + 20))])
    if "minInclusive" in t:
        return rng.choice([0, 1, 0.5, 0.1234, 0.0001, 1.0])
    return {"boolean": rng.choice([True, False]), "integer": rng.choice([0, 1, -7, 10 ** 15]),
            "date": rng.choice(["2024-01-01", "2024-02-29", "2024-12-31Z"]),
            "dateTime": rng.choice(["2025-06-30T12:00:00", "2025-06-30T12:00:00.5Z"])}[t["primitive"]]


def random_atoms(rng, p):
    """Atoms that are valid by construction; every optional node is present with probability p."""
    b = Builder()

    def fill(node, rel, row):
        if node["vector_id"]:
            b.x[node["vector_id"]][row] = random_value(rng, serialize.TYPE_OF[node["vector_id"]])
        kids = serialize.CHILDREN.get(node["node_id"], [])
        pick = None
        if node["kind"] == "choice":
            pick = rng.randrange(len(kids))
            if CHOICE_OP[node["path"]] == "<=" and rng.random() > p:
                pick = -1                                    # a choice that may be empty
        for i, child in enumerate(kids):
            build(child, rel, row, None if pick is None else i == pick)

    def build(node, rel, row, forced):
        child_rel = node["child_relation_id"]
        if child_rel:
            lo, hi = V.REL[child_rel]["min_occurs"], V.REL[child_rel]["max_occurs"]
            k = rng.randint(lo, lo + 2) if rng.random() < p else lo
            k = 0 if forced is False else max(k, 1) if forced else k
            if hi != "unbounded":
                k = min(k, int(hi))
            for _ in range(k):
                fill(node, child_rel, b.new_row(child_rel, row))
            return
        own = own_presence(node)
        if own:
            if not (forced if forced is not None else rng.random() < p):
                return
            b.pi[own][row] = 1
        if node["kind"] in ("attribute", "text"):
            b.x[node["vector_id"]][row] = random_value(rng, serialize.TYPE_OF[node["vector_id"]])
        else:
            fill(node, rel, row)

    top = g.nodes[0]
    fill(top, top["relation_id"], b.new_row(top["relation_id"], None))
    return b.atoms()


# ---------------------------------------------------------------- what the serialiser sees
def prune(a):
    """The atoms restricted to the nodes and rows that serialize() actually writes."""
    b = Builder()

    def fill(node, rel, row, new):
        if node["vector_id"]:
            b.x[node["vector_id"]][new] = a["x"][node["vector_id"]][row]
        for child in serialize.CHILDREN.get(node["node_id"], []):
            walk(child, rel, row, new)

    def walk(node, rel, row, new):
        child_rel = node["child_relation_id"]
        if child_rel:
            for j in np.flatnonzero(a["P"][child_rel][row]):
                fill(node, child_rel, j, b.new_row(child_rel, new))
            return
        ctx = node["context"]
        if ctx != g.ONE:
            if not a["pi"][ctx[3:]][row]:
                return
            b.pi[ctx[3:]][new] = 1
        if node["kind"] in ("attribute", "text"):
            b.x[node["vector_id"]][new] = a["x"][node["vector_id"]][row]
        else:
            fill(node, rel, row, new)

    top = g.nodes[0]
    fill(top, top["relation_id"], 0, b.new_row(top["relation_id"], None))
    return b.atoms()


# ---------------------------------------------------------------- random damage
BAD = [None, "", "ZZZ", "GIR000", "T" * 4001, 1.5, -0.5, 0.12345, "2024-13-45", "true", "1", True, 12]


def mutate(rng, a):
    """Apply one random mutation in place and return its description (None if not applicable)."""
    kind = rng.choice(["flip", "flip", "value", "value", "add", "duplicate", "orphan", "move"])
    if kind == "flip":
        v = rng.choice([v for v in g.vectors if v["kind"] == "presence" and a["n"][v["relation_id"]]])
        i = rng.randrange(a["n"][v["relation_id"]])
        a["pi"][v["vector_id"]][i] ^= 1
        return "flip pi of %s row %d to %d" % (v["path"], i, a["pi"][v["vector_id"]][i])
    if kind == "value":
        v = rng.choice([v for v in g.vectors if v["kind"] == "value" and a["n"][v["relation_id"]]])
        i = rng.randrange(a["n"][v["relation_id"]])
        bad = rng.choice(BAD)
        a["x"][v["vector_id"]][i] = bad
        return "set %s row %d to %r" % (v["path"], i, bad if not isinstance(bad, str) else bad[:12])
    rels = [r for r in g.relations if r["parent_relation_id"] and a["n"][r["parent_relation_id"]]]
    if kind in ("duplicate", "orphan", "move"):
        rels = [r for r in rels if a["n"][r["relation_id"]]]
    if not rels:
        return None
    r = rng.choice(rels)
    rid, q = r["relation_id"], r["parent_relation_id"]
    if kind in ("orphan", "move"):
        j = rng.randrange(a["n"][rid])
        a["P"][rid][:, j] = 0
        if kind == "move":
            a["P"][rid][rng.randrange(a["n"][q]), j] = 1
        return "%s row %d of %s" % (kind, j, r["path"])
    src = rng.randrange(a["n"][rid]) if kind == "duplicate" else None
    col = a["P"][rid][:, [src]].copy() if kind == "duplicate" else np.zeros((a["n"][q], 1), int)
    if kind == "add":
        col[rng.randrange(a["n"][q])] = 1
    a["P"][rid] = np.hstack([a["P"][rid], col])
    a["n"][rid] += 1
    for v in VECS_OF.get(rid, []):
        if v["kind"] == "presence":
            a["pi"][v["vector_id"]] = np.append(a["pi"][v["vector_id"]], a["pi"][v["vector_id"]][src] if kind == "duplicate" else 0)
        else:
            a["x"][v["vector_id"]] = a["x"][v["vector_id"]] + [a["x"][v["vector_id"]][src] if kind == "duplicate" else None]
    for child in g.relations:                                # children keep their shape: one more parent row
        if child["parent_relation_id"] == rid:
            cid = child["relation_id"]
            a["P"][cid] = np.vstack([a["P"][cid], np.zeros((1, a["n"][cid]), int)])
    return "%s a row of %s" % (kind, r["path"])


# ---------------------------------------------------------------- comparison
def verdicts(a):
    """(failed equations on the pruned atoms, lxml errors, xmlschema errors, equations hold on the raw atoms)."""
    text = serialize.to_string(serialize.serialize(a["n"], a["P"], a["x"], a["pi"]))
    pruned = prune(a)
    assert serialize.to_string(serialize.serialize(pruned["n"], pruned["P"], pruned["x"], pruned["pi"])) == text
    assert not V.shape_errors(pruned)
    e1, e2 = V.xsd_errors(text)
    raw_ok = not V.shape_errors(a) and not V.failed_equations(a)
    return V.failed_equations(pruned), e2, e1, raw_ok


def main(docs=40, muts=40, seed=1):
    rng = random.Random(seed)
    used_vec, used_rel, witnessed, disagreements = set(), set(), set(), []
    stats = {"valid docs": 0, "valid docs accepted": 0, "mutants": 0, "mutants rejected by both": 0,
             "mutants accepted by both": 0, "mutants: raw atoms fail but pruned atoms hold (not a tree)": 0,
             "mutants: raw atoms hold but validators reject": 0, "validators disagree with each other": 0}
    for d in range(docs):
        base = random_atoms(rng, rng.choice([0.15, 0.5, 0.9]))
        failed, lx, xs, raw_ok = verdicts(base)
        used_vec |= {k for k, v in base["pi"].items() if np.any(v)} | {k for k, v in base["x"].items() if any(e is not None for e in v)}
        used_rel |= {k for k, v in base["n"].items() if v}
        stats["valid docs"] += 1
        stats["valid docs accepted"] += not failed and not lx and not xs and raw_ok
        if failed or lx or xs or not raw_ok:
            disagreements.append(("valid-by-construction document %d" % d, [k["formula"] + " | " + k["path"] for k in failed], lx[:3] + xs[:3]))
            continue
        for _ in range(muts):
            a = copy.deepcopy(base)
            what = mutate(rng, a)
            if what is None:
                continue
            failed, lx, xs, raw_ok = verdicts(a)
            stats["mutants"] += 1
            stats["validators disagree with each other"] += bool(lx) != bool(xs)
            eq_ok, xsd_ok = not failed, not lx and not xs
            if eq_ok == xsd_ok:
                stats["mutants accepted by both" if eq_ok else "mutants rejected by both"] += 1
                witnessed |= {k["constraint_id"] for k in failed}
            else:
                disagreements.append((what, [k["formula"] + " | " + k["path"] for k in failed], lx[:3] + xs[:3]))
            stats["mutants: raw atoms fail but pruned atoms hold (not a tree)"] += eq_ok and not raw_ok
            stats["mutants: raw atoms hold but validators reject"] += raw_ok and not xsd_ok
    for k, v in stats.items():
        print("%-60s %d" % (k, v))
    print("%-60s %d of %d" % ("vectors present in at least one valid document", len(used_vec), len(g.vectors)))
    print("%-60s %d of %d" % ("relations with rows in at least one valid document", len(used_rel), len(g.relations)))
    print("%-60s %d of %d" % ("equations seen failing together with an XSD rejection", len(witnessed), len(g.constraints)))
    print("%-60s %d" % ("DISAGREEMENTS between equations and validators", len(disagreements)))
    for what, eqs, errs in disagreements[:40]:
        print("  mutation:", what)
        for e in eqs[:5]:
            print("     equation fails:", e)
        for e in errs:
            print("     validator:", e[:300])
    return disagreements


if __name__ == "__main__":
    main(*map(int, sys.argv[1:]))
