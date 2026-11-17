"""Apply the Link Model to the structure of Calculation-Model/Example.md and
evaluate the Output equations of GeneralSection/CorporateStructure.

Usage: python check.py     (run from XML-Model/Link; needs numpy)
"""
import contextlib
import io
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Output"))
with contextlib.redirect_stdout(io.StringIO()):
    import generate as g

# ================================================================ Input
names = ["UPE", "EE", "A", "B", "C", "PE", "IE1", "ST", "JV", "JS1", "JS2", "P1", "P2", "P3", "IE2", "S", "IE3"]
jur = ["US", "US", "XN", "XQ", "XR", "XQ", "XL", None, "XL", "XL", "XL", "XN", "XR", "XR", "XL", "XD", "XL"]
# The placeholder jurisdictions are replaced by arbitrary valid ISO codes only so
# that the CountryCode type predicate can be evaluated.
iso = {"US": "US", "XN": "AQ", "XQ": "BV", "XR": "HM", "XD": "TF", "XL": "GS"}
own = [("UPE", "EE", 1), ("UPE", "A", 1), ("A", "B", 1), ("B", "C", .9), ("C", "C", .1), ("C", "PE", 1),
       ("C", "IE1", .6), ("B", "IE1", .4), ("B", "ST", 1), ("B", "JV", .5), ("JV", "JS1", 1), ("JV", "JS2", .3),
       ("UPE", "P1", .3), ("P1", "P2", .8), ("P2", "P3", 1), ("P3", "IE2", 1), ("EE", "S", .25), ("UPE", "IE3", .2)]
ctl = [("UPE", "EE"), ("UPE", "A"), ("A", "B"), ("B", "C"), ("C", "PE"), ("C", "IE1"), ("B", "ST"), ("JV", "JS1"),
       ("JV", "JS2"), ("UPE", "P1"), ("P1", "P2"), ("P2", "P3"), ("P3", "IE2"), ("EE", "S"), ("UPE", "IE3")]
N = len(names)
ix = {n: i for i, n in enumerate(names)}


def vec(*ns):
    v = np.zeros(N, bool)
    v[[ix[n] for n in ns]] = True
    return v


group_upe, ee, pe, ie = vec("UPE"), vec("EE"), vec("PE"), vec("IE1", "IE2", "IE3")
stateless, eqt = vec("ST"), vec("JV")
ce = ~vec("EE", "JV", "JS1", "JS2")
ee_type = {"EE": "GIR1004"}
X0 = np.zeros((N, N))
C0 = np.zeros((N, N), bool)
for a, b, r in own:
    X0[ix[a], ix[b]] = r
for a, b in ctl:
    C0[ix[a], ix[b]] = True
jurs = sorted({j for j in jur if j})
M = len(jurs)
EJ = np.zeros((N, M), int)
for i, j in enumerate(jur):
    if j:
        EJ[i, jurs.index(j)] = 1
impl = {"XN": "iir", "XQ": "iir qiir dom qutpr qdmtt", "XR": "iir qiir", "XD": "qdmtt"}
jv = lambda key: np.array([key in impl.get(j, "").split() for j in jurs], int)
tin = ["TIN-" + n for n in names]                      # one TIN per Entity
ET = np.eye(N, dtype=int)                               # Entity-to-TIN matrix
tin_issued = [iso[j] if j else None for j in jur]
tin_type = ["GIR3001"] * N

# ================================================================ Calculation Model
I = np.eye(N)
Ib = I.astype(bool)
one = np.ones(N, int)


def f(X):
    E = X @ np.linalg.inv(I - X)
    return np.linalg.inv(I + np.diag(np.diag(E))) @ E


def w(C):
    C = C.copy()
    for t in range(N):
        C |= np.outer(C[:, t], C[t, :])
    return C


