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
nmce = vec("S")                                          # Non-material Constituent Entities
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
art1035 = np.zeros((N, M), int)                         # Entity x jurisdiction whose IIR it applies under Article 10.3.5

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
status_cols = [ce, zero, zero, zero, pe, main, mope, mos, smoce, ie, zero, zero, jvt, jvsub, nmce, ee, art1035.any(axis=1), zero]
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
    value(bp + "/Art10.3.5", [codes[int(r.argmax())] if r.any() else None for r in S_U @ art1035], mask)
    id_block(bp + "/ID", S_U, mask, excluded=(branch == "ExcludedUPE"))
# An Excluded UPE reports its kind with the GIR60x code that corresponds to GIR100x.
upe_status = [("GIR6" + ee_type[nm][-2:]) if nm in ee_type else None for nm in names]
value(CS + "UPE/(choice1)/ExcludedUPE/ExcludedUPEStatus", pick(S_U, upe_status), ex)

# ---- CE
S_C = rows((ce | jvmember) & ~group_upe)
nC = S_C.shape[0]
relation(CS + "CE", np.ones((1, nC), int))
id_block(CS + "CE/ID", S_C)

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

# ---- Excluded Entities
S_E = rows(ee & ~group_upe)
relation(CS + "ExcludedEntity", np.ones((1, S_E.shape[0]), int))
value(CS + "ExcludedEntity/Name", pick(S_E, names))
value(CS + "ExcludedEntity/Type", pick(S_E, [ee_type.get(nm) for nm in names]))
value(CS + "ExcludedEntity/Change", [False] * S_E.shape[0])

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
R_JW, Q_JW = R, Q                                                # rows of JurWithTaxingRights: section, collecting jurisdiction
relation(JS + "/JurWithTaxingRights", R)
value(JS + "/JurWithTaxingRights/JurisdictionName", pick(Q, codes))
value(JS + "/DocSpec/DocTypeIndic", ["OECD1"] * nJ)              # Input: filing metadata
value(JS + "/DocSpec/DocRefId", ["DOC-%s" % c for c in pick(S_J, codes)])

# ================================================================ Input: amounts and filing data (example)
def amounts(**kw):
    return np.array([kw.get(nm, 0) for nm in names], float)


fanil = amounts(UPE=1000, A=780, B=640, PE=150, C=615, IE1=300, ST=100, JV=400, JS1=200, JS2=100,
                P1=200, P2=300, P3=100, IE2=100, S=200, IE3=100)       # financial accounting net income
income_tax = amounts(UPE=250, A=40, B=51, PE=15, C=105, JV=20, JS1=10, JS2=12, P1=10, P3=20, S=10)
emp, tan = amounts(B=50, PE=10), amounts(B=1000, PE=200)
tcsh_rev, tcsh_pbt, tcsh_tax, tcsh_sbie = 5 * fanil, fanil.copy(), income_tax.copy(), amounts(A=100)
tcsh_elected_jur = {"US"}
qdmtt_of = {"B": 40, "S": 20}                                          # QDMTT of the group of each named Entity
r_min, tau, d_R, d_P = 0.15, 0.15, 10_000_000, 1_000_000
filing = {"transmitting": "US", "receiving": "US", "message_ref": "US2025-GIR-0001", "period_start": "2025-01-01",
          "period_end": "2025-12-31", "timestamp": "2026-06-30T00:00:00", "filing_ce": "UPE", "role": "GIR401",
          "cfs": "GIR501", "fas": "US GAAP", "currency": "EUR", "name_mne": "Example Group",
          "version": "1.0", "sending_entity": "TIN-UPE", "contact": "tax@example.com", "warning": "Example data",
          "additional_info": "Return of the example group of the Calculation Model"}
utpr_cash = {"XQ": 145}                                                # additional cash tax expense by jurisdiction

# ================================================================ Input: detail (example)
# Every table is a list of rows. A row names the Entity it belongs to; a row of a group-level
# table names one Entity of the Full Calculation Group it belongs to.
INC = ["GIR20%02d" % k for k in range(1, 27)]                          # items of the GloBE Income adjustments
TAX = ["GIR24%02d" % k for k in range(1, 18)]                          # items of the current tax adjustments
DEF = ["GIR25%02d" % k for k in range(1, 17)]                          # items of the deferred tax adjustments
FIN = ["GIR27%02d" % k for k in range(1, 21)]                          # items of the group's Adjusted Covered Taxes


def items(codes_, entries):
    """Entity-by-item matrix from {(Entity, item): amount}."""
    A = np.zeros((N, len(codes_)))
    for (nm, code), a in entries.items():
        A[ix[nm], codes_.index(code)] = a
    return A


def onehot(keys, index):
    """Incidence matrix with one row per key and one column per element of index; None gives a zero row."""
    T = np.zeros((len(keys), len(index)), int)
    for r, k in enumerate(keys):
        if k is not None:
            T[r, list(index).index(k)] = 1
    return T


def col(table, key):
    return [r.get(key) for r in table]


def num(table, key):
    return np.array([r.get(key) or 0 for r in table], float)


# Accounting income to GloBE Income
transfers = [dict(src="C", dst="PE", basis="GIR1701", amount=50)]       # allocations between Main Entity, PE and FTE
cross_border = [dict(entity="A", other="B", basis="GIR1801", additions=20),
                dict(entity="B", other="A", basis="GIR1801", reductions=20)]
upe_adj, upe_adj_owner = [], []                                         # Articles 7.1 and 7.2: none in the example
inc_add = items(INC, {("B", "GIR2007"): 10})                            # additions by item
inc_red = items(INC, {("B", "GIR2002"): 30})                            # reductions by item
SHIP = ["GIR21%02d" % k for k in range(1, 7)]
ship_cat = items(SHIP, {("C", "GIR2101"): 1, ("C", "GIR2103"): 1}).astype(int)
anc_cat = {"C": "GIR2201"}
ship_rev, ship_cost, anc_rev, anc_cost = amounts(C=100), amounts(C=60), amounts(C=30), amounts(C=5)
ship_payroll, ship_tangible, ship_tax = amounts(C=10), amounts(C=200), amounts()
# Income tax expense to Adjusted Covered Taxes
tax_transfers = [dict(src="C", dst="PE", bases=["GIR2301"], amount=5)]  # cross-allocation of Covered Taxes
tax_add = items(TAX, {("JS2", "GIR2414"): 3})
tax_red = items(TAX, {("B", "GIR2405"): 4})
defer_expense = amounts(B=12)
def_add, def_red = items(DEF, {("B", "GIR2504"): 5}), items(DEF, {("B", "GIR2501"): 2})
def_higher, def_lower = items(DEF, {("B", "GIR2504"): -3}), items(DEF, {("B", "GIR2501"): 1})
# Substance-based Income Exclusion
payroll, tangible, rho_p, rho_t = amounts(A=250), amounts(A=1000), 0.096, 0.076
sbie_pe = [dict(group="C", owner="XQ", payroll_total=400, payroll_alloc=100, tangible_total=800, tangible_alloc=200)]
sbie_fte = []
# Prior Fiscal Years
actt_prior = amounts(C=8)
recalc = [dict(group="C", year="2024-12-31", articles=["GIR2601"],
               previous=(480, 72, 0.15, 480, 0.0, 0), recalculated=(480, 64, 0.1333, 480, 0.0167, 8))]
