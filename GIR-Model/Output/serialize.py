"""Serialise Output atoms (n, P, x, pi) into a GloBE Information Return XML document.

The serialiser is generic: it walks `generate.nodes`, the element tree that
generate.py derives from the XSD, and knows nothing about individual elements.

    import serialize
    root = serialize.serialize(n, P, x, pi)      # xml.etree.ElementTree.Element
    text = serialize.to_string(root)

Atoms are keyed as in Link/check.py:
    n[relation_id]   number of rows
    P[relation_id]   parent matrix, shape (n_parent, n_r)
    x[vector_id]     list of n_r values (None where the node is absent)
    pi[vector_id]    0/1 vector of length n_r

Rules (Output/Model.md, "Not Expressed"):
    - elements are written in schema order, the rows of a relation in index order;
    - a repeated element is written once per row j with P[i, j] = 1, i being the
      row of the enclosing relation;
    - any other node is written iff its context is 1 in the row: the presence
      vector of the nearest enclosing optional node, or always if there is none;
    - elements are namespace-qualified with the target namespace of the schema
      that declares them (elementFormDefault="qualified"), attributes are
      unqualified (attributeFormDefault="unqualified").

Atom sets that are not a tree cannot be written faithfully and are NOT repaired:
a node present under an absent ancestor is dropped, a row without a parent is
dropped, a row with two parents is written twice. The nesting and parent
equations are what exclude those cases.
"""
import contextlib
import io
import os
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
with contextlib.redirect_stdout(io.StringIO()):
    import generate as g

for _uri, _prefix in g.PREFIX.items():
    if _prefix != "xsd":
        ET.register_namespace(_prefix, _uri)

CHILDREN = {}                                   # node_id -> child nodes, in schema order
for _nd in g.nodes:
    CHILDREN.setdefault(_nd["parent_node_id"], []).append(_nd)
TYPE_OF = {v["vector_id"]: v["type_id"] for v in g.vectors if v["kind"] == "value"}
ENUM = {}                                       # type_id -> values, in the order of Types.md
for _e in g.enum_rows:
    ENUM.setdefault(_e["type_id"], []).append(_e["value"])


def lexical(value, type_id):
    """The XML text of one value. None (no value) is written as the empty string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if type(value).__name__ in ("bool", "bool_"):
        return "true" if value else "false"
    if type_id in ENUM and float(value) == int(value):
        # Model.md encodes an enumeration value by its position in Types.md (1-based)
        k = int(value)
        return ENUM[type_id][k - 1] if 1 <= k <= len(ENUM[type_id]) else str(k)
    if float(value) == int(value) and "float" not in type(value).__name__:
        return str(int(value))
    return format(Decimal(repr(float(value))), "f")


def serialize(n, P, x, pi):
    """Build the document for the given atoms and return its root element."""

    def present(node, row):
        ctx = node["context"]
        return True if ctx == g.ONE else bool(pi[ctx[3:]][row])

    def fill(el, node, rel, row):
        """Write the value and the children of an element whose content lives in row `row` of `rel`."""
        if node["vector_id"]:
            el.text = lexical(x[node["vector_id"]][row], TYPE_OF[node["vector_id"]])
        for child in CHILDREN.get(node["node_id"], []):
            emit(el, child, row)

    def emit(parent, node, row):
        kind = node["kind"]
        if kind == "element" and node["child_relation_id"]:
            child_rel = node["child_relation_id"]
            for j in range(n[child_rel]):
                if P[child_rel][row, j]:
                    fill(ET.SubElement(parent, "{%s}%s" % (node["namespace"], node["name"])), node, child_rel, j)
        elif not present(node, row):
            return
        elif kind == "element":
            fill(ET.SubElement(parent, "{%s}%s" % (node["namespace"], node["name"])), node, node["relation_id"], row)
        elif kind == "attribute":
            parent.set(node["name"], lexical(x[node["vector_id"]][row], TYPE_OF[node["vector_id"]]))
        elif kind == "text":
            parent.text = lexical(x[node["vector_id"]][row], TYPE_OF[node["vector_id"]])
        else:                                   # sequence or choice: no markup of its own
            for child in CHILDREN.get(node["node_id"], []):
                emit(parent, child, row)

    top = g.nodes[0]
    assert n[top["relation_id"]] == 1, "the root relation must have exactly one row"
    root = ET.Element("{%s}%s" % (top["namespace"], top["name"]))
    fill(root, top, top["relation_id"], 0)
    return root


def to_string(root):
    """Pretty-printed XML text with an XML declaration."""
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
