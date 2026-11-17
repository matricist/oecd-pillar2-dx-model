"""Apply the Link Model to the structure of Calculation-Model/Example.md, with
example amounts, and evaluate every Output equation on the result.

Usage: python check.py     (run from GIR-Model/Link; needs numpy)
"""
import contextlib
import datetime
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
ee_type = {"EE": "GIR1004"}                              # kind of Excluded Entity (GIR1001 to GIR1008)
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
impl = {"XN": "iir dom self", "XQ": "iir qiir dom qutpr qdmtt", "XR": "iir qiir", "XD": "qdmtt"}
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

# Taxing Rights: IIR payability
iir, dom = (EJ @ jv("iir")).astype(bool), (EJ @ jv("dom")).astype(bool)
samejur = (EJ @ EJ.T) > 0
member = ce | jvt | jvsub
Own = (Y > 1e-12) & ~Ib
cond = ((np.diag(iir) @ ~samejur) | np.outer(dom & iir, np.ones(N, bool))) & member[None, :] & Own
UI = (np.diag(upe ^ ipe) @ cond).astype(bool)
PC = (np.diag(pope) @ cond).astype(bool)
UI &= ~((C.T.astype(int) @ (np.diag(qiir) @ UI).astype(int)) > 0)
PC &= ~(((np.abs(Y - 1) < 1e-9).T.astype(int) @ (np.diag(qiir) @ PC).astype(int)) > 0)
Iir_payable = UI ^ PC
self_iir = (EJ @ jv("self")).astype(bool)
covered_same = ((Iir_payable & samejur).T.astype(int) @ one) > 0
covered_upe = (Iir_payable.T.astype(int) @ upe) > 0
upper_ipe = ((C & ~samejur).T.astype(int) @ ipe) > 0
self_payable = self_iir & ~covered_same & (pope | (ipe & ~covered_upe & ~upper_ipe))

# ================================================================ Link
B = "GLOBE_OECD/GLOBEBody/GeneralSection/"
CS = B + "CorporateStructure/"
def plain(path):
    """A path without the (sequenceN) and (choiceN) group markers."""
    return re.sub(r"/\((sequence|choice)\d+\)", "", path)


rel_id = {r["path"]: r["relation_id"] for r in g.relations}
vec_id = {(v["path"], v["kind"]): v["vector_id"] for v in g.vectors}
rel_id.update({plain(r["path"]): r["relation_id"] for r in g.relations})
vec_id.update({(plain(v["path"]), v["kind"]): v["vector_id"] for v in g.vectors if v["node"] not in ("sequence", "choice")})
n, P, x, pi = {}, {}, {}, {}
linked = set()                                           # value vectors the Link Model defines


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
    linked.add(vec_id[(path, "value")])
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
# An Excluded UPE reports its kind with the GIR60x code that corresponds to GIR100x.
upe_status = [("GIR6" + ee_type[nm][-2:]) if nm in ee_type else None for nm in names]
value(CS + "UPE/(choice1)/ExcludedUPE/ExcludedUPEStatus", pick(S_U, upe_status), ex)

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

