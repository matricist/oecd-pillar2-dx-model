"""Serialise the atoms of check.py into a full GIR document and validate it against the XSD.

Usage: python validate.py     (run from GIR-Model/Link; needs numpy, xmlschema, lxml)

check.py fills GeneralSection/CorporateStructure and the frame of
JurisdictionSection. This script
  1. takes those atoms unchanged,
  2. adds DUMMY TEST VALUES for every other required node (MessageSpec, FilingInfo,
     RecJurCode, DocSpec) and leaves every optional node absent,
  3. serialises with Output/serialize.py,
  4. validates with two independent XSD validators (xmlschema, lxml/libxml2),
  5. evaluates all 782 Output equations on the same atoms,
and compares the two verdicts for the base case and a few negative cases.
"""
import copy
import datetime
import os
import re
import sys
from decimal import Decimal

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Output"))
sys.path.insert(0, HERE)

import check as c            # noqa: E402  builds the CorporateStructure atoms
import serialize             # noqa: E402
g = c.g

XSD = os.path.join(HERE, "..", "globe-xsd", "GLOBEXML_v1.0.xsd")
ROOT = "GLOBE_OECD"
BODY = ROOT + "/GLOBEBody"
REL = {r["relation_id"]: r for r in g.relations}
VEC = {v["vector_id"]: v for v in g.vectors}

# ================================================================ dummy test values
# Every required value node outside CorporateStructure. All values are test data.
DUMMY = {
    ROOT + "/MessageSpec/TransmittingCountry": "US",
    ROOT + "/MessageSpec/ReceivingCountry": "US",
    ROOT + "/MessageSpec/MessageType": "GIR",
    ROOT + "/MessageSpec/MessageRefId": "DUMMY-TEST-MessageRefId",
    ROOT + "/MessageSpec/MessageTypeIndic": "GIR101",
    ROOT + "/MessageSpec/ReportingPeriod": "2024-12-31",
    ROOT + "/MessageSpec/Timestamp": "2025-06-30T00:00:00",
    BODY + "/FilingInfo/FilingCE/ResCountryCode": "US",
    BODY + "/FilingInfo/FilingCE/Name": "DUMMY TEST Filing CE",
    BODY + "/FilingInfo/FilingCE/TIN/#text": "DUMMY-TEST-TIN",
    BODY + "/FilingInfo/FilingCE/Role": "GIR401",
    BODY + "/FilingInfo/AccountingInfo/CFSofUPE": "GIR501",
    BODY + "/FilingInfo/AccountingInfo/FAS": "DUMMY TEST FAS",
    BODY + "/FilingInfo/AccountingInfo/Currency": "USD",
    BODY + "/FilingInfo/Period/Start": "2024-01-01",
    BODY + "/FilingInfo/Period/End": "2024-12-31",
    BODY + "/FilingInfo/NameMNE": "DUMMY TEST MNE Group",
    BODY + "/FilingInfo/DocSpec/DocTypeIndic": "OECD1",
    BODY + "/FilingInfo/DocSpec/DocRefId": "DUMMY-TEST-DocRefId-FilingInfo",
    BODY + "/GeneralSection/DocSpec/DocTypeIndic": "OECD1",
    BODY + "/GeneralSection/DocSpec/DocRefId": "DUMMY-TEST-DocRefId-GeneralSection",
}
# Required repeated element outside CorporateStructure: one row.
DUMMY_ROWS = {BODY + "/GeneralSection/RecJurCode": ["US"]}


def base_atoms():
    """The atoms of check.py (deep copy) plus the dummies; everything else absent."""
    a = {"n": dict(c.n), "P": copy.deepcopy(c.P), "x": copy.deepcopy(c.x), "pi": copy.deepcopy(c.pi)}
    for path, value in DUMMY.items():
        a["x"][c.vec_id[(path, "value")]] = [value]
    for path, values in DUMMY_ROWS.items():
        rid = c.rel_id[path]
        a["n"][rid] = len(values)
        a["P"][rid] = np.ones((1, len(values)), int)
        a["x"][c.vec_id[(path, "value")]] = list(values)
    return fill_absent(a)