Y, C = f(X0), w(C0)
upe_own = Y.T @ group_upe
jvc = eqt & (upe_own >= .5 - 1e-12)
jvsub = (C.T.astype(int) @ jvc) > 0
jvt = jvc & ~jvsub
J = np.diag(jvt) @ (Ib | C)
jvmember = jvt | jvsub
ord_ce = ce & ~jvmember
S_grp = np.outer(ord_ce, ord_ce) | ((J.T.astype(int) @ J.astype(int)) > 0)
mocec = (ord_ce & ~group_upe & (upe_own <= .3 + 1e-12)) | (jvsub & ((J * Y).T @ one <= .3 + 1e-12))
Cm = (np.diag(mocec) @ C @ np.diag(mocec)).astype(bool) & S_grp
mope = ((Cm.astype(int) @ one) > 0) & ~((Cm.T.astype(int) @ one) > 0)
Mosg = (np.diag(mope) @ (Ib | C) @ np.diag(mocec)).astype(bool) & S_grp
mos = ((Mosg.T.astype(int) @ one) > 0) & ~mope
smoce = mocec & ~mope & ~mos
upe = group_upe & ~ee
Yp = f(np.diag(ce) @ X0 @ np.diag(ce))
owns_ce = np.array([(Y[i] > 1e-12)[ce & (np.arange(N) != i)].any() for i in range(N)])
parent = ce & owns_ce & ~upe & ~pe & ~ie & ~ee & ~jvt & ~jvsub
pope = parent & ((1 - one @ np.diag(upe) @ Yp @ np.diag(parent)) > .2)
ipe = parent & ~pope
qiir = (EJ @ jv("qiir")).astype(bool)

# ================================================================ Link
B = "GLOBE_OECD/GLOBEBody/GeneralSection/"
CS = B + "CorporateStructure/"
rel_id = {r["path"]: r["relation_id"] for r in g.relations}
vec_id = {(v["path"], v["kind"]): v["vector_id"] for v in g.vectors}
n, P, x, pi = {}, {}, {}, {}


def rows(v):
    """Selection matrix: the rows of I_N at which v is True."""
    return np.eye(N, dtype=int)[np.flatnonzero(v)]


def cells(A):
    """Row and column incidence matrices of the non-zero cells of A, in row-major order."""
    r, c = np.nonzero(A)
    R = np.zeros((A.shape[0], len(r)), int)
    Q = np.zeros((len(r), A.shape[1]), int)
    R[r, np.arange(len(r))] = 1
    Q[np.arange(len(r)), c] = 1
    return R, Q


def pick(Q, values):
    """Q x values for a vector of arbitrary values."""
    return [values[j] for j in np.argmax(Q, axis=1)] if Q.shape[0] else []


def relation(path, Pm):
    P[rel_id[path]] = np.asarray(Pm, int)
    n[rel_id[path]] = P[rel_id[path]].shape[1]


def value(path, values, present=None):
    values = list(values)
    if present is not None:
        values = [v if p else None for v, p in zip(values, present)]
    x[vec_id[(path, "value")]] = values


def presence(path, p):
    pi[vec_id[(path, "presence")]] = np.asarray(p, int)


def tin_block(path, Q, text, issued, typ, unknown=None):
    k = Q.shape[0]
    unknown = unknown if unknown is not None else [False] * k
    value(path + "/#text", text)
    presence(path + "/@issuedBy", [v is not None for v in issued])
    value(path + "/@issuedBy", issued)
    presence(path + "/@unknown", unknown)
    value(path + "/@unknown", [True if u else None for u in unknown])
    presence(path + "/@TypeOfTIN", [1] * k)
    value(path + "/@TypeOfTIN", typ)


# Entity-level matrices shared by every ID block
codes = [iso[j] for j in jurs] + ["X5"]                 # X5: Stateless Constituent Entities
EJx = np.hstack([EJ, stateless.astype(int)[:, None]])
r201, r202 = EJ @ (jv("qiir") & ~jv("dom")), EJ @ (jv("qiir") & jv("dom"))
r203, r204 = EJ @ jv("qutpr"), EJ @ jv("qdmtt")
Rule = np.stack([r201, r202, r203, r204, 1 - np.clip(r201 + r202 + r203 + r204, 0, 1)], axis=1)
rule_codes = ["GIR201", "GIR202", "GIR203", "GIR204", "GIR205"]
main = (C0.astype(int) @ pe) > 0
zero = np.zeros(N, bool)
status_cols = [ce, zero, zero, zero, pe, main, mope, mos, smoce, ie, zero, zero, jvt, jvsub, zero, ee, zero, zero]
Status = np.stack(status_cols, axis=1).astype(int)
status_codes = ["GIR3%02d" % k for k in range(1, 19)]


