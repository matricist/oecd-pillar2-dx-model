"""Convert the GloBE XSD into relations, atomic vectors and constraint equations.

Usage: python generate.py            (run from XML-Model/Vector-Model)
Reads ../globe-xsd/*.xsd and writes Equations.md and Types.md next to this
script. See Model.md.
"""
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
XSD_DIR = os.path.join(HERE, "..", "globe-xsd")
FILES = ["GLOBEXML_v1.0.xsd", "isoglobetypes_v1.1.xsd", "oecdglobetypes_v5.0.xsd"]
ROOT = "GLOBE_OECD"
XS = "{http://www.w3.org/2001/XMLSchema}"
XSD_NS = "http://www.w3.org/2001/XMLSchema"
PREFIX = {"urn:oecd:ties:globe:v2": "globe", "urn:oecd:ties:isoglobetypes:v1": "iso",
          "urn:oecd:ties:globestf:v5": "stf", XSD_NS: "xsd"}
FACETS = ["minLength", "maxLength", "length", "pattern", "minInclusive", "maxInclusive",
          "minExclusive", "maxExclusive", "totalDigits", "fractionDigits"]


def tag(e):
    return e.tag.replace(XS, "")


# ---------------------------------------------------------------- schema loading
types = {}      # (namespace, name) -> (definition element, namespace map)
elements = {}   # (namespace, name) -> (declaration element, namespace map)
for fn in FILES:
    path = os.path.join(XSD_DIR, fn)
    nsmap = {}
    for _, (p, uri) in ET.iterparse(path, events=["start-ns"]):
        nsmap[p] = uri
    root = ET.parse(path).getroot()
    tns = root.attrib["targetNamespace"]
    for e in root:
        if tag(e) in ("simpleType", "complexType"):
            types[(tns, e.attrib["name"])] = (e, nsmap)
        elif tag(e) == "element":
            elements[(tns, e.attrib["name"])] = (e, nsmap)


def qname(q, nsmap):
    p, _, n = q.rpartition(":")
    return (nsmap[p], n)


def label(key):
    return "%s:%s" % (PREFIX[key[0]], key[1])


# ---------------------------------------------------------------- simple types
type_rows = {}   # type_id -> row
enum_rows = []


def simple_type(key=None, anon=None, nsmap=None, anon_id=None):
    """Register a simple type and return its type_id."""
    if key is not None and key[0] == XSD_NS:
        tid = label(key)
        type_rows.setdefault(tid, {"type_id": tid, "primitive": key[1]})
        return tid
    tid = label(key) if key is not None else anon_id
    if tid in type_rows:
        return tid
    node, nsmap = (types[key] if key is not None else (anon, nsmap))
    r = node.find(XS + "restriction")
    assert r is not None, "only restrictions are supported: %s" % tid
    base = simple_type(qname(r.attrib["base"], nsmap))
    row = dict(type_rows[base])
    row.update({"type_id": tid, "base": base})
    enums = r.findall(XS + "enumeration")
    if enums:
        row["enumerations"] = len(enums)
        for e in enums:
            doc = e.find(XS + "annotation/" + XS + "documentation")
            enum_rows.append({"type_id": tid, "value": e.attrib["value"],
                              "annotation": " ".join((doc.text or "").split()) if doc is not None else ""})
    for f in FACETS:
        fe = r.find(XS + f)
        if fe is not None:
            row[f] = fe.attrib["value"]
    type_rows[tid] = row
    return tid


def is_simple(key):
    return key[0] == XSD_NS or tag(types[key][0]) == "simpleType"


# ---------------------------------------------------------------- model building
relations, vectors, constraints = [], [], []
ONE = "1"


def new_relation(path, parent, lo, hi):
    rid = "r%03d" % (len(relations) + 1)
    relations.append({"relation_id": rid, "path": path, "parent_relation_id": parent or "",
                      "min_occurs": lo, "max_occurs": hi})
    return rid