def fill_absent(a):
    """Give every atom that is still unset its 'absent' value: no rows, pi = 0, x = None."""
    for r in g.relations:                       # parents come before children
        rid = r["relation_id"]
        if rid not in a["n"]:
            a["n"][rid] = 0
            a["P"][rid] = np.zeros((a["n"][r["parent_relation_id"]], 0), int)
    for v in g.vectors:
        k = a["n"][v["relation_id"]]
        if v["kind"] == "presence":
            a["pi"].setdefault(v["vector_id"], np.zeros(k, int))
        else:
            a["x"].setdefault(v["vector_id"], [None] * k)
    return a


# ================================================================ equations
def tau_lexical(type_id, values):
    """tau_t evaluated on the text that would be written for each value.

    check.tau is only safe for values of the expected Python type (it raises on a
    str where a number is expected) and accepts any str as a date or dateTime.
    This version implements the predicates of Types.md on the lexical form, so
    that it is defined for every value: enumeration membership, length bounds,
    the percentage range and digits, and the XSD lexical forms of the built-ins.
    """
    t = g.type_rows[type_id]
    tz = r"(Z|[+-]\d\d:\d\d)?"

    def ok(v):
        if v is None:
            return False
        s = serialize.lexical(v, type_id)
        if type_id in serialize.ENUM:
            return s in serialize.ENUM[type_id]
        if t["primitive"] == "string":
            return int(t.get("minLength", 0)) <= len(s) <= int(t.get("maxLength", 10 ** 9))
        s = s.strip()
        try:
            if t["primitive"] == "decimal":
                if not re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)", s):
                    return False
                d = Decimal(s)
                digits = max(0, -d.normalize().as_tuple().exponent)
                return Decimal(t.get("minInclusive", "-Infinity")) <= d <= Decimal(t.get("maxInclusive", "Infinity")) \
                    and digits <= int(t.get("fractionDigits", 10 ** 9))
            if t["primitive"] == "boolean":
                return s in ("true", "false", "1", "0")
            if t["primitive"] == "integer":
                return bool(re.fullmatch(r"[+-]?\d+", s))
            if t["primitive"] == "date":
                m = re.fullmatch(r"(\d{4})-(\d\d)-(\d\d)" + tz, s)
                datetime.date(*map(int, m.groups()[:3]))
                return True
            if t["primitive"] == "dateTime":
                m = re.fullmatch(r"(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(\.\d+)?" + tz, s)
                datetime.datetime(*map(int, m.groups()[:6]))
                return True
        except (AttributeError, ValueError):
            return False
        raise NotImplementedError(t["primitive"])

    return np.array([ok(v) for v in values], int)


def tau_check(type_id, values):
    """check.tau, entry by entry; -1 where it raises."""
    out = []
    for v in values:
        try:
            out.append(int(c.tau(type_id, [v])[0]))
        except TypeError:
            out.append(-1)
    return np.array(out, int)


def shape_errors(a):
    """Atom typing of Model.md (not counted among the 782 equations): shapes and 0/1 entries."""
    out = []
    for r in g.relations:
        rid, q = r["relation_id"], r["parent_relation_id"]
        if q and np.shape(a["P"][rid]) != (a["n"][q], a["n"][rid]):
            out.append("P_%s has shape %s, expected %s" % (rid, np.shape(a["P"][rid]), (a["n"][q], a["n"][rid])))
        elif q and not np.isin(a["P"][rid], (0, 1)).all():
            out.append("P_%s is not 0/1" % rid)
    for v in g.vectors:
        vec = a["pi" if v["kind"] == "presence" else "x"][v["vector_id"]]
        if len(vec) != a["n"][v["relation_id"]]:
            out.append("%s has length %d, expected %d" % (v["vector_id"], len(vec), a["n"][v["relation_id"]]))
        elif v["kind"] == "presence" and not np.isin(vec, (0, 1)).all():
            out.append("pi_%s is not 0/1" % v["vector_id"])
    return out