def id_block(path, S, mask=None, excluded=False):
    """Name and the four repeated children of an ID element, for the Entities selected by S.

    An Excluded UPE reports neither ResCountryCode nor Rules.
    """
    D = np.diag(mask) if mask is not None else np.eye(S.shape[0], dtype=int)
    value(path + "/Name", pick(S, names), mask)
    for child, A, vals in (("ResCountryCode", EJx, codes), ("Rules", Rule, rule_codes), ("GlobeStatus", Status, status_codes)):
        R, Q = cells(D @ S @ (0 * A if excluded and child != "GlobeStatus" else A))
        relation(path + "/" + child, R)
        value(path + "/" + child, pick(Q, vals))
    R, Q = cells(D @ S @ ET)
    relation(path + "/TIN", R)
    tin_block(path + "/TIN", Q, pick(Q, tin), pick(Q, tin_issued), pick(Q, tin_type))


n["r001"], n["r002"] = 1, 1
P["r002"] = np.ones((1, 1), int)
presence(B.rstrip("/"), [1])

# ---- UPE
S_U = rows(group_upe)
relation(CS + "UPE", np.ones((1, S_U.shape[0]), int))
ex = S_U @ ee
for branch, mask in (("ExcludedUPE", ex), ("OtherUPE", 1 - ex)):
    bp = CS + "UPE/(choice1)/" + branch
    presence(bp, mask)
    presence(bp + "/Art10.3.5", 0 * mask)
    value(bp + "/Art10.3.5", [None] * len(mask))
    id_block(bp + "/ID", S_U, mask, excluded=(branch == "ExcludedUPE"))
value(CS + "UPE/(choice1)/ExcludedUPE/ExcludedUPEStatus", [None] * len(ex))

# ---- CE
S_C = rows((ce | jvmember) & ~group_upe)
nC = S_C.shape[0]
relation(CS + "CE", np.ones((1, nC), int))
id_block(CS + "CE/ID", S_C)

relation(CS + "CE/OwnershipChange", np.zeros((nC, 0)))          # in-year changes: not modelled
relation(CS + "CE/OwnershipChange/PreGlobeStatus", np.zeros((0, 0)))
relation(CS + "CE/OwnershipChange/PreOwnership", np.zeros((0, 0)))
for v in g.vectors:
    if v["path"].startswith(CS + "CE/OwnershipChange"):
        (x if v["kind"] == "value" else pi)[v["vector_id"]] = [] if v["kind"] == "value" else np.zeros(0, int)

member = (group_upe | ce | jvmember) & ~ee                       # owners reported individually
Xt = np.diag(~ee) @ X0 @ np.linalg.inv(I - np.diag(ee) @ X0)     # looking through Excluded Entities
W = np.vstack([np.diag(member) @ (Xt - np.diag(np.diag(Xt))),
               ee @ X0 - one @ np.diag(member) @ (Xt - X0),
               1 - one @ X0])
owner_type = [("GIR801" if group_upe[i] else "GIR803" if jvt[i] else "GIR804" if jvsub[i] else "GIR802")
              for i in range(N)] + ["GIR805", "GIR806"]
A = np.round((W @ S_C.T).T, 4)
R, Q = cells(A > 0)
relation(CS + "CE/Ownership", R)
value(CS + "CE/Ownership/OwnershipType", pick(Q, owner_type))
value(CS + "CE/Ownership/OwnershipPercentage", [float(v) for v in A[A > 0]])
agg = [j >= N for j in np.argmax(Q, axis=1)]
tin_block(CS + "CE/Ownership/TIN", Q, pick(Q, tin + ["NOTIN", "NOTIN"]), pick(Q, tin_issued + [None, None]),
          pick(Q, tin_type + ["GIR3004", "GIR3004"]), agg)

q_upe_ipe = qiir & (upe ^ ipe)
exc213 = ipe & qiir & ((C.T.astype(int) @ q_upe_ipe) > 0)
wholly = (np.abs(Y - 1) < 1e-9) & ~Ib
exc215 = pope & qiir & ((wholly.T.astype(int) @ (qiir & pope)) > 0)


def top(i, above, cand):
    """The candidate above Entity i that has no other candidate above it."""
    ks = [k for k in range(N) if above[k, i] and cand[k]]
    return next(k for k in ks if not any(above[m, k] for m in ks))