post_dta = [dict(group="P2", year="2023-12-31", amount=6), dict(group="P2", year="2024-12-31", amount=4)]
post_refund = [dict(group="P2", year="2024-12-31", amount=3)]
ddt = [dict(group="JS2", year="2025-12-31", start=3, d0=0, d1=0, d2=0, d3=0, end=3)]
ddt_terms = {"JS2": (0, 0, 0.0)}                                        # reduction, incremental Top-up Tax, ratio
# Deferred tax of a group
def_diff, def_globe, loss_dta = {"B": 2}, {"B": 2}, {}
recapture = {"B": (0, 0, 9, 0, 9, 0, 0, 0, 0)}
transition = [dict(group="B", year="2024-12-31", dtl_start=50, dtl_recast=40, dta_total=30, dta_start=30, dta_recast=0,
                   dta_excluded=0, disposal=dict(jur="XR", net=4, carrying=100, tax_paid=6, dtadtl=3), alt="XR")]
cfc = [dict(group="A", jur="XQ", top="B", amount=7)]
# De minimis exclusion, non-material Constituent Entities
dm_basis, dm_now = {"JS2": "GIR2901"}, {"JS2": (900, 900)}              # revenue and GloBE revenue of the year
dm_prior = [dict(group="JS2", year="2024-12-31", revenue=800, globe_revenue=800, income=90, fanil=90),
            dict(group="JS2", year="2023-12-31", revenue=700, globe_revenue=700, income=80, fanil=80)]
nm_rev = {"S": (1000, 900, 800)}                                        # year, first and second preceding year
nm_simplified = {"S": 5}
# Elections
FIVE_E = ["Art1.5.3", "Art3.2.1b", "Art3.2.1c", "Art4.4.7", "Art4.5.6"]
FIVE_G = ["Art3.2.2", "Art3.2.5", "Art3.2.8", "NoDefTaxAllocation", "Art4.5", "Art3.2.1.c"]
ent_elect = {("B", "Art3.2.1b"): (True, "2024-01-01", None), ("B", "Art4.4.7"): (True, "2025-01-01", None),
             ("P1", "Art3.2.1c"): (False, "2020-01-01", "2025-01-01")}
ent_flag = {("S", "SimplCalculations"): True, ("P2", "Art3.2.1"): True}
art634 = [dict(entity="P3", trigger="2025-12-31", option="ii")]
tax_groups = [dict(tin="TCG-XL-1", issued="XL", type="GIR3001", members=["JV", "JS1"])]
art75, art76 = [], []                                                   # Investment Entity elections: none
other_fas = {"JS1": "Local GAAP"}
grp_elect = {("B", "Art3.2.2"): (True, "2024-01-01", None), ("A", "Art3.2.1.c"): (True, "2024-01-01", None),
             ("P2", "Art3.2.5"): (True, "2024-01-01", None), ("JV", "Art3.2.8"): (False, "2020-01-01", "2025-01-01"),
             ("S", "Art4.5"): (True, "2025-01-01", None), ("A", "NoDefTaxAllocation"): (True, "2025-01-01", None)}
grp_flag = {("B", "Art4.6.1"): True, ("JV", "Art3.2.6"): True, ("ST", "Art5.3.1"): True, ("P2", "SimplifiedReporting"): True}
art321c = {"A": (100, 20, 5)}                                           # opening balance, additions, reductions
ente_elected_of = set()                                                 # groups that elect the Article 4.1.5 carry-forward
# QDMTT terms by jurisdiction
qdmtt_terms = {"XQ": dict(fas="US GAAP", sbie=True, demin=True, currency="EUR",
                          election=(True, "2024-01-01", None, "GIR3101")),
               "XD": dict(fas="US GAAP", sbie=True, demin=True, currency="EUR", min_rate=0.16,
                          blending="Blended by Entity")}
# UTPR
art_93, utpr_sh, cit_rate = False, True, 0.21                           # Article 9.3; Transitional UTPR Safe Harbour
initial = dict(start="2025-01-01", ref="US", tangible={"US": 5000, "XQ": 1200})   # reported only under Article 9.3
# Corporate structure
changes = [dict(entity="C", date="2025-07-01", status=["GIR701"], owners={"B": 1.0})]
unreported_change = False
# Differences under domestic law, currencies, data points, corrections
diff = [dict(section="XR", jur="XQ", etr=0.12, agg_current_tax=20, qrtc_expense=0, other_credits=0, defer_expense=0,
             net_globe=400, sbie=0, add_tut=0, tut=12, elections="No differences in elections", qrtc_income=0, ente=0,
             transition=False)]
local_currency = {"XD": "CHF"}
dp_general = [dict(description="Employees of the group", amount=1200),
              dict(description="Share of income from royalties", percentage=0.25, text="Estimate", boolean=True)]
dp_summary = [dict(group="A", description="Number of sites", amount=3, text="At the end of the year", boolean=False)]
dp_section = [dict(section="XN", description="Occupancy", amount=40, percentage=0.8)]
dp_utpr = [dict(description="UTPR in force for the whole year", amount=12, percentage=1.0, text="Months", boolean=True)]
corr_ref = {}                                                           # corrected document by section: a first filing

# ================================================================ Input: amounts the Calculation Model takes
tr_from, tr_to = onehot(col(transfers, "src"), names), onehot(col(transfers, "dst"), names)
adj_fanil = fanil + (tr_to - tr_from).T @ num(transfers, "amount")
cb_T, ua_T = onehot(col(cross_border, "entity"), names), onehot(col(upe_adj, "entity"), names)
for basis, item in (("GIR1801", "GIR2013"), ("GIR1802", "GIR2017")):    # items that have their own table
    pick_basis = np.array([r["basis"] == basis for r in cross_border], float)
    inc_add[:, INC.index(item)] = cb_T.T @ (pick_basis * num(cross_border, "additions"))
    inc_red[:, INC.index(item)] = cb_T.T @ (pick_basis * num(cross_border, "reductions"))
for bases, item in ((("GIR1901", "GIR1902", "GIR1903", "GIR1904"), "GIR2022"),
                    (("GIR1905", "GIR1906", "GIR1907", "GIR1908", "GIR1909", "GIR1910"), "GIR2023")):
    inc_red[:, INC.index(item)] = ua_T.T @ (np.array([r["basis"] in bases for r in upe_adj], float) * num(upe_adj, "amount"))
ship_income, anc_income = ship_rev - ship_cost, anc_rev - anc_cost
inc_red[:, INC.index("GIR2025")] = np.maximum(ship_income + anc_income, 0)
inc_add[:, INC.index("GIR2025")] = np.maximum(-(ship_income + anc_income), 0)
globe_income = adj_fanil + (inc_add - inc_red).sum(axis=1)
tt_from, tt_to = onehot(col(tax_transfers, "src"), names), onehot(col(tax_transfers, "dst"), names)
adj_income_tax = income_tax + (tt_to - tt_from).T @ num(tax_transfers, "amount")
defer_total = defer_expense + (def_add - def_red + def_higher + def_lower).sum(axis=1)
tax_add[:, TAX.index("GIR2416")] = np.maximum(defer_total, 0)
tax_red[:, TAX.index("GIR2416")] = np.maximum(-defer_total, 0)
act = adj_income_tax + (tax_add - tax_red).sum(axis=1)
sbie = rho_p * payroll + rho_t * tangible

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