def new_vector(rel, path, kind, node, type_id="", presence=""):
    vid = "v%04d" % (len(vectors) + 1)
    vectors.append({"vector_id": vid, "relation_id": rel, "path": path, "kind": kind,
                    "node": node, "type_id": type_id, "presence": presence})
    return vid


def constrain(kind, rel, formula, path):
    constraints.append({"constraint_id": "k%04d" % (len(constraints) + 1), "kind": kind,
                        "relation_id": rel, "formula": formula, "path": path})


def scaled(k, ctx):
    """k * ctx, written without redundant factors."""
    if ctx == ONE:
        return str(k)
    return ctx if str(k) == "1" else "%s * %s" % (k, ctx)


def presence(rel, path, node, ctx):
    """Create a presence vector nested in ctx and return its expression."""
    pi = "pi_" + new_vector(rel, path, "presence", node)
    if ctx != ONE:
        constrain("nesting", rel, "%s <= %s" % (pi, ctx), path)
    return pi


def value(rel, path, node, type_id, ctx):
    x = "x_" + new_vector(rel, path, "value", node, type_id, ctx)
    constrain("type", rel, "tau[%s](%s) >= %s" % (type_id, x, ctx), path)


def content(type_el, nsmap, rel, path, ctx, stack):
    """Expand the attributes and content model of a complex type."""
    sc = type_el.find(XS + "simpleContent")
    cc = type_el.find(XS + "complexContent")
    holder = type_el
    if sc is not None:
        ext = sc.find(XS + "extension")
        value(rel, path + "/#text", "text", simple_type(qname(ext.attrib["base"], nsmap)), ctx)
        holder = ext
    elif cc is not None:
        ext = cc.find(XS + "extension")
        bkey = qname(ext.attrib["base"], nsmap)
        assert bkey not in stack, "recursive type"
        b_el, b_ns = types[bkey]
        content(b_el, b_ns, rel, path, ctx, stack + [bkey])
        holder = ext
    for a in holder.findall(XS + "attribute"):
        apath = "%s/@%s" % (path, a.attrib["name"])
        actx = ctx if a.attrib.get("use") == "required" else presence(rel, apath, "attribute", ctx)
        value(rel, apath, "attribute", simple_type(qname(a.attrib["type"], nsmap)), actx)
    counter = {}
    for child in holder:
        if tag(child) in ("sequence", "choice", "element"):
            particle(child, nsmap, rel, path, ctx, False, stack, counter)


def particle(p, nsmap, rel, path, ctx, in_choice, stack, counter):
    """Expand one particle; return the expression of its presence in a row of rel."""
    lo = int(p.attrib.get("minOccurs", "1"))
    hi = p.attrib.get("maxOccurs", "1")
    kind = tag(p)
    if kind == "element":
        epath = "%s/%s" % (path, p.attrib["name"])
        if hi != "1":                                   # repeated: a child relation
            child = new_relation(epath, rel, lo, hi)
            count = "P_%s 1" % child
            delta = "(%s > 0)" % count
            constrain("parent", child, "P_%s^T 1 = 1" % child, epath)
            bound = delta if in_choice else ctx
            if lo > 0:
                constrain("occurrence", rel, "%s >= %s" % (count, scaled(lo, bound)), epath)
            if hi != "unbounded":
                constrain("occurrence", rel, "%s <= %s" % (count, scaled(hi, bound)), epath)
            elif bound != ONE and not in_choice:
                constrain("occurrence", rel, "(1 - %s) . (%s) = 0" % (bound, count), epath)
            element_body(p, nsmap, child, epath, ONE, stack)
            return delta
        ectx = presence(rel, epath, "element", ctx) if (lo == 0 or in_choice) else ctx
        element_body(p, nsmap, rel, epath, ectx, stack)
        return ectx
    assert hi == "1", "repeated %s group at %s" % (kind, path)
    counter[kind] = counter.get(kind, 0) + 1
    gpath = "%s/(%s%d)" % (path, kind, counter[kind])
    gctx = presence(rel, gpath, kind, ctx) if (lo == 0 or in_choice) else ctx
    sub = {}
    if kind == "sequence":
        for child in p:
            if tag(child) in ("sequence", "choice", "element"):
                particle(child, nsmap, rel, gpath if (lo == 0 or in_choice) else path, gctx, False, stack,
                         sub if (lo == 0 or in_choice) else counter)
        return gctx
    alts, may_be_empty = [], False
    for child in p:
        if tag(child) in ("sequence", "choice", "element"):
            may_be_empty |= child.attrib.get("minOccurs", "1") == "0"
            alts.append(particle(child, nsmap, rel, gpath, gctx, True, stack, sub))
    constrain("choice", rel, "%s %s %s" % (" + ".join(alts), "<=" if may_be_empty else "=", gctx), gpath)
    return gctx