def failed_equations(a, strict=True):
    """Evaluate all Output equations; return the constraints that do not hold.

    strict=True uses tau_lexical, strict=False the tau of check.py.
    """
    env = {"np": np, "tau": tau_lexical if strict else tau_check, "x": a["x"], "P": a["P"], "pi": a["pi"]}
    failed = []
    for k in g.constraints:
        if k["kind"] == "root":
            holds = a["n"][k["relation_id"]] == 1
        else:
            holds = bool(eval(c.python(k["formula"]), env))
        if not holds:
            failed.append(k)
    return failed


# ================================================================ XSD validation
_schemas = {}


def xsd_errors(xml_text):
    """Validation errors from xmlschema and from lxml (libxml2), as two lists of strings."""
    import xmlschema
    from lxml import etree
    if not _schemas:
        _schemas["xmlschema"] = xmlschema.XMLSchema(XSD)
        _schemas["lxml"] = etree.XMLSchema(etree.parse(XSD))
    e1 = ["%s: %s" % (strip_ns(e.path or ""), " ".join(strip_ns(e.reason or "").split()))
          for e in _schemas["xmlschema"].iter_errors(xml_text)]
    doc = etree.fromstring(xml_text.encode("utf-8"))
    _schemas["lxml"].validate(doc)
    e2 = ["line %d: %s" % (e.line, strip_ns(e.message)) for e in _schemas["lxml"].error_log]
    return e1, e2


def strip_ns(s):
    for uri, prefix in g.PREFIX.items():
        s = s.replace("{%s}" % uri, prefix + ":")
    return s


# ================================================================ variants of the atoms
CS = c.CS


def columns_of(a, rid, parent_row):
    return np.flatnonzero(a["P"][rid][parent_row])


def add_row(a, path, parent_row, values):
    """Append one row to the relation at `path` under `parent_row`; values: {vector path suffix: (kind, value)}."""
    rid = c.rel_id[path]
    col = np.zeros((a["P"][rid].shape[0], 1), int)
    col[parent_row] = 1
    a["P"][rid] = np.hstack([a["P"][rid], col])
    a["n"][rid] += 1
    for v in g.vectors:
        if v["relation_id"] == rid:
            if v["kind"] == "presence":
                a["pi"][v["vector_id"]] = np.append(a["pi"][v["vector_id"]], values.get((v["path"], "presence"), 0))
            else:
                a["x"][v["vector_id"]] = list(a["x"][v["vector_id"]]) + [values.get((v["path"], "value"))]


def drop_rows(a, path, cols):
    """Remove rows `cols` from the relation at `path` (it must have no child relations)."""
    rid = c.rel_id[path]
    assert not any(r["parent_relation_id"] == rid for r in g.relations)
    keep = np.setdiff1d(np.arange(a["n"][rid]), cols)
    a["P"][rid] = a["P"][rid][:, keep]
    a["n"][rid] = len(keep)
    for v in g.vectors:
        if v["relation_id"] == rid:
            d = a["pi" if v["kind"] == "presence" else "x"]
            d[v["vector_id"]] = np.asarray(d[v["vector_id"]])[keep] if v["kind"] == "presence" else [d[v["vector_id"]][j] for j in keep]


def ce_row(name):
    """Row of Entity `name` in the CE relation."""
    return int(np.flatnonzero(c.S_C @ c.vec(name))[0])


def neg_both_upe():
    """The UPE row is both ExcludedUPE and OtherUPE; ExcludedUPE is filled completely."""
    a = base_atoms()
    ex, ot = CS + "UPE/(choice1)/ExcludedUPE", CS + "UPE/(choice1)/OtherUPE"
    a["pi"][c.vec_id[(ex, "presence")]] = np.array([1])
    a["x"][c.vec_id[(ex + "/ExcludedUPEStatus", "value")]] = ["GIR601"]
    a["x"][c.vec_id[(ex + "/ID/Name", "value")]] = list(a["x"][c.vec_id[(ot + "/ID/Name", "value")]])
    for child in ("ResCountryCode", "TIN", "Rules", "GlobeStatus"):        # copy the ID block of OtherUPE
        src, dst = c.rel_id[ot + "/ID/" + child], c.rel_id[ex + "/ID/" + child]
        a["n"][dst], a["P"][dst] = a["n"][src], a["P"][src].copy()
        for v in g.vectors:
            if v["relation_id"] == src:
                d = a["pi" if v["kind"] == "presence" else "x"]
                d[c.vec_id[(v["path"].replace(ot, ex), v["kind"])]] = copy.deepcopy(d[v["vector_id"]])
    return a