def grp(values, default=0.0):
    """Group vector from {Entity of the group: value}."""
    out = [default] * MC
    for nm, v in values.items():
        out[int(EG[ix[nm]].argmax())] = v
    return out


ente_elected = np.array(grp({nm: True for nm in ente_elected_of}, False))
g_ship, g_anc = EG.T @ ship_income, EG.T @ anc_income
ship_cap = 0.5 * pos(g_ship)
ship_excess = pos(g_anc - ship_cap)                                    # Qualified Ancillary income above the 50% cap
income_adj, act_adj = ship_excess, np.array(grp(loss_dta))
g_income, g_tax = EG.T @ globe_income + income_adj, EG.T @ act + act_adj
g_pos, g_expected = g_income > 0, r_min * g_income
ente_used = g_pos * np.minimum(ente_prior, pos(g_tax))
etr = g_pos * (pos(g_tax) - ente_used) * dag(pos(g_income))
tt_percent = g_pos * pos(r_min - etr)
excess = pos(g_income - EG.T @ sbie)
art415 = ~g_pos & (g_tax < 0) & (g_tax < g_expected)
actt415 = (art415 & ~ente_elected) * (g_expected - g_tax)
ente_generated = g_pos * pos(-g_tax) + (art415 & ente_elected) * (g_expected - g_tax)
ente_next = ente_prior - ente_used + ente_generated
regular = tt_percent * excess
gross = regular + actt415 + EG.T @ actt_prior
tt_group = ~safe * pos(gross - qdmtt)
theta = tt_group * dag(gross)
key = pos(globe_income)
key415 = ((act < 0) & (act < r_min * globe_income)) * (r_min * globe_income - act)
alloc = lambda k: np.diag(k) @ EG @ np.diag(dag(EG.T @ k))
tt_entt = alloc(key) @ (theta * regular) + alloc(key415) @ (theta * actt415) + (EG @ theta) * actt_prior
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
R_SW, Q_SW = R, Q                                                        # rows: unit, collecting jurisdiction
relation(SM + "/JurWithTaxingRights", R)
presence(SM + "/JurWithTaxingRights/JurisdictionName", [1] * R.shape[1])
value(SM + "/JurWithTaxingRights/JurisdictionName", pick(Q, codes))
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
ETR = JS + "/GLoBETax/ETR"
relation(ETR, u_section)
presence(ETR + "/SubGroup", etr_sub)
inline_tin(ETR + "/SubGroup/TIN", tops, etr_sub)
E = np.array([[kc in u["etr_kinds"] for kc in kind_codes] for u in units], int)
R, Q = cells(E)
relation(ETR + "/SubGroup/TypeofSubGroup", R)
value(ETR + "/SubGroup/TypeofSubGroup", pick(Q, ["GIR16" + kc for kc in kind_codes]))
EX = ETR + "/ETRStatus/ETRException"
presence(EX + "/TransitionalCbCRSafeHarbour", ~full)
for name, v in (("Revenue", t_r), ("Profit", t_p), ("IncomeTax", t_t)):
    value(EX + "/TransitionalCbCRSafeHarbour/" + name, [whole(a) for a in v[ti_]], ~full)
EC = ETR + "/ETRStatus/ETRComputation"
OC = EC + "/OverallComputation"
presence(EC, full)
presence(OC, full)
for name, v in (("FANIL", EG.T @ fanil), ("AdjustedFANIL", EG.T @ adj_fanil), ("NetGlobeIncome/Total", g_income),
                ("IncomeTaxExpense", EG.T @ income_tax), ("ExcessProfits", excess), ("TopUpTax", tt_group),
                ("ExcessNegTaxExpense/PriorYearBalance", ente_prior), ("ExcessNegTaxExpense/GeneratedInRFY", ente_generated),
                ("ExcessNegTaxExpense/UtilizedInRFY", ente_used), ("ExcessNegTaxExpense/Remaining", ente_next)):
    value(OC + "/" + name, [whole(a) for a in v[gi_]], full)
value(OC + "/ETRRate", [ratio4(a) for a in etr[gi_]], full)
value(OC + "/TopUpTaxPercentage", [ratio4(a) for a in tt_percent[gi_]], full)
presence(OC + "/AdjustedCoveredTax", full)
value(OC + "/AdjustedCoveredTax/Total", [whole(a) for a in (g_tax + ente_generated - ente_used)[gi_]], full)
value(OC + "/AdjustedCoveredTax/AggregrateCurrentTax", [whole(a) for a in (EG.T @ adj_income_tax)[gi_]], full)
has_q = full & (u_qdmtt > 0)
presence(OC + "/QDMTT", has_q)
value(OC + "/QDMTT/Amount", [whole(a) for a in u_qdmtt], has_q)
has_415 = full & art415[gi_]
presence(OC + "/AdditionalTopUpTax/Art4.1.5", has_415)
for name, v in (("AdjustedCoveredTax", g_tax), ("GlobeLoss", g_income), ("ExpectedAdjustedCoveredTax", g_expected),
                ("AdditionalTopUpTax", actt415)):
    value(OC + "/AdditionalTopUpTax/Art4.1.5/" + name, [whole(a) for a in v[gi_]], has_415)

# CEComputation: one row per Entity of each fully calculated unit
CM = np.array([u["members"] * (not u["tcsh"]) for u in units], int)      # units x Entities
R, Q = cells(CM)
Q_CE = Q                                                                # rows of CEComputation x Entities
CC = EC + "/CEComputation"
relation(CC, R)
ents = [int(e) for e in np.argmax(Q, axis=1)]
inline_tin(CC + "/TIN", ents)
for name, v in (("AdjustedFANIL/Total", adj_fanil), ("AdjustedFANIL/FANIL", fanil), ("NetGlobeIncome/Total", globe_income),
                ("AdjustedIncomeTax/Total", adj_income_tax), ("AdjustedIncomeTax/IncomeTax", income_tax),
                ("AdjustedCoveredTax/Total", act), ("AdjustedCoveredTax/DeferTaxAdjustAmt/Total", defer_total),
                ("AdjustedCoveredTax/DeferTaxAdjustAmt/DeferTaxExpense", defer_expense)):
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
upe_sec = (S_J @ (EJx.T @ upe)) > 0                                     # section of the UPE jurisdiction
sh_sec = upe_sec & utpr_sh & (sec_tt > 0)                               # Transitional UTPR Safe Harbour in place of the calculation
presence(LT + "/UTPR", (sec_utpr > 0) | sh_sec)
presence(LT + "/UTPR/UTPRSafeHarbour", sh_sec)
value(LT + "/UTPR/UTPRSafeHarbour/CITRate", [cit_rate] * nJ, sh_sec)
presence(LT + "/UTPR/UTPRCalculation", (sec_utpr > 0) & ~sh_sec)
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

# ================================================================ Link: optional detail
# A detail table is attached to the rows of an Output relation by cells(H x T^T): H relates the
# rows of the parent relation to Entities, groups or sections, and T does the same for the table.
sec_names = jurs + ["X5"]


def attach(path, H, T, table):
    """Relation with one row per (parent row, table row) that share an owner; returns R and the table rows."""
    R, Qt = cells(np.asarray(H) @ np.asarray(T).T)
    relation(path, R)
    return R, Qt, pick(Qt, table)


def by_unit(values):
    """A group vector, one entry per unit; None for a unit that is not a Full Calculation Group."""
    return [values[gi_[k]] if full[k] else None for k in range(nU)]