def element_body(e, nsmap, rel, path, ctx, stack):
    if "type" in e.attrib:
        key = qname(e.attrib["type"], nsmap)
        if is_simple(key):
            value(rel, path, "element", simple_type(key), ctx)
            return
        assert key not in stack, "recursive type at %s" % path
        t_el, t_ns = types[key]
        content(t_el, t_ns, rel, path, ctx, stack + [key])
        return
    st = e.find(XS + "simpleType")
    if st is not None:
        value(rel, path, "element", simple_type(anon=st, nsmap=nsmap, anon_id="anon:" + path), ctx)
        return
    content(e.find(XS + "complexType"), nsmap, rel, path, ctx, stack)


root_key = next(k for k in elements if k[1] == ROOT)
root_el, root_ns = elements[root_key]
root_rel = new_relation(ROOT, None, 1, "1")
constrain("root", root_rel, "n_%s = 1" % root_rel, ROOT)
element_body(root_el, root_ns, root_rel, ROOT, ONE, [])


used = {v["type_id"] for v in vectors if v["type_id"]}


# ---------------------------------------------------------------- Equations.md
def num(ident):
    return str(int(ident[1:]))


def latex(formula):
    """Render a constraint formula as LaTeX."""
    f = re.sub(r"tau\[[^\]]*\]\(", r"\\tau(", formula)
    f = re.sub(r"P_(r\d+)\^T 1", lambda m: r"\mathbf{P}_{%s}^{T}\times\mathbf{1}" % num(m.group(1)), f)
    f = re.sub(r"P_(r\d+) 1", lambda m: r"\mathbf{P}_{%s}\times\mathbf{1}" % num(m.group(1)), f)
    f = re.sub(r"pi_(v\d+)", lambda m: r"\boldsymbol{\pi}_{%s}" % num(m.group(1)), f)
    f = re.sub(r"x_(v\d+)", lambda m: r"\mathbf{x}_{%s}" % num(m.group(1)), f)
    if f.startswith("n_r"):
        return re.sub(r"n_(r\d+)", lambda m: "n_{%s}" % num(m.group(1)), f)
    out = []
    tokens = f.split(" ")
    for i, t in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        if t == "(1":
            t = r"(\mathbf{1}"
        elif t.isdigit() and nxt != "*":
            t = {"0": r"\mathbf{0}", "1": r"\mathbf{1}"}.get(t, t + r"\cdot\mathbf{1}")
        out.append({">=": r"\ge", "<=": r"\le", ".": r"\odot", "*": r"\cdot"}.get(t, t))
    return " ".join(out)


def cell(text):
    return text.replace("|", r"\|").replace("_", r"\_")