displacer = [top(i, C, q_upe_ipe) if exc213[i] else top(i, wholly, qiir & pope) if exc215[i] else None for i in range(N)]
exc = S_C @ (exc213 | exc215)
presence(CS + "CE/QIIR", S_C @ ((pope | ipe) & qiir))
value(CS + "CE/QIIR/POPE-IPE", pick(S_C, ["GIR901" if p else "GIR902" for p in pope]), S_C @ ((pope | ipe) & qiir))
presence(CS + "CE/QIIR/Exception", exc)
for art, v in (("Art2.1.3", exc213), ("Art2.1.5", exc215)):
    presence(CS + "CE/QIIR/Exception/ExceptionRule/(choice1)/" + art, S_C @ v)
    value(CS + "CE/QIIR/Exception/ExceptionRule/(choice1)/" + art, [True] * nC, S_C @ v)
d = pick(S_C, displacer)
tp = CS + "CE/QIIR/Exception/TIN"
value(tp + "/#text", [tin[k] if k is not None else None for k in d])
presence(tp + "/@issuedBy", [k is not None and tin_issued[k] is not None for k in d])
value(tp + "/@issuedBy", [tin_issued[k] if k is not None else None for k in d])
presence(tp + "/@unknown", [0] * nC)
value(tp + "/@unknown", [None] * nC)
presence(tp + "/@TypeOfTIN", exc)
value(tp + "/@TypeOfTIN", [tin_type[k] if k is not None else None for k in d])

for name in ("QUTPR", "QUTPR/AggOwnership", "QUTPR/UPEOwnership"):   # pending 05.UTPR
    presence(CS + "CE/" + name, [0] * nC)
for name in ("QUTPR/Art9.3", "QUTPR/AggOwnership", "QUTPR/UPEOwnership"):
    value(CS + "CE/" + name, [None] * nC)

# ---- Excluded Entities
S_E = rows(ee & ~group_upe)
relation(CS + "ExcludedEntity", np.ones((1, S_E.shape[0]), int))
value(CS + "ExcludedEntity/Name", pick(S_E, names))
value(CS + "ExcludedEntity/Type", pick(S_E, [ee_type.get(nm) for nm in names]))
value(CS + "ExcludedEntity/Change", [False] * S_E.shape[0])
presence(CS + "UnreportChangeCorpStr", [0])
value(CS + "UnreportChangeCorpStr", [None])

# ================================================================ Output equations
enum = {}
for e in g.enum_rows:
    enum.setdefault(e["type_id"], set()).add(e["value"])


def tau(type_id, values):
    t = g.type_rows[type_id]

    def ok(v):
        if v is None:
            return False
        if t.get("enumerations"):
            return v in enum[type_id]
        if "minLength" in t or "maxLength" in t:
            return int(t.get("minLength", 0)) <= len(v) <= int(t.get("maxLength", 10 ** 9))
        if "minInclusive" in t:
            scaled = v * 10 ** int(t["fractionDigits"])
            return float(t["minInclusive"]) <= v <= float(t["maxInclusive"]) and abs(scaled - round(scaled)) < 1e-6
        return {"boolean": isinstance(v, bool), "integer": isinstance(v, int)}.get(t["primitive"], isinstance(v, str))

    return np.array([ok(v) for v in values], int)


def python(formula):
    f = re.sub(r"tau\[([^\]]*)\]\(x_(v\d+)\)", r"tau('\1', x['\2'])", formula)
    f = re.sub(r"P_(r\d+)\^T 1", r"P['\1'].sum(0)", f)
    f = re.sub(r"P_(r\d+) 1", r"P['\1'].sum(1)", f)
    f = re.sub(r"pi_(v\d+)", r"pi['\1']", f)
    f = f.replace(" . ", " * ")
    lhs, op, rhs = re.split(r" (>=|<=|=) ", f, maxsplit=1)
    return "np.all(%s %s %s)" % (lhs, "==" if op == "=" else op, rhs)


passed, failed, skipped = 0, [], 0
for c in g.constraints:
    if c["kind"] == "root" or not c["path"].startswith(CS):
        continue
    try:
        result = eval(python(c["formula"]))
    except KeyError:
        skipped += 1
        continue
    if result:
        passed += 1
    else:
        failed.append(c)

if __name__ == "__main__":
    print("rows:", {r["path"].replace(CS, ""): n[r["relation_id"]] for r in g.relations if r["relation_id"] in n and r["path"].startswith(CS)})
    print("equations passed: %d, failed: %d, not evaluated: %d" % (passed, len(failed), skipped))
    for c in failed:
        print("FAILED", c["kind"], c["formula"], "|", c["path"].replace(CS, ""))