def opt(v, f=lambda a: a):
    return None if v is None else f(v)


def nz(v):
    """An amount that is reported only where it is not zero."""
    return None if v is None or whole(v) == 0 else whole(v)


def ext_tin(path, tins):
    """TIN of something that is not an Entity of the Input Model: a dict(tin, issued, type) or None."""
    k = len(tins)
    value(path + "/#text", [t["tin"] if t else None for t in tins])
    presence(path + "/@issuedBy", [bool(t and t.get("issued")) for t in tins])
    value(path + "/@issuedBy", [iso[t["issued"]] if t and t.get("issued") else None for t in tins])
    presence(path + "/@unknown", [0] * k)
    value(path + "/@unknown", [None] * k)
    presence(path + "/@TypeOfTIN", [bool(t and t.get("type")) for t in tins])
    value(path + "/@TypeOfTIN", [t["type"] if t and t.get("type") else None for t in tins])


def code_of(e):
    """Jurisdiction code of an Entity; X5 for a Stateless Entity."""
    return codes[int(EJx[e].argmax())]


def five_year(path, triples):
    """Status, election year and revocation year of a five-year election; None where not made."""
    value(path + "/Status", [opt(t, lambda a: a[0]) for t in triples])
    value(path + "/ElectionYear", [opt(t, lambda a: a[1]) for t in triples])
    value(path + "/RevocationYear", [opt(t, lambda a: a[2]) for t in triples])


def data_points(path, R, table):
    relation(path, R)
    for name in ("Description", "Amount", "Percentage", "Text", "Boolean"):
        value(path + "/" + name, col(table, name.lower()))


def signed_items(path, H, add, red, codes_):
    """One row per item and sign: the additions and, as negative amounts, the reductions."""
    A = np.hstack([H @ add, -(H @ red)])
    R, Qi = cells(np.round(A) != 0)
    relation(path, R)
    value(path + "/Amount", [whole(a) for a in A[np.round(A) != 0]])
    value(path + "/AdjustmentItem", pick(Qi, list(codes_) + list(codes_)))
    return R


def entity_items(path, add, red, codes_):
    """One row per Entity and item, with the addition and the reduction as up to two amounts."""
    a, r = Q_CE @ add, Q_CE @ red
    mask = (np.round(a) != 0) | (np.round(r) != 0)
    R, Qi = cells(mask)
    relation(path, R)
    value(path + "/AdjustmentItem", pick(Qi, codes_))
    two = np.stack([np.round(a[mask]) != 0, np.round(r[mask]) != 0], axis=1).astype(int).reshape(-1, 2)
    R2, _ = cells(two)
    relation(path + "/Amount", R2)
    value(path + "/Amount", [whole(v) for v in np.stack([a[mask], -r[mask]], axis=1).reshape(-1, 2)[two > 0]])
    return mask


def transfer_rows(path, table, T_from, T_to, optional):
    """A transfer between two Entities, reported for each of them: an addition for one, a reduction for the other."""
    R, Qt = cells(Q_CE @ (T_to + T_from).T)
    relation(path, R)
    t = [int(q.argmax()) for q in Qt]
    e = [ents[int(j)] for j in R.argmax(axis=0)] if R.shape[1] else []
    into = [bool(T_to[k, i]) for k, i in zip(t, e)]
    other = [int((T_from if d else T_to)[k].argmax()) for k, d in zip(t, into)]
    inline_tin(path + "/OtherTIN", other)
    value(path + "/ResCountryCode", [code_of(o) for o in other])
    amount = [whole(table[k]["amount"]) for k in t]
    zero_ = None if optional else 0
    value(path + "/Additions", [a if d else zero_ for a, d in zip(amount, into)])
    value(path + "/Reductions", [zero_ if d else a for a, d in zip(amount, into)])
    return Qt


# ---- Header and corrections
value("GLOBE_OECD/@version", [filing.get("version")])
value(MS + "SendingEntityIN", [filing.get("sending_entity")])
value(MS + "Warning", [filing.get("warning")])
value(MS + "Contact", [filing.get("contact")])
value(FI + "AdditionalInfo", [filing.get("additional_info")])
value(FI + "DocSpec/CorrDocRefId", [corr_ref.get("FilingInfo")])
value(BODY + "/GeneralSection/DocSpec/CorrDocRefId", [corr_ref.get("GeneralSection")])
value(SM + "/DocSpec/CorrDocRefId", [corr_ref.get("Summary-%d" % (k + 1)) for k in range(nU)])
value(JS + "/DocSpec/CorrDocRefId", pick(S_J, [corr_ref.get(j) for j in sec_names]))
value(UA + "/DocSpec/CorrDocRefId", [corr_ref.get("UTPRAttribution")] * int(utpr_total > 0))

# ---- Additional data points
Hg = np.zeros((nU, MC), int)                                            # units x Full Calculation Groups
Hg[np.flatnonzero(full), gi_[full]] = 1


def group_of(table):
    """Table rows x groups, for a table whose rows name an Entity of their group."""
    return onehot(col(table, "group"), names) @ EG


data_points(BODY + "/GeneralSection/AdditionalDataPoint", np.ones((1, len(dp_general)), int), dp_general)
R, _, t = attach(SM + "/AdditionalDataPoint", Hg, group_of(dp_summary), dp_summary)
data_points(SM + "/AdditionalDataPoint", R, t)
R, _, t = attach(JS + "/AdditionalDataPoint", S_J, onehot([iso.get(j, j) for j in col(dp_section, "section")], codes), dp_section)
data_points(JS + "/AdditionalDataPoint", R, t)
data_points(UA + "/AdditionalDataPoint", np.ones((int(utpr_total > 0), len(dp_utpr) * int(utpr_total > 0)), int),
            dp_utpr if utpr_total > 0 else [])

# ---- Corporate structure: changes during the year
PRE = ["GIR7%02d" % k for k in range(1, 22)]
OC_ = CS + "CE/OwnershipChange"
_, Qc, ch = attach(OC_, S_C, onehot(col(changes, "entity"), names), changes)
value(OC_ + "/ChangeDate", col(ch, "date"))
R, Qs = cells(np.array([[code in r["status"] for code in PRE] for r in ch], int).reshape(len(ch), len(PRE)))
relation(OC_ + "/PreGlobeStatus", R)
value(OC_ + "/PreGlobeStatus", pick(Qs, PRE))
W_pre = np.array([[r["owners"].get(o, 0) for o in names + ["excluded", "non-group"]] for r in ch], float).reshape(len(ch), N + 2)
R, Qo = cells(W_pre > 0)
relation(OC_ + "/PreOwnership", R)
value(OC_ + "/PreOwnership/OwnershipType", pick(Qo, owner_type))
value(OC_ + "/PreOwnership/PreOwnershipPercentage", [ratio4(v) for v in W_pre[W_pre > 0]])
tin_block(OC_ + "/PreOwnership/TIN", Qo, pick(Qo, tin + ["NOTIN", "NOTIN"]), pick(Qo, tin_issued + [None, None]),
          pick(Qo, tin_type + ["GIR3004", "GIR3004"]), [j >= N for j in np.argmax(Qo, axis=1)] if Qo.shape[0] else [])
value(CS + "UnreportChangeCorpStr", [unreported_change])

