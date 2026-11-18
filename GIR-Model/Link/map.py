"""Write Map.md: every value vector of the Output Model and where the Link Model takes it from.

Usage: python map.py     (run from GIR-Model/Link; needs numpy)
"""
import contextlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    import check as c
g = c.g

# The first matching rule gives the source of a vector.
RULES = [
    (r"/(MessageSpec|FilingInfo|DocSpec)/|@version$|/GeneralSection/RecJurCode$|/UTPRAttribution/RecJurCode$", "Input", "filing data"),
    (r"/AdditionalDataPoint/", "Input", "data points"),
    (r"/ExcludedEntity/(Type|Change)$|/ExcludedUPEStatus$", "Input", "Entity classification"),
    (r"/OwnershipChange/(ChangeDate|PreGlobeStatus|PreOwnership/PreOwnershipPercentage)$|/UnreportChangeCorpStr$", "Input", "changes during the year"),
    (r"/QUTPR/Art9\.3$|/InitialIntActivity/(StartDate|ReferenceJurisdiction/TangibleAssetValue|OtherJurisdiction/TangibleAssetValue)$", "Input", "Article 9.3"),
    (r"/QUTPR/", "Calculation", "UTPR"),
    (r"/InitialIntActivity/RFY", "Aggregate", "Entities and their tangible assets"),
    (r"/EntityOwner/|/IndOwners/|/TaxConsolGroupTIN/", "Input", "owners of the UPE, tax consolidation groups"),
    (r"/RecJurCode$", "Input", "recipients of the section"),
    (r"TIN/|/Name$|ResCountryCode$|/Jurisdiction$|JurisdictionName$|/AltJurisdiction$|/Art10\.3\.5$", "Reference", "Entity, TIN, or jurisdiction"),
    (r"/Rules$", "Reference", "implementation status of the jurisdiction"),
    (r"/GlobeStatus$|/OwnershipType$|/POPE-IPE$|/Art2\.1\.[35]$|TypeofSubGroup$", "Calculation", "classification"),
    (r"/OwnershipPercentage$", "Calculation", "Ownership Interest"),
    (r"/Summary/(SafeHarbour|ETRRange|QDMTTut|GLoBETut|SBIE/\w+)$", "Calculation", "TCSH and Top-up Tax Calculation"),
    (r"/ReportDifference/|/DiffDomesticTut$|/LocalCurrency$", "Input", "differences under domestic law"),
    (r"/TransitionalCbCRSafeHarbour/", "Calculation", "TCSH"),
    (r"UTPRSafeHarbour/", "Input", "Transitional UTPR Safe Harbour"),
    (r"/Deminimis-SimplifiedNMCECalc/Average/|/Non-MaterialCE/Average/", "Aggregate", "average of the years"),
    (r"/Deminimis-SimplifiedNMCECalc/|/Non-MaterialCE/", "Input", "de minimis exclusion, non-material Entities"),
    (r"/Elections?/.*OutstandingBalance$", "Aggregate", "balance of the year"),
    (r"/Election/Art4\.1\.5$", "Input", "election of Top-up Tax Calculation"),
    (r"/Elections?/", "Input", "elections"),
    (r"/CEComputation/(AdjustedFANIL|NetGlobeIncome|AdjustedIncomeTax|AdjustedCoveredTax|AdjustedCoveredTax/DeferTaxAdjustAmt)/Total$"
     r"|ShipIncome/Total$", "Aggregate", "derived amount of the Entity"),
    (r"/CEComputation/", "Input", "Entity amounts and their detail"),
    (r"/OverallComputation/QDMTT/Amount$", "Calculation", "Top-up Tax Calculation"),
    (r"/OverallComputation/QDMTT/", "Input", "QDMTT terms of the jurisdiction"),
    (r"/OverallComputation/(FANIL|AdjustedFANIL|IncomeTaxExpense)$|AggregrateCurrentTax$|/OverallComputation/.*/Adjustments/Amount$"
     r"|/OverallComputation/NetGlobeIncome/IntShippingIncome/|/(PostFilingAdjust/\w+|DeemedDistTax|TransBlendCFC)/Total$|/TotalDDT$"
     r"|/DeferTaxAdjustAmt/(Total|DefTaxAmt|BefRecastAdjust|TotalAdjust|PreRecast|Recast/\w+)$"
     r"|/SubstanceExclusion/(Total|PayrollCost|TangibleAssetValue)$|/NONArt4\.1\.5/AdditionalTopUpTax$",
     "Aggregate", "sum over the group"),
    (r"/NONArt4\.1\.5/|/PostFilingAdjust/|/DeemedDistTax/|/DeferTaxAdjustAmt/|/TransBlendCFC/|/SubstanceExclusion/|AdjustmentItem$",
     "Input", "group detail"),
    (r"/OverallComputation/", "Calculation", "Top-up Tax Calculation"),
    (r"/LowTaxJurisdiction/UTPR/|/Attribution/(UTPRPercentage|UTPRTopUpTaxAttributed|Employees|TangibleAssetValue|UTPRTopUpTaxCarriedForward)$", "Calculation", "UTPR"),
    (r"/Attribution/", "Input", "UTPR carry-forward and cash tax"),
    (r"/LowTaxJurisdiction/LTCE/IIR/ParentEntity/", "Calculation", "IIR"),
    (r"/LowTaxJurisdiction/", "Calculation", "Top-up Tax Calculation"),
]
SECTIONS = ["MessageSpec", "FilingInfo", "GeneralSection", "Summary", "JurisdictionSection", "UTPRAttribution"]