owner = (group_upe | ce | jvmember) & ~ee                        # owners reported individually
Xt = np.diag(~ee) @ X0 @ np.linalg.inv(I - np.diag(ee) @ X0)     # looking through Excluded Entities
W = np.vstack([np.diag(owner) @ (Xt - np.diag(np.diag(Xt))),
               ee @ X0 - one @ np.diag(owner) @ (Xt - X0),
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

for name in ("QUTPR", "QUTPR/AggOwnership", "QUTPR/UPEOwnership"):   # pending UTPR
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

# ---- JurisdictionSection: rows, Jurisdiction, recipients, jurisdictions with taxing rights
JS = "GLOBE_OECD/GLOBEBody/JurisdictionSection"
in_scope = ce | jvmember
sec = (EJx.T @ in_scope) > 0                                     # jurisdictions (and X5) with Entities
S_J = np.eye(M + 1, dtype=int)[np.flatnonzero(sec)]
nJ = S_J.shape[0]
relation(JS, np.ones((1, nJ), int))
value(JS + "/Jurisdiction", pick(S_J, codes))
rec_jur = np.zeros((M + 1, M), int)                              # Input: recipients of each section
rec_jur[:, jurs.index("US")] = 1
R, Q = cells(S_J @ rec_jur)
relation(JS + "/RecJurCode", R)
value(JS + "/RecJurCode", pick(Q, codes))
iir_rights = (EJ.T @ (((Iir_payable | np.diag(self_payable)).astype(int) @ EJx) > 0)) > 0  # collecting jurisdiction x section
qdmtt_rights = np.hstack([np.diag(jv("qdmtt")), np.zeros((M, 1), int)]) > 0
R, Q = cells(S_J @ (iir_rights | qdmtt_rights).T)
relation(JS + "/JurWithTaxingRights", R)
value(JS + "/JurWithTaxingRights/JurisdictionName", pick(Q, codes))
value(JS + "/DocSpec/DocTypeIndic", ["OECD1"] * nJ)              # Input: filing metadata
value(JS + "/DocSpec/DocRefId", ["DOC-%s" % c for c in pick(S_J, codes)])

# ================================================================ Input: amounts and filing data (example)
def amounts(**kw):
    return np.array([kw.get(nm, 0) for nm in names], float)


fanil = amounts(UPE=1000, A=800, B=600, PE=200, C=500, IE1=300, ST=100, JV=400, JS1=200, JS2=100,
                P1=200, P2=300, P3=100, IE2=100, S=200, IE3=100)       # financial accounting net income
income_tax = amounts(UPE=250, A=40, B=60, PE=20, C=100, JV=20, JS1=10, JS2=15, P1=10, P3=20, S=10)
globe_income, act = fanil.copy(), income_tax.copy()                    # no adjustments in the example
sbie = amounts(A=100)
emp, tan = amounts(B=50, PE=10), amounts(B=1000, PE=200)
tcsh_rev, tcsh_pbt, tcsh_tax, tcsh_sbie = 5 * fanil, fanil.copy(), income_tax.copy(), sbie.copy()
tcsh_elected_jur = {"US"}
qdmtt_of = {"B": 40, "S": 20}                                          # QDMTT of the group of each named Entity
r_min, tau, d_R, d_P = 0.15, 0.15, 10_000_000, 1_000_000
filing = {"transmitting": "US", "receiving": "US", "message_ref": "US2025-GIR-0001", "period_start": "2025-01-01",
          "period_end": "2025-12-31", "timestamp": "2026-06-30T00:00:00", "filing_ce": "UPE", "role": "GIR401",
          "cfs": "GIR501", "fas": "US GAAP", "currency": "EUR", "name_mne": "Example Group"}
utpr_cash = {"XQ": 145}                                                # additional cash tax expense by jurisdiction

# ================================================================ Calculation Model: groups, TCSH, Top-up Tax, IIR, UTPR
dag = lambda v: np.where(v > 0, 1 / np.where(v > 0, v, 1), 0.0)
pos = lambda v: np.maximum(v, 0)
idx = np.arange(1, N + 1)
jv_id = J.T.astype(int) @ idx
mosg_id = Mosg.T.astype(int) @ idx + (smoce & ~ie) * idx
group_id = stateless * idx + ~stateless * (mosg_id + (mosg_id == 0) * jv_id)
eq = lambda v: np.equal.outer(v, v)


def partition(Same):
    """Membership matrix (Entities x groups) of the distinct non-zero rows of Same."""
    seen = []
    for row in Same:
        if row.any() and not any((row == q).all() for q in seen):
            seen.append(row)
    return np.array(seen, int).T.reshape(N, len(seen))


EG = partition(eq(group_id) & eq(ie) & (samejur | Ib) & np.outer(in_scope, in_scope))       # Entt-group
in_tcsh = in_scope & ~ie & ~stateless
EGt = partition(eq(jv_id) & samejur & np.outer(in_tcsh, in_tcsh))                          # G_TCSH, transposed

# TCSH
t_r, t_p, t_t, t_s = (EGt.T @ v for v in (tcsh_rev, tcsh_pbt, tcsh_tax, tcsh_sbie))
t_dm, t_setr, t_rp = (t_r < d_R) & (t_p < d_P), (t_p > 0) & (t_t >= tau * t_p), t_p <= t_s
first = EGt.argmax(axis=0)                                             # one Entity of each Tested Jurisdiction
t_elected = np.array([jur[i] in tcsh_elected_jur for i in first])
t_applied = t_elected & (t_dm | t_setr | t_rp)
tcsh_entity = (EGt @ t_applied) > 0

# Top-up Tax Calculation; a group under an applied TCSH has no Top-up Tax
MC = EG.shape[1]
g_first = EG.argmax(axis=0)
safe = (EG.T @ tcsh_entity) == EG.sum(axis=0)
qdmtt = np.zeros(MC)
for nm, amount in qdmtt_of.items():
    qdmtt[EG[ix[nm]].argmax()] = amount
ente_prior = np.zeros(MC)
g_income, g_tax = EG.T @ globe_income, EG.T @ act
g_pos, g_expected = g_income > 0, r_min * g_income
ente_used = g_pos * np.minimum(ente_prior, pos(g_tax))
etr = g_pos * (pos(g_tax) - ente_used) * dag(pos(g_income))
tt_percent = g_pos * pos(r_min - etr)
excess = pos(g_income - EG.T @ sbie)
art415 = ~g_pos & (g_tax < 0) & (g_tax < g_expected)
actt415 = art415 * (g_expected - g_tax)
ente_generated = g_pos * pos(-g_tax)
ente_next = ente_prior - ente_used + ente_generated
regular = tt_percent * excess
gross = regular + actt415
tt_group = ~safe * pos(gross - qdmtt)
theta = tt_group * dag(gross)
key = pos(globe_income)
key415 = ((act < 0) & (act < r_min * globe_income)) * (r_min * globe_income - act)
alloc = lambda k: np.diag(k) @ EG @ np.diag(dag(EG.T @ k))
tt_entt = alloc(key) @ (theta * regular) + alloc(key415) @ (theta * actt415)
assert np.allclose(EG.T @ tt_entt, tt_group)

# IIR under Qualified IIRs: Net Income Inclusion Ratio
d0 = np.diag(X0).copy()
X_iir = np.diag(member) @ ((X0 - np.diag(d0)) / (1 - d0)[None, :]) @ np.diag(member)
Y_iir = f(X_iir)
Qpay = (np.diag(qiir) @ Iir_payable).astype(float)
net, unpaid = np.zeros((N, N)), np.eye(N)
for _ in range(4 * N):
    flow = X_iir @ unpaid
    net, unpaid = net + flow * Qpay, flow * (1 - Qpay)
gross_iir = Y_iir * Qpay

# UTPR
charged = net + np.diag((self_payable & qiir).astype(float))
gY = Y_iir - np.diag(np.diag(Y_iir)) + np.eye(N)
residual = np.diag(upe) @ gY @ (np.eye(N) - charged)
utpr_ratio = ((residual.T @ one) > 1e-12) * pos(1 - charged.T @ one)
utpr_tt = utpr_ratio * tt_entt
utpr_total = utpr_tt.sum()
qutpr, utpr_zero = jv("qutpr").astype(bool), np.zeros(M, bool)
utpr_jur = qutpr & (~utpr_zero | (qutpr @ ~utpr_zero == 0))
data_jur = np.diag(utpr_jur) @ EJ.T @ np.diag(ce & ~ie) @ np.stack([emp, tan], axis=1)
utpr_percentage = data_jur @ np.diag(dag(data_jur.sum(axis=0))) @ np.array([.5, .5])
utpr_amount = utpr_total * utpr_percentage

# ================================================================ Link: the rest of the return
whole = lambda v: int(round(float(v)))
ratio4 = lambda v: round(min(max(float(v), 0.0), 1.0), 4)
BODY = "GLOBE_OECD/GLOBEBody"


def single(path, v):
    """A value of a relation that has one row, with its optional ancestors present."""
    value(path, [v])


def inline_tin(path, entities, mask=None):
    """An inline TIN element of a relation whose rows refer to `entities` (None: no TIN to report)."""
    k = len(entities)
    mask = [1] * k if mask is None else list(mask)
    known = [e is not None and bool(m) for e, m in zip(entities, mask)]
    value(path + "/#text", [(tin[e] if e is not None else "NOTIN") if m else None for e, m in zip(entities, mask)])
    presence(path + "/@issuedBy", [kn and tin_issued[e] is not None for kn, e in zip(known, entities)])
    value(path + "/@issuedBy", [tin_issued[e] if kn else None for kn, e in zip(known, entities)])
    presence(path + "/@unknown", [bool(m) and e is None for e, m in zip(entities, mask)])
    value(path + "/@unknown", [True if (m and e is None) else None for e, m in zip(entities, mask)])
    presence(path + "/@TypeOfTIN", mask)
    value(path + "/@TypeOfTIN", [(tin_type[e] if e is not None else "GIR3004") if m else None for e, m in zip(entities, mask)])


# ---- MessageSpec, FilingInfo, GeneralSection: Input, passed through
MS = "GLOBE_OECD/MessageSpec/"
single(MS + "TransmittingCountry", filing["transmitting"])
single(MS + "ReceivingCountry", filing["receiving"])
single(MS + "MessageType", "GIR")
single(MS + "MessageRefId", filing["message_ref"])
single(MS + "MessageTypeIndic", "GIR101")
single(MS + "ReportingPeriod", filing["period_end"])
single(MS + "Timestamp", filing["timestamp"])
FI = BODY + "/FilingInfo/"
fce = ix[filing["filing_ce"]]
single(FI + "FilingCE/ResCountryCode", iso[jur[fce]])
single(FI + "FilingCE/Name", names[fce])
inline_tin(FI + "FilingCE/TIN", [fce])
single(FI + "FilingCE/Role", filing["role"])
single(FI + "AccountingInfo/CFSofUPE", filing["cfs"])
single(FI + "AccountingInfo/FAS", filing["fas"])
single(FI + "AccountingInfo/Currency", filing["currency"])
single(FI + "Period/Start", filing["period_start"])
single(FI + "Period/End", filing["period_end"])
single(FI + "NameMNE", filing["name_mne"])
single(FI + "DocSpec/DocTypeIndic", "OECD1")
single(FI + "DocSpec/DocRefId", "DOC-FilingInfo")
single(BODY + "/GeneralSection/DocSpec/DocTypeIndic", "OECD1")
single(BODY + "/GeneralSection/DocSpec/DocRefId", "DOC-GeneralSection")
relation(BODY + "/GeneralSection/RecJurCode", np.ones((1, 1), int))
value(BODY + "/GeneralSection/RecJurCode", [filing["receiving"]])

# ---- Calculation units: one per applied TCSH Tested Jurisdiction, one per remaining Full Calculation Group
units = [{"tcsh": True, "members": EGt[:, t], "t": t} for t in np.flatnonzero(t_applied)] + \
        [{"tcsh": False, "members": EG[:, k], "g": k} for k in np.flatnonzero(~safe)]
sec_row = {int(c): r for r, c in enumerate(np.flatnonzero(sec))}        # section column -> row of JurisdictionSection
rights = S_J @ (iir_rights | qdmtt_rights).T                            # sections x collecting jurisdictions
for u in units:
    m0 = int(np.flatnonzero(u["members"])[0])
    u["section"] = sec_row[int(EJx[m0].argmax())]
    u["has_rights"] = bool(rights[u["section"]].any())
    gid = int(group_id[m0])
    if u["tcsh"]:
        u["top"], u["kinds"] = (int(jv_id[m0]) - 1, ["05"]) if jv_id[m0] else (None, [])
        u["etr_kinds"] = ["08"] if jv_id[m0] else ["07"]
    else:
        kinds = (["06"] if stateless[m0] else ["02"] if (mope | mos)[m0] else ["03"] if smoce[m0] and gid == m0 + 1
                 else ["05"] if jvmember[m0] else [])
        kinds += ["04"] if ie[m0] else []
        u["top"], u["kinds"], u["etr_kinds"] = (gid - 1 if gid else None), kinds, kinds
nU = len(units)
sub = np.array([bool(u["kinds"]) for u in units])
etr_sub = np.array([bool(u["etr_kinds"]) for u in units])
tops = [u["top"] for u in units]
u_section = np.zeros((nJ, nU), int)
for k, u in enumerate(units):
    u_section[u["section"], k] = 1
has_rights = np.array([u["has_rights"] for u in units])
full = np.array([not u["tcsh"] for u in units])
gi_ = np.array([u.get("g", 0) for u in units])
ti_ = np.array([u.get("t", 0) for u in units])
u_tt = np.where(full, tt_group[gi_], 0.0)
u_qdmtt = np.where(full, qdmtt[gi_], 0.0)


def band(amount, series):
    """Range code of an amount in EUR: none, below 1m, 5m, 25m, 50m, 75m, 100m, 250m, or above."""
    limits = [1e6, 5e6, 25e6, 50e6, 75e6, 100e6, 250e6]
    return "GIR%s%02d" % (series, 1 if amount <= 0 else 2 + sum(amount >= lim for lim in limits))


# ---- Summary: one row per calculation unit
SM = BODY + "/Summary"
relation(SM, np.ones((1, nU), int))
presence(SM + "/Jurisdiction/JurisdictionName", [1] * nU)
value(SM + "/Jurisdiction/JurisdictionName", pick(u_section.T @ S_J, codes))
R, Q = cells(u_section.T @ S_J @ rec_jur)
relation(SM + "/RecJurCode", R)
value(SM + "/RecJurCode", pick(Q, codes))
R, Q = cells(np.diag(sub & has_rights))
relation(SM + "/Jurisdiction/Subgroup", R)
inline_tin(SM + "/Jurisdiction/Subgroup/TIN", pick(Q, tops))
kind_codes = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
K = np.array([[kc in u["kinds"] for kc in kind_codes] for u in units], int)
Rk, Qk = cells(Q @ K)
relation(SM + "/Jurisdiction/Subgroup/TypeofSubGroup", Rk)
value(SM + "/Jurisdiction/Subgroup/TypeofSubGroup", pick(Qk, ["GIR11" + kc for kc in kind_codes]))
R, Q = cells(u_section.T @ rights)
relation(SM + "/JurWithTaxingRights", R)
presence(SM + "/JurWithTaxingRights/JurisdictionName", [1] * R.shape[1])
value(SM + "/JurWithTaxingRights/JurisdictionName", pick(Q, codes))
presence(SM + "/JurWithTaxingRights/DiffDomesticTut", [0] * R.shape[1])
value(SM + "/JurWithTaxingRights/DiffDomesticTut", [None] * R.shape[1])
passed = np.zeros((nU, 3), int)                                         # TCSH tests passed: de minimis, ETR, routine profits
passed[~full] = np.stack([t_dm, t_setr, t_rp], axis=1)[ti_[~full]]
R, Q = cells(np.diag(has_rights) @ passed)
relation(SM + "/SafeHarbour", R)
value(SM + "/SafeHarbour", pick(Q, ["GIR1203", "GIR1204", "GIR1205"]))
show_etr = has_rights & (~full | g_pos[gi_])
presence(SM + "/ETRRange", show_etr)
value(SM + "/ETRRange", ["GIR1314" if not fl else "GIR13%02d" % min(int(e / .025) + 1, 13)
                         for fl, e in zip(full, etr[gi_])], show_etr)
presence(SM + "/QDMTTut", has_rights & full)
value(SM + "/QDMTTut", [band(a, "14") for a in u_qdmtt], has_rights & full)
presence(SM + "/GLoBETut", has_rights)
value(SM + "/GLoBETut", [band(a, "15") for a in u_tt], has_rights)
value(SM + "/DocSpec/DocTypeIndic", ["OECD1"] * nU)
value(SM + "/DocSpec/DocRefId", ["DOC-Summary-%d" % (k + 1) for k in range(nU)])

# ---- JurisdictionSection/GLoBETax/ETR: one row per calculation unit
ET = JS + "/GLoBETax/ETR"
relation(ET, u_section)
presence(ET + "/SubGroup", etr_sub)
inline_tin(ET + "/SubGroup/TIN", tops, etr_sub)
E = np.array([[kc in u["etr_kinds"] for kc in kind_codes] for u in units], int)
R, Q = cells(E)
relation(ET + "/SubGroup/TypeofSubGroup", R)
value(ET + "/SubGroup/TypeofSubGroup", pick(Q, ["GIR16" + kc for kc in kind_codes]))
EX = ET + "/ETRStatus/ETRException"
presence(EX, ~full)
presence(EX + "/TransitionalCbCRSafeHarbour", ~full)
for name, v in (("Revenue", t_r), ("Profit", t_p), ("IncomeTax", t_t)):
    value(EX + "/TransitionalCbCRSafeHarbour/" + name, [whole(a) for a in v[ti_]], ~full)
EC = ET + "/ETRStatus/ETRComputation"
OC = EC + "/OverallComputation"
presence(EC, full)
presence(OC, full)
for name, v in (("FANIL", EG.T @ fanil), ("AdjustedFANIL", EG.T @ fanil), ("NetGlobeIncome/Total", g_income),
                ("IncomeTaxExpense", EG.T @ income_tax), ("ExcessProfits", excess), ("TopUpTax", tt_group),
                ("ExcessNegTaxExpense/PriorYearBalance", ente_prior), ("ExcessNegTaxExpense/GeneratedInRFY", ente_generated),
                ("ExcessNegTaxExpense/UtilizedInRFY", ente_used), ("ExcessNegTaxExpense/Remaining", ente_next)):
    value(OC + "/" + name, [whole(a) for a in v[gi_]], full)
value(OC + "/ETRRate", [ratio4(a) for a in etr[gi_]], full)
value(OC + "/TopUpTaxPercentage", [ratio4(a) for a in tt_percent[gi_]], full)
presence(OC + "/AdjustedCoveredTax", full)
value(OC + "/AdjustedCoveredTax/Total", [whole(a) for a in g_tax[gi_]], full)
value(OC + "/AdjustedCoveredTax/AggregrateCurrentTax", [whole(a) for a in (EG.T @ income_tax)[gi_]], full)
has_q = full & (u_qdmtt > 0)
presence(OC + "/QDMTT", has_q)
value(OC + "/QDMTT/FAS", [filing["fas"]] * nU, has_q)
value(OC + "/QDMTT/Amount", [whole(a) for a in u_qdmtt], has_q)
value(OC + "/QDMTT/SBIEAvailable", [True] * nU, has_q)
value(OC + "/QDMTT/DeMinAvailable", [True] * nU, has_q)
value(OC + "/QDMTT/Currency", [filing["currency"]] * nU, has_q)
has_415 = full & art415[gi_]
presence(OC + "/AdditionalTopUpTax", has_415)
presence(OC + "/AdditionalTopUpTax/Art4.1.5", has_415)
for name, v in (("AdjustedCoveredTax", g_tax), ("GlobeLoss", g_income), ("ExpectedAdjustedCoveredTax", g_expected),
                ("AdditionalTopUpTax", actt415)):
    value(OC + "/AdditionalTopUpTax/Art4.1.5/" + name, [whole(a) for a in v[gi_]], has_415)

# CEComputation: one row per Entity of each fully calculated unit
CM = np.array([u["members"] * (not u["tcsh"]) for u in units], int)      # units x Entities
R, Q = cells(CM)
CC = EC + "/CEComputation"
relation(CC, R)
ents = [int(e) for e in np.argmax(Q, axis=1)]
inline_tin(CC + "/TIN", ents)
for name, v in (("AdjustedFANIL/Total", fanil), ("AdjustedFANIL/FANIL", fanil), ("NetGlobeIncome/Total", globe_income),
                ("AdjustedIncomeTax/Total", income_tax), ("AdjustedIncomeTax/IncomeTax", income_tax),
                ("AdjustedCoveredTax/Total", act), ("AdjustedCoveredTax/DeferTaxAdjustAmt/Total", 0 * act),
                ("AdjustedCoveredTax/DeferTaxAdjustAmt/DeferTaxExpense", 0 * act)):
    value(CC + "/" + name, [whole(v[e]) for e in ents])

# ---- JurisdictionSection/LowTaxJurisdiction
LT = JS + "/LowTaxJurisdiction"
sec_tt = u_section @ u_tt
presence(LT, sec_tt > 0)
value(LT + "/TopUpTaxAmount", [whole(a) for a in sec_tt], sec_tt > 0)
ltce = np.flatnonzero(np.round(tt_entt) > 0)
L = np.zeros((nJ, len(ltce)), int)
for k, e in enumerate(ltce):
    L[sec_row[int(EJx[e].argmax())], k] = 1
relation(LT + "/LTCE", L)
inline_tin(LT + "/LTCE/TIN", [int(e) for e in ltce])
relation(LT + "/LTCE/IIR", np.eye(len(ltce), dtype=int))
presence(LT + "/LTCE/IIR/NetGlobeIncome", [1] * len(ltce))
value(LT + "/LTCE/IIR/NetGlobeIncome", [whole(globe_income[e]) for e in ltce])
value(LT + "/LTCE/IIR/TopUpTax", [whole(tt_entt[e]) for e in ltce])
R, Q = cells(Qpay[:, ltce].T)                                           # LTCE rows x Parent Entities
relation(LT + "/LTCE/IIR/ParentEntity", R)
PE_ = LT + "/LTCE/IIR/ParentEntity"
par = [int(k) for k in np.argmax(Q, axis=1)]
low = [int(ltce[j]) for j in np.argmax(R, axis=0)] if R.shape[1] else []
inline_tin(PE_ + "/TIN", par)
value(PE_ + "/ResCountryCode", [iso[jur[k]] for k in par])
value(PE_ + "/OtherOwnershipAllocation", [whole((1 - Y_iir[k, j]) * globe_income[j]) for k, j in zip(par, low)])
value(PE_ + "/InclusionRatio", [ratio4(Y_iir[k, j]) for k, j in zip(par, low)])
value(PE_ + "/TopUpTaxShare", [whole(gross_iir[k, j] * tt_entt[j]) for k, j in zip(par, low)])
value(PE_ + "/IIROffSet", [whole((gross_iir[k, j] - net[k, j]) * tt_entt[j]) for k, j in zip(par, low)])
value(PE_ + "/TopUpTax", [whole(net[k, j] * tt_entt[j]) for k, j in zip(par, low)])
sec_utpr = np.array([utpr_tt[(EJx[:, int(c)] > 0)].sum() for c in np.flatnonzero(sec)])
presence(LT + "/UTPR", sec_utpr > 0)
presence(LT + "/UTPR/UTPRSafeHarbour", [0] * nJ)
presence(LT + "/UTPR/UTPRCalculation", sec_utpr > 0)
value(LT + "/UTPR/UTPRCalculation/TotalUTPRTopUpTax", [whole(a) for a in sec_utpr], sec_utpr > 0)
value(LT + "/UTPR/UTPRCalculation/Article2.5.1TopUpTax", [whole(a) for a in sec_utpr], sec_utpr > 0)

# ---- UTPRAttribution
UA = BODY + "/UTPRAttribution"
relation(UA, np.ones((1, int(utpr_total > 0)), int))
relation(UA + "/RecJurCode", np.ones((int(utpr_total > 0), int(utpr_total > 0)), int))
value(UA + "/RecJurCode", [filing["receiving"]] * int(utpr_total > 0))
uj = np.flatnonzero(utpr_jur) if utpr_total > 0 else np.array([], int)
relation(UA + "/Attribution", np.ones((int(utpr_total > 0), len(uj)), int))
AT = UA + "/Attribution/"
cash = np.array([utpr_cash.get(jurs[k], 0) for k in uj], float)
value(AT + "ResCountryCode", [codes[k] for k in uj])
value(AT + "UTPRTopUpTaxCarryForward", [0] * len(uj))
presence(AT + "Employees", [1] * len(uj))
value(AT + "Employees", [whole(data_jur[k, 0]) for k in uj])
presence(AT + "TangibleAssetValue", [1] * len(uj))
value(AT + "TangibleAssetValue", [whole(data_jur[k, 1]) for k in uj])
value(AT + "UTPRPercentage", [ratio4(utpr_percentage[k]) for k in uj])
value(AT + "UTPRTopUpTaxAttributed", [whole(utpr_amount[k]) for k in uj])
value(AT + "AddCashTaxExpense", [whole(a) for a in cash])
value(AT + "UTPRTopUpTaxCarriedForward", [whole(pos(utpr_amount[k] - a)) for k, a in zip(uj, cash)])
value(UA + "/DocSpec/DocTypeIndic", ["OECD1"] * int(utpr_total > 0))
value(UA + "/DocSpec/DocRefId", ["DOC-UTPRAttribution"] * int(utpr_total > 0))

# ---- Everything not linked above is absent: no rows, presence 0, no value
for r in g.relations:                                                   # parents come before children
    if r["relation_id"] not in P and r["parent_relation_id"]:
        P[r["relation_id"]] = np.zeros((n[r["parent_relation_id"]], 0), int)
        n[r["relation_id"]] = 0
for v in g.vectors:
    k = n[v["relation_id"]]
    if v["kind"] == "presence":
        pi.setdefault(v["vector_id"], np.zeros(k, int))
    else:
        x.setdefault(v["vector_id"], [None] * k)

# Set to absent above without being linked.
for path in [CS + "CE/QUTPR/Art9.3", CS + "CE/QUTPR/AggOwnership", CS + "CE/QUTPR/UPEOwnership",
             CS + "UPE/ExcludedUPE/Art10.3.5", CS + "UPE/OtherUPE/Art10.3.5", CS + "UnreportChangeCorpStr",
             SM + "/JurWithTaxingRights/DiffDomesticTut"]:
    linked.discard(vec_id[(path, "value")])

# ================================================================ Output equations
enum = {}
for e in g.enum_rows:
    enum.setdefault(e["type_id"], set()).add(e["value"])


def tau(type_id, values):
    t = g.type_rows[type_id]

    def ok(v):
        number = isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_))
        if v is None:
            return False
        if t.get("enumerations"):
            return v in enum[type_id]
        if "minLength" in t or "maxLength" in t:
            return isinstance(v, str) and int(t.get("minLength", 0)) <= len(v) <= int(t.get("maxLength", 10 ** 9))
        if "minInclusive" in t:
            if not number:
                return False
            scaled = v * 10 ** int(t["fractionDigits"])
            return float(t["minInclusive"]) <= v <= float(t["maxInclusive"]) and abs(scaled - round(scaled)) < 1e-6
        if t["primitive"] == "boolean":
            return isinstance(v, (bool, np.bool_))
        if t["primitive"] == "integer":
            return number and float(v).is_integer()
        if t["primitive"] in ("date", "dateTime"):
            parse = datetime.date.fromisoformat if t["primitive"] == "date" else datetime.datetime.fromisoformat
            try:
                return isinstance(v, str) and bool(parse(v))
            except ValueError:
                return False
        return isinstance(v, str)

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
    if c["kind"] == "root":
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
    names_of = dict(zip(codes, jurs + ["stateless"]))
    Pm, jn = P[rel_id[JS + "/JurWithTaxingRights"]], x[vec_id[(JS + "/JurWithTaxingRights/JurisdictionName", "value")]]
    sections = [names_of[c] for c in x[vec_id[(JS + "/Jurisdiction", "value")]]]
    print("taxing rights:", {s: [names_of[jn[k]] for k in np.flatnonzero(Pm[i])] for i, s in enumerate(sections)})
    print("equations passed: %d, failed: %d, not evaluated: %d" % (passed, len(failed), skipped))
    for c in failed:
        print("FAILED", c["kind"], c["formula"], "|", c["path"].replace(CS, ""))