# ---- Corporate structure: QUTPR
q_any = (S_C @ (member & bool(utpr_jur.any()))) > 0                     # some jurisdiction applies a Qualified UTPR
upe_charges = Qpay[upe].sum(axis=0) > 0                                 # a UPE applies a Qualified IIR to the Entity
q_share = q_any & (not art_93) & ((S_C @ ~upe_charges) > 0)
presence(CS + "CE/QUTPR", q_any)
value(CS + "CE/QUTPR/Art9.3", [art_93] * nC, q_any)
value(CS + "CE/QUTPR/AggOwnership", [ratio4(v) for v in S_C @ (charged.T @ one)], q_share)
value(CS + "CE/QUTPR/UPEOwnership", [bool(v <= 1e-12) for v in S_C @ (residual.T @ one)], q_share)

# ---- Jurisdictions with taxing rights: subgroups, differences under domestic law
Unit = np.array([u["members"] for u in units], int).T                   # Entities x units
payer = (Iir_payable | np.diag(self_payable)).astype(int)
unit_rights = ((EJ.T @ ((payer @ Unit) > 0)) > 0) | ((np.diag(jv("qdmtt")) @ EJ.T @ Unit) > 0)   # jurisdictions x units
R, Qu = cells((R_JW.T @ u_section) * (Q_JW @ unit_rights) * sub[None, :])
SG = JS + "/JurWithTaxingRights/Subgroup"
relation(SG, R)
inline_tin(SG + "/TIN", pick(Qu, tops))
R, Qk2 = cells(Qu @ K)
relation(SG + "/TypeofSubGroup", R)
value(SG + "/TypeofSubGroup", pick(Qk2, ["GIR11" + kc for kc in kind_codes]))

D_sec, D_jur = onehot([iso.get(j, j) for j in col(diff, "section")], codes), onehot(col(diff, "jur"), jurs)
Z = (R_JW.T @ S_J @ D_sec.T) * (Q_JW @ D_jur.T)                         # rows of JurWithTaxingRights x differences
d = [diff[int(z.argmax())] if z.any() else {} for z in Z]
RD = JS + "/JurWithTaxingRights/ReportDifference/"
for name, key, f in (("ETRDifference", "etr", ratio4), ("AdjCoveredTaxDifference/AggCurrentTaxExpense", "agg_current_tax", whole),
                     ("AdjCoveredTaxDifference/QRTCExpense", "qrtc_expense", whole),
                     ("AdjCoveredTaxDifference/OtherTaxCredits", "other_credits", whole),
                     ("AdjCoveredTaxDifference/DeferTaxExpense", "defer_expense", whole), ("NetGLoBEDifference", "net_globe", whole),
                     ("SBIEDifference", "sbie", whole), ("AddCurrentTuTDifference", "add_tut", whole), ("TuTDifference", "tut", whole),
                     ("ElectionsDifference", "elections", str), ("QRTCIncome", "qrtc_income", whole),
                     ("ExcessNegTaxCarryForw", "ente", whole), ("TransitionDifference", "transition", bool)):
    value(RD + name, [opt(r.get(key), f) for r in d])
Z = (R_SW.T @ u_section.T @ S_J @ D_sec.T) * (Q_SW @ D_jur.T)           # the same for the rows of the Summary
value(SM + "/JurWithTaxingRights/DiffDomesticTut",
      [opt(diff[int(z.argmax())].get("tut") if z.any() else None, lambda a: band(a, "15")) for z in Z])
value(JS + "/LocalCurrency", pick(S_J, [local_currency.get(j) for j in jurs] + [None]))

# ---- Summary: effect of the SBIE
g_sbie = EG.T @ sbie
show = has_rights & full
value(SM + "/SBIE/NotApplicable", [bool(v) for v in (g_sbie == 0)[gi_]], show)
value(SM + "/SBIE/NoTut", [bool(v) for v in ((g_sbie > 0) & (tt_percent > 0) & (excess == 0))[gi_]], show)

# ---- ETR: exceptions
DM = EX + "/Deminimis-SimplifiedNMCECalc"
dm_b = grp(dm_basis, None)
value(DM + "/Basis", by_unit(dm_b))
now = grp(dm_now, None)
g_fanil = EG.T @ fanil
fd = [dict(group=k, year=filing["period_end"], revenue=now[k][0], globe_revenue=now[k][1], income=g_income[k], fanil=g_fanil[k])
      for k in range(MC) if dm_b[k] is not None]                        # the Reporting Fiscal Year comes from the return itself
fd += [dict(r, group=int(EG[ix[r["group"]]].argmax())) for r in dm_prior]
R, _, t = attach(DM + "/FinancialData", Hg, onehot(col(fd, "group"), range(MC)), fd)
value(DM + "/FinancialData/Year", col(t, "year"))
for name, key in (("Revenue", "revenue"), ("GlobeRevenue", "globe_revenue"), ("NetGlobeIncome", "income"), ("FANIL", "fanil")):
    value(DM + "/FinancialData/" + name, [whole(v) for v in col(t, key)])
    value(DM + "/Average/" + name, [whole(a / c_) if c_ else None for a, c_ in zip(R @ num(t, key), R.sum(axis=1))])
sh_unit = ((u_section.T @ upe_sec) > 0) & utpr_sh
value(EX + "/UTPRSafeHarbour/CITRate", [cit_rate] * nU, sh_unit)

# ---- ETR: elections of a group
EL = ETR + "/Election"
flags = dict(grp_flag, **{(names[g_first[k]], "Art4.1.5"): True for k in np.flatnonzero(ente_elected)})
for name in ("Art3.2.6", "Art4.1.5", "Art4.6.1", "Art5.3.1", "SimplifiedReporting"):
    value(EL + "/" + name, by_unit(grp({nm: v for (nm, e), v in flags.items() if e == name}, None)))
for name in FIVE_G:
    five_year(EL + "/" + name, by_unit(grp({nm: v for (nm, e), v in grp_elect.items() if e == name}, None)))
bal = by_unit(grp(art321c, None))
for k, name in enumerate(("QualOwnerIntentBalance", "Additions", "Reductions")):
    value(EL + "/Art3.2.1.c/" + name, [opt(b, lambda a: whole(a[k])) for b in bal])
value(EL + "/Art3.2.1.c/OutstandingBalance", [opt(b, lambda a: whole(a[0] + a[1] - a[2])) for b in bal])