def source(path):
    for pattern, kind, what in RULES:
        if re.search(pattern, path):
            return kind, what
    raise ValueError("no source for " + path)


rows, count, shown = {s: [] for s in SECTIONS}, {}, 0
for v in g.vectors:
    if v["kind"] != "value":
        continue
    assert v["vector_id"] in c.linked, v["path"]
    path = c.plain(v["path"])
    section = next(s for s in SECTIONS if "/" + s in path or path.endswith("@version") and s == "MessageSpec")
    kind, what = source(path)
    used = any(a is not None for a in c.x[v["vector_id"]])
    shown += used
    count[(section, kind)] = count.get((section, kind), 0) + 1
    rows[section].append("| %d | %s | %s | %s | %s |" % (int(v["vector_id"][1:]), path.split("GLOBEBody/")[-1].replace("GLOBE_OECD/", "").replace("_", "\\_"), kind, what, "yes" if used else ""))

kinds = ["Reference", "Calculation", "Aggregate", "Input"]
total = sum(len(r) for r in rows.values())
L = ["# Link Map", "",
     "Every value vector of the [Output Model](../Output/Model.md) and where the [Link Model](Model.md) takes it from. Generated by `map.py`; do not edit.", "",
     "- **Reference:** an Entity, a TIN, or a jurisdiction of the Input Model, selected for the row.",
     "- **Calculation:** a result of the Calculation Model.",
     "- **Aggregate:** a sum, a difference, or an average of atoms of the Input Model.",
     "- **Input:** an atom of the Input Model, passed through.", "",
     "The last column marks the %d vectors that have a value in the example of `check.py`; the other %d are linked but the example has nothing to report in them." % (shown, total - shown), "",
     "| Section | " + " | ".join(kinds) + " | Total |", "| --- |" + " --- |" * (len(kinds) + 1)]
for s in SECTIONS:
    L.append("| %s | %s | %d |" % (s, " | ".join(str(count.get((s, k), 0)) for k in kinds), len(rows[s])))
L.append("| **Total** | %s | %d |" % (" | ".join(str(sum(count.get((s, k), 0) for s in SECTIONS)) for k in kinds), total))
L.append("")
for s in SECTIONS:
    L += ["# " + s, "", "| Vector | Path | Source | From | In example |", "| --- | --- | --- | --- | --- |"] + rows[s] + [""]
with open(os.path.join(HERE, "Map.md"), "w", newline="\n", encoding="utf-8") as fh:
    fh.write("\n".join(L))

if __name__ == "__main__":
    print("\n".join(L[9:20]))
