"""Gera comp/index.html para uma variação: python3 gen.py <nome>"""
import json, sys, shutil, os
name = sys.argv[1]
V = json.load(open(f"cuts/{name}.json"))
sys.path.insert(0, "cuts")
from spec import VARIATIONS
spec = VARIATIONS[name]
W, SEGS, DUR, SPEECH_END = V["words"], V["segments"], V["duration"], V["speech_end"]
phr = spec["phrases"]

def pr(p):  # (inicio, fim) da frase na timeline de saída
    ss = [s for s in SEGS if s[4] == p]
    return (ss[0][2], ss[-1][2] + ss[-1][1] - ss[-1][0]) if ss else None

def word(p, prefix, n=1):  # tempo da n-ésima palavra que começa com prefix dentro da frase p
    if p not in phr: return None
    pi = phr.index(p); k = 0
    for w in W:
        if w[3] == pi and w[2].lower().strip('.,“”?').startswith(prefix.lower()):
            k += 1
            if k == n: return w[0]
    return None

groups, sfx = [], []
def G(gid, a, b, items=(), instant=False, snd="whoosh"):
    if a is None or b is None: return
    items = [[sel, t, fr] for sel, t, fr in items if t is not None and not (instant and t < 0.3)]
    groups.append({"id": gid, "a": round(a, 2), "b": round(b, 2), "items": items, "instant": instant})
    if not instant: sfx.append((a, snd))
    for _, t, _ in items: sfx.append((t, "pop"))

# gancho (visível já no frame 0 = thumbnail)
first_other = None
if spec["hook"]:
    hook_end = word("P2", "desafio") if phr[0] == "P2" else (pr("P6")[1] + 0.05 if phr[0] == "P6" else 2.6)
    G("g-hook", 0, hook_end, instant=True)

if "P2" in phr:
    G("g-desafio", word("P2", "desafio") - 0.1, pr("P2")[1] + 0.05)
if "P3" in phr:
    a = pr("P3")[0]
    G("g-num", a, pr("P3")[1] + 0.05, [["#n1", word("P3", "4") or a, {"x": -80}], ["#n2", word("P3", "4", 2) or a + 0.4, {"x": 80}]], instant=(a < 0.05))
if "P5" in phr:
    a = pr("P4")[0] if "P4" in phr else pr("P5")[0]
    G("g-areas", a, pr("P5")[1] + 0.05, [["#a1", word("P5", "marketing"), {"x": -120}], ["#a2", word("P5", "financeiro"), {"x": 120}], ["#a3", word("P5", "opera"), {"x": -120}]])
if "P6" in phr and phr[0] != "P6":  # na V2 o gancho ocupa essa frase
    a = pr("P6")[0]
    G("g-career", a, pr("P6")[1] + 0.05, [["#k1", a + 0.3, {}], ["#k2", a + 0.8, {}], ["#k3", a + 1.3, {}]])
if "P7" in phr:
    G("g-ask", word("P7", "perguntar") - 0.1, pr("P7")[1] + 0.05)
if "P8" in phr:
    G("g-stamp", word("P8", "não"), pr("P8")[1] + 0.1, snd="thump")
P10 = "P10" if "P10" in phr else ("P10b" if "P10b" in phr else None)
if P10:
    G("g-2026", pr(P10)[0], pr(P10)[1] + 0.05, [["#y1", word(P10, "habilidade"), {"y": 30}], ["#y2", word(P10, "2026"), {"scale": 2.5}]])
if "P11" in phr:
    G("g-ano", pr("P11")[0], pr("P11")[1] + 0.02, [["#an2", word("P11", "valer"), {"scale": 1.6}]])
cta = pr("P12")[0]
sfx.append((cta, "ding"))

# zoom alterna a cada corte; punches
seg_z = []
for i, s in enumerate(SEGS):
    seg_z.append([round(s[2], 3), 1.0 if i % 2 == 0 else 1.1])
def zoom_at(t):
    z = 1.0
    for a, s in seg_z:
        if a <= t: z = s
    return z
punches = []
if "P8" in phr:
    a = word("P8", "não"); punches.append([a, pr("P8")[1], 1.22, zoom_at(pr("P8")[1] + 0.01)])
if P10 and word(P10, "2026"):
    a = word(P10, "2026"); punches.append([a, pr(P10)[1], 1.2, zoom_at(pr(P10)[1] + 0.01)])

# legendas: até 3 palavras, quebra em pontuação/pausa; somem no CTA
chunks, cur = [], []
ws = [w for w in W if w[0] < cta - 0.05]
for i, w in enumerate(ws):
    cur.append(w)
    nxt = ws[i + 1] if i + 1 < len(ws) else None
    joined = nxt and ((w[2].lower() == "claude" and nxt[2].lower().startswith("code"))
                      or (w[2].lower() in ("de", "a", "o", "em", "do", "da", "com", "e", "um", "uma") and nxt[3] == w[3]))
    if not joined and (w[2][-1] in ".,?!" or len(cur) >= 3 or not nxt or nxt[0] - w[1] > 0.3 or nxt[3] != w[3]):
        chunks.append(cur); cur = []
out = []
for i, c in enumerate(chunks):
    a = c[0][0] - 0.04
    nb = chunks[i + 1][0][0] - 0.04 if i + 1 < len(chunks) else cta
    b = min(nb, c[-1][1] + 0.5)
    out.append({"a": round(max(0, a), 3), "b": round(b, 3), "words": c})

cfg = {"dur": DUR, "segZooms": seg_z, "punches": punches, "groups": groups, "chunks": out, "cta": round(cta, 2)}
vol = {"whoosh": 0.3, "pop": 0.35, "ding": 0.3, "thump": 0.6}
dur = {"whoosh": 0.45, "pop": 0.12, "ding": 0.5, "thump": 0.5}
sfx = sorted((round(t, 2), n) for t, n in sfx if t is not None)
tags = "\n      ".join(f'<audio id="sfx{i}" src="assets/{n}.wav" data-start="{t}" data-duration="{dur[n]}" data-track-index="{2 + i % 3}" data-volume="{vol[n]}"></audio>' for i, (t, n) in enumerate(sfx))
h = open("comp_template.html").read()
hook = spec["hook"] or ["", ""]
h = (h.replace("__CFG__", json.dumps(cfg, ensure_ascii=False)).replace("__SFX__", tags).replace("__DUR__", str(DUR))
      .replace("__HOOK1__", hook[0]).replace("__HOOK2__", hook[1]))
open("comp/index.html", "w").write(h)
if os.path.exists("comp/clip.mp4"): os.remove("comp/clip.mp4")
shutil.copy(f"cuts/{name}.mp4", "comp/clip.mp4")
print(name, "dur", DUR, "cta", cta, "groups", [(g["id"], g["a"], g["b"]) for g in groups])