# ---- CEComputation: accounting income to GloBE Income
per_ce = lambda v: [v[e] for e in ents]
AD = CC + "/AdjustedFANIL/Adjustment"
Qt = transfer_rows(AD + "/MainEntityPEandFTE", transfers, tr_from, tr_to, optional=False)
value(AD + "/MainEntityPEandFTE/Basis", pick(Qt, col(transfers, "basis")))
_, _, t = attach(AD + "/CrossBorderAdjustments", Q_CE, cb_T, cross_border)
value(AD + "/CrossBorderAdjustments/Basis", col(t, "basis"))
inline_tin(AD + "/CrossBorderAdjustments/OtherTIN", [ix[r["other"]] for r in t])
value(AD + "/CrossBorderAdjustments/ResCountryCode", [code_of(ix[r["other"]]) for r in t])
value(AD + "/CrossBorderAdjustments/Additions", [opt(r.get("additions"), whole) for r in t])
value(AD + "/CrossBorderAdjustments/Reductions", [opt(r.get("reductions"), whole) for r in t])
_, Qa, t = attach(AD + "/UPEAdjustments", Q_CE, ua_T, upe_adj)
value(AD + "/UPEAdjustments/Basis", col(t, "basis"))
value(AD + "/UPEAdjustments/Reductions/Amount", [opt(r.get("amount"), whole) for r in t])
value(AD + "/UPEAdjustments/Reductions/Exception", [True if r.get("exception") else None for r in t])
OW = AD + "/UPEAdjustments/IdentificationOfOwners"
_, _, o = attach(OW, Qa, onehot(col(upe_adj_owner, "adjustment"), range(len(upe_adj))), upe_adj_owner)
value(OW + "/OwnershipPercentage", [ratio4(r["percentage"]) for r in o])
value(OW + "/IndOwners/NumOfOwners", col(o, "individuals"))
value(OW + "/IndOwners/ResCountryCode", [opt(r.get("jur"), iso.get) if r.get("individuals") else None for r in o])
value(OW + "/IndOwners/TaxRate", [opt(r.get("rate"), ratio4) if r.get("individuals") else None for r in o])
ext_tin(OW + "/EntityOwner/TIN", col(o, "owner"))
value(OW + "/EntityOwner/ResCountryCode", [iso[r["jur"]] if r.get("owner") else None for r in o])
value(OW + "/EntityOwner/TaxRate", [opt(r.get("rate"), ratio4) if r.get("owner") else None for r in o])
value(OW + "/EntityOwner/ExTypeOfEntity", [r.get("excluded_type") if r.get("owner") else None for r in o])
entity_items(CC + "/NetGlobeIncome/Adjustments", inc_add, inc_red, INC)

# International shipping
has_ship = ship_cat.any(axis=1)
m_ship = per_ce(has_ship)
SH = CC + "/NetGlobeIncome/IntShippingIncome"
for name, v in (("InternationalShipIncome/Total", ship_income), ("InternationalShipIncome/Revenue", ship_rev),
                ("InternationalShipIncome/Costs", ship_cost), ("QualifiedAncShipIncome/Total", anc_income),
                ("QualifiedAncShipIncome/Revenue", anc_rev), ("QualifiedAncShipIncome/Costs", anc_cost),
                ("SubstanceExclusion/PayrollCosts", ship_payroll), ("SubstanceExclusion/TangibleAssets", ship_tangible),
                ("CoveredTaxes", ship_tax)):
    value(SH + "/" + name, [whole(a) for a in per_ce(v)], m_ship)
value(SH + "/QualifiedAncShipIncome/Category", per_ce([anc_cat.get(nm) for nm in names]), m_ship)
R, Qs = cells(Q_CE @ ship_cat)
relation(SH + "/InternationalShipIncome/Category", R)
value(SH + "/InternationalShipIncome/Category", pick(Qs, SHIP))

# ---- CEComputation: income tax expense to Adjusted Covered Taxes
CA = CC + "/AdjustedIncomeTax/CrossAllocation"
Qt = transfer_rows(CA, tax_transfers, tt_from, tt_to, optional=True)
BAS = ["GIR23%02d" % k for k in range(1, 10)]
R, Qb = cells(Qt @ np.array([[b in r["bases"] for b in BAS] for r in tax_transfers], int).reshape(len(tax_transfers), len(BAS)))
relation(CA + "/Basis", R)
value(CA + "/Basis", pick(Qb, BAS))
entity_items(CC + "/AdjustedCoveredTax/Adjustments", tax_add, tax_red, TAX)
DA = CC + "/AdjustedCoveredTax/DeferTaxAdjustAmt/Adjustment"
mask = entity_items(DA, def_add, def_red, DEF)
value(DA + "/Recast/Higher", [nz(v) for v in (Q_CE @ def_higher)[mask]])
value(DA + "/Recast/Lower", [nz(v) for v in (Q_CE @ def_lower)[mask]])

# ---- CEComputation: elections of an Entity
CE_EL = CC + "/Elections"
for name in FIVE_E:
    five_year(CE_EL + "/" + name, per_ce([ent_elect.get((nm, name)) for nm in names]))
for name in ("SimplCalculations", "Art3.2.1"):
    value(CE_EL + "/" + name, per_ce([ent_flag.get((nm, name)) for nm in names]))
_, _, t = attach(CE_EL + "/Art6.3.4", Q_CE, onehot(col(art634, "entity"), names), art634)
value(CE_EL + "/Art6.3.4/FYTriggerEvent", col(t, "trigger"))
value(CE_EL + "/Art6.3.4/Inclusion/Art6.3.4.c.i", [True if r["option"] == "i" else None for r in t])
value(CE_EL + "/Art6.3.4/Inclusion/Art6.3.4.c.ii", [True if r["option"] == "ii" else None for r in t])
TG = np.array([[nm in r["members"] for r in tax_groups] for nm in names], int).reshape(N, len(tax_groups))   # Entities x tax groups
ext_tin(CE_EL + "/AggregatedReporting/TaxConsolGroupTIN", [tax_groups[int(r.argmax())] if r.any() else None for r in Q_CE @ TG])
R, Qm = cells(Q_CE @ TG @ TG.T)
relation(CE_EL + "/AggregatedReporting/EntityTIN", R)
inline_tin(CE_EL + "/AggregatedReporting/EntityTIN", [int(e) for e in np.argmax(Qm, axis=1)])
_, Q75, t = attach(CE_EL + "/Art7.5", Q_CE, onehot(col(art75, "entity"), names), art75)
five_year(CE_EL + "/Art7.5", [(r["status"], r.get("year"), r.get("revoked")) for r in t])
R, Qm = cells(Q75 @ np.array([[nm in r["owners"] for nm in names] for r in art75], int).reshape(len(art75), N))
relation(CE_EL + "/Art7.5/CEOwnerTIN", R)
inline_tin(CE_EL + "/Art7.5/CEOwnerTIN", [int(e) for e in np.argmax(Qm, axis=1)])
_, _, t = attach(CE_EL + "/Art7.6", Q_CE, onehot(col(art76, "entity"), names), art76)
five_year(CE_EL + "/Art7.6", [(r["status"], r["year"], r.get("revoked")) for r in t])
value(CE_EL + "/Art7.6/ActualDeemedDist", [whole(r["distribution"]) for r in t])
value(CE_EL + "/Art7.6/LocalCreditableTaxGross", [whole(r["credit"]) for r in t])
value(CE_EL + "/Art7.6/ShareOfUndistNetGlobeInc", [ratio4(r["share"]) for r in t])
inline_tin(CE_EL + "/Art7.6/InvestmentEntityTIN", [ix[r["investment_entity"]] for r in t])
value(CC + "/OtherFAS", per_ce([other_fas.get(nm) for nm in names]))

# ---- OverallComputation: GloBE Income
signed_items(OC + "/NetGlobeIncome/Adjustments", Hg, EG.T @ inc_add, EG.T @ inc_red, INC)
m = full & ((EG.T @ has_ship) > 0)[gi_]
OS = OC + "/NetGlobeIncome/IntShippingIncome"
for name, v in (("Total", g_ship + g_anc - ship_excess), ("TotalIntShipIncome", g_ship), ("FiftyPercentCap", ship_cap),
                ("TotalQualifiedAncIncome", g_anc)):
    value(OS + "/" + name, [whole(a) for a in v[gi_]], m)
value(OS + "/ExcessOfCap", [nz(a) for a in ship_excess[gi_]], m)

