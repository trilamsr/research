"""Search 3 — logged completeness search for the sim2real correlation census.

Runs a fixed battery of arXiv API metadata queries (title/abstract), window
2024-01-01 .. 2026-07-21, categories cs.RO/cs.LG/cs.CV. Prints, per query:
the verbatim query string and every hit (id, title). Then dedupes and splits
hits into KNOWN (already in survey/excluded lists) vs NEW (need screening).
"""
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
CATS = "(cat:cs.RO OR cat:cs.LG OR cat:cs.CV)"
DATE = "submittedDate:[202401010000 TO 202607212359]"

QUERIES = [
    'abs:"sim-to-real correlation"',
    'abs:"real-to-sim correlation"',
    'abs:"sim-and-real correlation" OR abs:"sim-real correlation"',
    'abs:"correlation" AND abs:"policy evaluation" AND (abs:"simulation" OR abs:"simulator")',
    'abs:"MMRV" OR abs:"maximum rank violation" OR abs:"rank violation"',
    'abs:"real2sim" AND (abs:"evaluation" OR abs:"benchmark")',
    'abs:"correlation" AND abs:"real-world" AND abs:"robot" AND (abs:"simulated evaluation" OR abs:"simulation-based evaluation" OR abs:"evaluation in simulation")',
    '(abs:"Pearson" OR abs:"Spearman") AND abs:"sim-to-real" AND abs:"policy"',
    'abs:"world model" AND abs:"policy evaluation" AND abs:"correlation"',
]

KNOWN_SURVEY = {
    "2511.04665": "real2sim-eval", "2607.01060": "RoboWorld", "2604.15805": "Digital Cousins",
    "2405.05941": "SIMPLER", "2606.28276": "SimFoundry", "2506.00613": "WorldGym",
    "2607.06699": "RoboSnap", "2512.19562": "REALM", "2512.16881": "PolaRiS",
    "2606.18610": "SC3-Eval", "2505.19017": "WorldEval", "2606.10366": "A Practical Recipe",
    "2510.16240": "Cosmos-Surg-dVRK", "2512.10675": "Gemini/Veo", "2602.06949": "DreamDojo",
    "2604.22152": "dWorldEval", "2606.13672": "WEAVER", "2603.09030": "PlayWorld",
    "2509.17430": "EmbodiedSplat", "2602.11337": "MolmoSpaces", "2606.18960": "Mem-World",
    "2605.27759": "Colosseum V2",
}
KNOWN_EXCLUDED = {
    "2510.20813": "GSWorld", "2603.08546": "Interactive World Sim", "2510.10637": "RoboSimGS",
    "2606.04233": "Benchmarking audit", "2503.24278": "AutoEval", "2607.02642": "GigaWorld-1",
    "1912.06321": "Kadian 2020 (pre-window)",
}

def run(qs):
    url = ("http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": f"({qs}) AND {CATS} AND {DATE}",
        "start": 0, "max_results": 100, "sortBy": "submittedDate", "sortOrder": "descending"}))
    with urllib.request.urlopen(url, timeout=60) as r:
        tree = ET.fromstring(r.read())
    out = []
    for e in tree.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1]
        base = aid.split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        out.append((base, aid, title, summ))
    return out

all_hits = {}
for i, q in enumerate(QUERIES, 1):
    hits = run(q)
    print(f"\n=== Q{i}: {q}")
    print(f"    hits: {len(hits)}")
    for base, aid, title, _ in hits:
        tag = KNOWN_SURVEY.get(base) or KNOWN_EXCLUDED.get(base) or "NEW"
        print(f"    {aid:16s} [{tag}] {title[:95]}")
        all_hits.setdefault(base, (aid, title, _, []))[3].append(f"Q{i}")
    time.sleep(3)

print("\n\n=== SUMMARY ===")
survey_found = sorted(b for b in all_hits if b in KNOWN_SURVEY)
excl_found = sorted(b for b in all_hits if b in KNOWN_EXCLUDED)
new = sorted(b for b in all_hits if b not in KNOWN_SURVEY and b not in KNOWN_EXCLUDED)
print(f"unique hits: {len(all_hits)}")
print(f"survey papers recalled: {len(survey_found)}/22 -> {[KNOWN_SURVEY[b] for b in survey_found]}")
print(f"known-excluded recalled: {[KNOWN_EXCLUDED[b] for b in excl_found]}")
print(f"\nNEW candidates needing screening: {len(new)}")
for b in new:
    aid, title, summ, qs = all_hits[b]
    print(f"\n--- {aid}  (queries: {','.join(qs)})\n    {title}\n    {summ[:600]}")