def neg_no_tin(name="A"):
    """All TINs of one CE dropped."""
    a = base_atoms()
    drop_rows(a, CS + "CE/ID/TIN", columns_of(a, c.rel_id[CS + "CE/ID/TIN"], ce_row(name)))
    return a


def neg_bad_enum():
    """An invalid enumeration value in the first CE/ID/GlobeStatus row."""
    a = base_atoms()
    a["x"][c.vec_id[(CS + "CE/ID/GlobeStatus", "value")]][0] = "GIR399"
    return a


def neg_bad_percentage():
    """An ownership percentage with five decimals."""
    a = base_atoms()
    a["x"][c.vec_id[(CS + "CE/Ownership/OwnershipPercentage", "value")]][0] = 0.12345
    return a


def neg_bad_date():
    """A string that is not a date. check.tau accepts it; tau_lexical does not."""
    a = base_atoms()
    a["x"][c.vec_id[(BODY + "/FilingInfo/Period/Start", "value")]] = ["2024-13-45"]
    return a


def neg_no_recjur():
    """No RecJurCode under GeneralSection (required, outside CorporateStructure)."""
    a = base_atoms()
    drop_rows(a, BODY + "/GeneralSection/RecJurCode", [0])
    return a


CASES = [("base: check.py atoms + dummies", base_atoms),
         ("negative: UPE is both ExcludedUPE and OtherUPE", neg_both_upe),
         ("negative: CE 'A' has no TIN", neg_no_tin),
         ("negative: invalid GlobeStatus code", neg_bad_enum),
         ("negative: OwnershipPercentage 0.12345", neg_bad_percentage),
         ("negative: Period/Start = '2024-13-45'", neg_bad_date),
         ("negative: no RecJurCode", neg_no_recjur)]


def run(title, a):
    """Print the verdict of the equations and of both validators for one atom set."""
    text = serialize.to_string(serialize.serialize(a["n"], a["P"], a["x"], a["pi"]))
    shapes = shape_errors(a)
    failed = failed_equations(a)
    loose = failed_equations(a, strict=False)
    e1, e2 = xsd_errors(text)
    eq_ok, xsd_ok = not failed and not shapes, not e1 and not e2
    print("=" * 100)
    print(title)
    print("  equations: %d of %d hold%s" % (len(g.constraints) - len(failed), len(g.constraints),
                                            "" if len(loose) == len(failed) else
                                            "   (with check.py's own tau: %d fail)" % len(loose)))
    for s in shapes:
        print("    SHAPE", s)
    for k in failed:
        print("    FAILED %s %-10s %s | %s" % (k["constraint_id"], k["kind"], k["formula"], k["path"].replace(BODY + "/", "")))
    print("  xmlschema: %d error(s)" % len(e1))
    for e in e1:
        print("    " + e)
    print("  lxml:      %d error(s)" % len(e2))
    for e in e2:
        print("    " + e)
    print("  -> equations %s, validators %s: %s" % ("hold" if eq_ok else "fail", "accept" if xsd_ok else "reject",
                                                     "AGREE" if eq_ok == xsd_ok else "DISAGREE"))
    return text, eq_ok, xsd_ok


if __name__ == "__main__":
    untouched = all(np.array_equal(c.P[k], base_atoms()["P"][k]) for k in c.P) and \
        all(list(c.x[k]) == list(base_atoms()["x"][k]) for k in c.x)
    print("check.py: equations passed %d, failed %d; its atoms are used unchanged: %s" % (c.passed, len(c.failed), untouched))
    agree = True
    for title, make in CASES:
        text, eq_ok, xsd_ok = run(title, make())
        agree &= eq_ok == xsd_ok
        if make is base_atoms and xsd_ok:
            with open(os.path.join(HERE, "sample.xml"), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
    print("=" * 100)
    print("equations and validators agree in every case:", agree)