# ---- OverallComputation: Adjusted Covered Taxes
ACT = OC + "/AdjustedCoveredTax"
to_fin = [0] + list(range(2, 18))                                       # GIR24xx to GIR27xx: GIR2702 is for groups only
fin_add, fin_red = np.zeros((MC, len(FIN))), np.zeros((MC, len(FIN)))
fin_add[:, to_fin], fin_red[:, to_fin] = EG.T @ tax_add, EG.T @ tax_red
fin_add[:, FIN.index("GIR2702")], fin_red[:, FIN.index("GIR2702")] = pos(act_adj), pos(-act_adj)
fin_add[:, FIN.index("GIR2719")], fin_red[:, FIN.index("GIR2720")] = ente_generated, ente_used
signed_items(ACT + "/Adjustments", Hg, fin_add, fin_red, FIN)

PF = ACT + "/PostFilingAdjust"
has_pf = np.zeros(nU, bool)
totals = {}
for name, table in (("DeferTaxAsset", post_dta), ("CoveredTaxRefund", post_refund)):
    R, _, t = attach(PF + "/" + name + "/AmountAttributed", Hg, group_of(table), table)
    value(PF + "/" + name + "/AmountAttributed/Year", col(t, "year"))
    value(PF + "/" + name + "/AmountAttributed/Amount", [whole(a) for a in col(t, "amount")])
    totals[name], has_pf = R @ num(t, "amount"), has_pf | (R.sum(axis=1) > 0)
for name in totals:
    value(PF + "/" + name + "/Total", [whole(a) for a in totals[name]], has_pf)

DD = ACT + "/DeemedDistTax"
R, _, t = attach(DD + "/Election/Recapture", Hg, group_of(ddt), ddt)
value(DD + "/Election/Recapture/Year", col(t, "year"))
for name, key in (("StartAmount", "start"), ("DDTYear-0", "d0"), ("DDTYear-1", "d1"), ("DDTYear-2", "d2"), ("DDTYear-3", "d3"),
                  ("EndAmount", "end")):
    value(DD + "/Election/Recapture/" + name, [whole(a) for a in col(t, key)])
value(DD + "/Election/Recapture/TotalDDT", [whole(r["d0"] + r["d1"] + r["d2"] + r["d3"]) for r in t])
has_el = R.sum(axis=1) > 0
terms = by_unit(grp(ddt_terms, (0, 0, 0.0)))
for k, (name, f) in enumerate((("Reduction", whole), ("IncrementalTopUpTax", whole), ("Ratio", ratio4))):
    value(DD + "/Election/" + name, [opt(a, lambda b: f(b[k])) for a in terms], has_el)
g_ddt = EG.T @ (tax_add - tax_red)[:, TAX.index("GIR2414")]
value(DD + "/Total", [whole(a) for a in g_ddt[gi_]], has_el | (full & (np.round(g_ddt[gi_]) != 0)))

DF = ACT + "/DeferTaxAdjustAmt"
g_bef, g_adj = EG.T @ defer_expense, EG.T @ (def_add - def_red).sum(axis=1)
g_hi, g_lo = EG.T @ def_higher.sum(axis=1), EG.T @ def_lower.sum(axis=1)
g_diff, g_glo = np.array(grp(def_diff)), np.array(grp(def_globe))
R_adj = signed_items(DF + "/Adjustments", Hg, EG.T @ def_add, EG.T @ def_red, DEF)
rec = by_unit(grp(recapture, (0,) * 9))
row_unit = [int(j) for j in R_adj.argmax(axis=0)] if R_adj.shape[1] else []
for k, name in enumerate(("DTLRFYMinus5", "RecapDTLRFYMinus5", "DTLRFY", "AggregateDTL/ReportingFiscalYear/AmountPreTransition",
                          "AggregateDTL/ReportingFiscalYear/AmountOutBalance", "AggregateDTL/ReportingFiscalYear/AmountUnjustified",
                          "AggregateDTL/PriorFiscalYear/AmountPreTransition", "AggregateDTL/PriorFiscalYear/AmountOutBalance",
                          "AggregateDTL/PriorFiscalYear/AmountUnjustified")):
    value(DF + "/Adjustments/RecaptureDeferred/" + name, [whole(rec[u][k]) for u in row_unit])
R_tr, _, t = attach(DF + "/Transition", Hg, group_of(transition), transition)
value(DF + "/Transition/Year", col(t, "year"))
for name, key in (("DeferredTaxLiabilityStart", "dtl_start"), ("DeferredTaxLiabilityRecast", "dtl_recast"),
                  ("DeferredTaxAssets/Total", "dta_total"), ("DeferredTaxAssets/DeferredTaxAssetStart", "dta_start"),
                  ("DeferredTaxAssets/DeferredTaxAssetRecast", "dta_recast"),
                  ("DeferredTaxAssets/DeferredTaxAssetExcluded", "dta_excluded")):
    value(DF + "/Transition/" + name, [opt(r.get(key), whole) for r in t])
dis = [r.get("disposal") or {} for r in t]
value(DF + "/Transition/Disposal/ResCountryCode", [opt(r.get("jur"), lambda j: iso.get(j, j)) for r in dis])
for name, key in (("NetDTADTL", "net"), ("CarryingValue", "carrying"), ("TaxPaid", "tax_paid"), ("DTADTL", "dtadtl")):
    value(DF + "/Transition/Disposal/" + name, [opt(r.get(key), whole) for r in dis])
value(DF + "/Transition/AltJurisdiction", [opt(r.get("alt"), iso.get) for r in t])
used = (EG.T @ (np.abs(defer_expense) + np.abs(def_add) .sum(axis=1) + np.abs(def_red).sum(axis=1))) + np.abs(g_diff) + np.abs(g_glo)
has_def = full & ((used[gi_] > 0) | (R_tr.sum(axis=1) > 0))
for name, v in (("Total", g_bef + g_adj + g_hi + g_lo), ("DefTaxAmt", g_bef + g_diff - g_glo), ("DiffCarryValue", g_diff),
                ("GLoBEValue", g_glo), ("BefRecastAdjust", g_bef), ("TotalAdjust", g_adj), ("PreRecast", g_bef + g_adj)):
    value(DF + "/" + name, [whole(a) for a in v[gi_]], has_def)
value(DF + "/Recast/Higher", [nz(a) for a in g_hi[gi_]], has_def)
value(DF + "/Recast/Lower", [nz(a) for a in g_lo[gi_]], has_def)

CF = ACT + "/TransBlendCFC"
R, _, t = attach(CF + "/CFCJur", Hg, group_of(cfc), cfc)
value(CF + "/CFCJur/Jurisdiction", [iso[r["jur"]] for r in t])
inline_tin(CF + "/CFCJur/Allocation/SubGroupTIN", [opt(r.get("top"), ix.get) for r in t])
value(CF + "/CFCJur/Allocation/AggAllocTax", [whole(r["amount"]) for r in t])
value(CF + "/Total", [whole(a) for a in R @ num(t, "amount")], R.sum(axis=1) > 0)