def write_equations():
    by_rel_v, by_rel_c = {}, {}
    for v in vectors:
        by_rel_v.setdefault(v["relation_id"], []).append(v)
    for c in constraints:
        by_rel_c.setdefault(c["relation_id"], []).append(c)
    type_eq = {c["path"]: c["formula"] for c in constraints if c["kind"] == "type"}
    path_of = {r["relation_id"]: r["path"] for r in relations}
    L = ["# Equations", "",
         "Every equation of the [Output Model](Model.md), by relation. Generated by `generate.py`; do not edit.", "",
         "Subscripts are relation and vector numbers: $\\mathbf{P}_{6}$ is the parent matrix of `r006`, and "
         "$\\mathbf{x}_{41}$ and $\\boldsymbol{\\pi}_{40}$ are vectors 41 and 40. $\\tau$ is the predicate of the "
         "[type](Types.md) shown in the same row. Nodes are given relative to the relation.", ""]
    for r in relations:
        rid, rpath = r["relation_id"], r["path"]
        L += ["# %s · %s" % (rid, rpath.rsplit("/", 1)[-1]), "", "`%s`" % rpath, ""]
        if r["parent_relation_id"]:
            hi = "∞" if r["max_occurs"] == "unbounded" else r["max_occurs"]
            L += ["Parent `%s`, occurs %s to %s." % (r["parent_relation_id"], r["min_occurs"], hi), ""]
        vs = by_rel_v.get(rid, [])
        if vs:
            L += ["| Vector | Node | Type | Equation |", "| --- | --- | --- | --- |"]
            for v in vs:
                node = cell(v["path"][len(rpath):].lstrip("/") or ".")
                if v["kind"] == "presence":
                    L.append("| $\\boldsymbol{\\pi}_{%s}$ | %s | presence | |" % (num(v["vector_id"]), node))
                else:
                    L.append("| $\\mathbf{x}_{%s}$ | %s | %s | $%s$ |" % (
                        num(v["vector_id"]), node, cell(v["type_id"]), latex(type_eq[v["path"]])))
            L.append("")
        cs = [c for c in by_rel_c.get(rid, []) if c["kind"] != "type"]
        if cs:
            L += ["| Kind | Equation | Node |", "| --- | --- | --- |"]
            for c in cs:
                base = rpath if c["path"].startswith(rpath) else ""
                node = cell(c["path"][len(base):].lstrip("/") or ".")
                L.append("| %s | $%s$ | %s |" % (c["kind"].capitalize(), latex(c["formula"]), node))
            L.append("")
    with open(os.path.join(HERE, "Equations.md"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(L))



def write_types():
    L = ["# Types", "",
         "The value types of the [Output Model](Model.md) and their predicates $\\tau_t$. Generated by `generate.py`; do not edit.", "",
         "| Type | Primitive | $\\tau_t(x)$ |", "| --- | --- | --- |"]
    enums = {}
    for e in enum_rows:
        enums.setdefault(e["type_id"], []).append(e)
    for tid in sorted(used):
        t = type_rows[tid]
        if t.get("enumerations"):
            pred = "$1\\le x\\le %s$" % t["enumerations"]
        elif "minLength" in t or "maxLength" in t:
            pred = "$%s\\le\\operatorname{len}(x)\\le %s$" % (t.get("minLength", "0"), t.get("maxLength", "\\infty"))
        elif "minInclusive" in t:
            pred = "$%s\\le x\\le %s$ and $10^{%s}x\\in\\mathbb{Z}$" % (t["minInclusive"], t["maxInclusive"], t["fractionDigits"])
        else:
            pred = "$x$ is a valid %s" % t["primitive"]
        L.append("| %s | %s | %s |" % (cell(tid), t["primitive"], pred))
    L.append("")
    for tid in sorted(enums):
        L += ["# %s" % cell(tid), "", "| $x$ | Value | Annotation |", "| --- | --- | --- |"]
        for i, e in enumerate(enums[tid], 1):
            L.append("| %d | %s | %s |" % (i, cell(e["value"]), cell(e["annotation"])))
        L.append("")
    with open(os.path.join(HERE, "Types.md"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(L))


write_equations()
write_types()

if __name__ == "__main__":
    from collections import Counter
    print("relations", len(relations))
    print("vectors", dict(Counter(v["kind"] for v in vectors)))
    print("value nodes", dict(Counter(v["node"] for v in vectors if v["kind"] == "value")))
    print("types", len(used), dict(Counter(type_rows[t]["primitive"] for t in used)))
    print("constraints", dict(Counter(c["kind"] for c in constraints)))