# ---- OverallComputation: Substance-based Income Exclusion
SE = OC + "/SubstanceExclusion"
has_se = full & ((EG.T @ (payroll + tangible))[gi_] > 0)
for name, table in (("PEAllocation", sbie_pe), ("FTEAllocation", sbie_fte)):
    R, _, t = attach(SE + "/" + name, Hg, group_of(table), table)
    own = col(t, "owner")
    value(SE + "/" + name + "/JurOfOwners/ResCountryCode", [iso.get(o, o) if o not in (None, "UPE") else None for o in own])
    value(SE + "/" + name + "/JurOfOwners/UPE", [True if o == "UPE" else None for o in own])
    value(SE + "/" + name + "/JurOfOwners/NotApplicable", [True if o is None else None for o in own])
    for leaf, key in (("PayrollCost/Total", "payroll_total"), ("PayrollCost/Allocation", "payroll_alloc"),
                      ("TangibleAssetValue/Total", "tangible_total"), ("TangibleAssetValue/Allocation", "tangible_alloc")):
        value(SE + "/" + name + "/" + leaf, [whole(a) for a in col(t, key)])
    has_se = has_se | (R.sum(axis=1) > 0)
for name, v in (("Total", g_sbie), ("PayrollCost", EG.T @ payroll), ("TangibleAssetValue", EG.T @ tangible)):
    value(SE + "/" + name, [whole(a) for a in v[gi_]], has_se)
value(SE + "/PayrollMarkUp", [rho_p] * nU, has_se)
value(SE + "/TangibleAssetMarkup", [rho_t] * nU, has_se)

# ---- OverallComputation: Additional Current Top-up Tax of prior Fiscal Years, QDMTT
NA = OC + "/AdditionalTopUpTax/NONArt4.1.5"
R, Qr, t = attach(NA, Hg, group_of(recalc), recalc)
ART = ["GIR26%02d" % k for k in range(1, 7)]
Ra, Qa = cells(np.array([[a in r["articles"] for a in ART] for r in t], int).reshape(len(t), len(ART)))
relation(NA + "/Articles", Ra)
value(NA + "/Articles", pick(Qa, ART))
value(NA + "/Year", col(t, "year"))
for part, key in (("Previous", "previous"), ("Recalculated", "recalculated")):
    for k, (name, f) in enumerate((("NetGlobeIncome", whole), ("AdjustedCoveredTax", whole), ("ETRRate", ratio4),
                                   ("ExcessProfits", whole), ("TopUpTaxPercentage", ratio4), ("TopUpTax", whole))):
        value(NA + "/" + part + "/" + name, [f(r[key][k]) for r in t])
value(NA + "/AdditionalTopUpTax", [whole(r["recalculated"][5] - r["previous"][5]) for r in t])
QD = OC + "/QDMTT"
qd = [qdmtt_terms.get(j, {}) for j in pick(u_section.T @ S_J, jurs + [None])]
value(QD + "/FAS", col(qd, "fas"), has_q)
value(QD + "/SBIEAvailable", col(qd, "sbie"), has_q)
value(QD + "/DeMinAvailable", col(qd, "demin"), has_q)
value(QD + "/Currency", col(qd, "currency"), has_q)
value(QD + "/MinRate", [opt(r.get("min_rate"), ratio4) for r in qd], has_q)
value(QD + "/BasisforBlending", col(qd, "blending"), has_q)
five_year(QD + "/CurrencyElection", [r.get("election") if q_ else None for r, q_ in zip(qd, has_q)])
value(QD + "/CurrencyElection/Currency", [r["election"][3] if q_ and r.get("election") else None for r, q_ in zip(qd, has_q)])

# ---- Non-material Constituent Entities
NM = EC + "/Non-MaterialCE"
R, Qn = cells(CM @ np.diag(nmce.astype(int)))
relation(NM, R)
rev3 = [nm_rev.get(names[int(e)], (0, None, None)) for e in np.argmax(Qn, axis=1)] if Qn.shape[0] else []
value(NM + "/RFY/TotalRevenue", [whole(r[0]) for r in rev3])
value(NM + "/RFY/AggregateSimplified", [opt(nm_simplified.get(names[int(e)]), whole) for e in np.argmax(Qn, axis=1)] if Qn.shape[0] else [])
value(NM + "/RFY-1/TotalRevenue", [opt(r[1], whole) for r in rev3])
value(NM + "/RFY-2/TotalRevenue", [opt(r[2], whole) for r in rev3])
value(NM + "/Average/TotalRevenue", [whole(sum(a for a in r if a is not None) / sum(a is not None for a in r)) for r in rev3])
id_block(NM + "/ID", Qn)

# ---- Initial phase of international activity (Article 9.3), reported in every section
IA = JS + "/GLoBETax/InitialIntActivity"
in_93 = np.full(nJ, bool(art_93))
first_year = initial["start"] == filing["period_start"]
others = [j for j in initial["tangible"] if j != initial["ref"]]
tan_now = EJx.T @ ((ce & ~ie) * tan)                                    # tangible assets by jurisdiction; X5 last
value(IA + "/StartDate", [initial["start"]] * nJ, in_93)
value(IA + "/ReferenceJurisdiction/ResCountryCode", [iso[initial["ref"]]] * nJ, in_93)
value(IA + "/ReferenceJurisdiction/TangibleAssetValue", [whole(initial["tangible"][initial["ref"]])] * nJ, in_93)
R = np.kron(np.diag(in_93.astype(int))[:, np.flatnonzero(in_93)], np.ones((1, len(others)), int))
relation(IA + "/OtherJurisdiction", R)
value(IA + "/OtherJurisdiction/TangibleAssetValue", [whole(initial["tangible"][j]) for j in others] * int(in_93.sum()))
relation(IA + "/OtherJurisdiction/ResCountryCode", np.eye(R.shape[1], dtype=int))
value(IA + "/OtherJurisdiction/ResCountryCode", [iso[j] for j in others] * int(in_93.sum()))
report_now = in_93 & (not first_year)
value(IA + "/RFYNumberOfJurisdictions", [int(((EJ.T @ (ce & ~ie)) > 0).sum())] * nJ, report_now)
value(IA + "/RFYSumTangibleAssetValue", [whole(tan_now.sum() - tan_now[jurs.index(initial["ref"])])] * nJ, report_now)

# ---- Presence: an optional node is present where it has content, and absent elsewhere
for r in g.relations:                                                   # parents come before children
    if r["relation_id"] not in P and r["parent_relation_id"]:
        P[r["relation_id"]] = np.zeros((n[r["parent_relation_id"]], 0), int)
        n[r["relation_id"]] = 0
for v in g.vectors:
    if v["kind"] == "value":
        x.setdefault(v["vector_id"], [None] * n[v["relation_id"]])
unlinked = [v["path"] for v in g.vectors if v["kind"] == "value" and v["vector_id"] not in linked]
node_of = {nd["node_id"]: nd for nd in g.nodes}
content = {}                                                            # node -> rows of its relation in which it has content
for nd in reversed(g.nodes):                                            # children come after their parents
    here = content.setdefault(nd["node_id"], np.zeros(n[nd["relation_id"]], bool))
    if nd["child_relation_id"]:                                         # a repeated element: present where it has rows
        here |= P[nd["child_relation_id"]].sum(axis=1) > 0
    elif nd["vector_id"]:
        here |= np.array([a is not None for a in x[nd["vector_id"]]], bool)
    parent = node_of.get(nd["parent_node_id"])
    if parent is not None and not parent["child_relation_id"]:
        content.setdefault(parent["node_id"], np.zeros(n[parent["relation_id"]], bool))
        content[parent["node_id"]] |= here
presence_of = {v["path"]: v["vector_id"] for v in g.vectors if v["kind"] == "presence"}
for nd in g.nodes:
    vid = presence_of.get(nd["path"])
    if vid and vid not in pi:
        pi[vid] = content[nd["node_id"]].astype(int)

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
