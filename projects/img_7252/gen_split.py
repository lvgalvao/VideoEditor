"""Gera comp_split/index.html (tela dividida) para uma variação: python3 gen_split.py <nome>"""
import json, sys, shutil, os
name = sys.argv[1]
V = json.load(open(f"cuts/{name}.json"))
sys.path.insert(0, "cuts")
from spec import VARIATIONS
spec = VARIATIONS[name]
W, SEGS, DUR = V["words"], V["segments"], V["duration"]
phr = spec["phrases"]

def pr(p):
    ss = [s for s in SEGS if s[4] == p]
    return (ss[0][2], ss[-1][2] + ss[-1][1] - ss[-1][0]) if ss else None

def word(p, prefix, n=1):
    if p not in phr: return None
    pi = phr.index(p); k = 0
    for w in W:
        if w[3] == pi and w[2].lower().strip('.,“”?').startswith(prefix.lower()):
            k += 1
            if k == n: return w[0]
    return None

cta = pr("P12")[0]
starts, keys, sfx = {}, {}, []
if spec["hook"]:
    starts["hook"] = 0.0
if "P2" in phr:
    starts["desafio"] = word("P2", "desafio") - 0.15
if "P3" in phr:
    starts["num"] = pr("P3")[0]
    keys["num1"] = word("P3", "4") or pr("P3")[0]
    keys["num2"] = word("P3", "4", 2) or keys["num1"] + 0.4
    sfx += [(keys["num1"], "pop"), (keys["num2"], "pop")]
if "P5" in phr:
    starts["areas"] = pr("P4")[0] if "P4" in phr else pr("P5")[0]
    keys.update(ar1=word("P5", "marketing"), ar2=word("P5", "financeiro"), ar3=word("P5", "opera"))
    sfx += [(keys["ar1"], "pop"), (keys["ar2"], "pop"), (keys["ar3"], "pop")]
if "P6" in phr and phr[0] != "P6":
    starts["career"] = pr("P6")[0]
    sfx += [(starts["career"] + 0.25 + i * 0.45, "pop") for i in range(3)]
if "P7" in phr:
    starts["ask"] = pr("P7")[0]
    keys["ask"] = word("P7", "perguntar") or pr("P7")[0] + 0.8
    sfx.append((keys["ask"], "pop"))
if "P8" in phr:
    starts["stamp"] = pr("P8")[0]
    keys["stamp"] = word("P8", "opcional") or word("P8", "não")
    sfx.append((keys["stamp"], "thump"))
P10 = "P10" if "P10" in phr else ("P10b" if "P10b" in phr else None)
if P10:
    starts["2026"] = pr(P10)[0]
    keys["y2026"] = word(P10, "2026")
    sfx.append((keys["y2026"], "ding"))
if "P11" in phr:
    starts["ano"] = pr("P11")[0]
    keys["valer"] = word("P11", "valer")
    sfx.append((keys["valer"], "pop"))
starts["cta"] = cta
sfx.append((cta, "ding"))

# cenas encadeadas: cada uma vai até a próxima começar
order = sorted(starts.items(), key=lambda kv: kv[1])
scenes = {}
for i, (sid, a) in enumerate(order):
    b = order[i + 1][1] if i + 1 < len(order) else DUR
    scenes[sid] = {"a": round(a, 2), "b": round(b, 2), "instant": a < 0.05}
    if a >= 0.05: sfx.append((a, "whoosh"))

# câmera: alterna zoom a cada corte; punch em "opcional" e "2026"
seg_z = [[round(s[2], 3), 1.0 if i % 2 == 0 else 1.1] for i, s in enumerate(SEGS)]
def zoom_at(t):
    z = 1.0
    for a, s in seg_z:
        if a <= t: z = s
    return z
punches = []
if "P8" in phr:
    a = word("P8", "não"); punches.append([a, pr("P8")[1], 1.2, zoom_at(pr("P8")[1] + 0.01)])
if P10 and keys.get("y2026"):
    punches.append([keys["y2026"], pr(P10)[1], 1.18, zoom_at(pr(P10)[1] + 0.01)])

# legendas (mesma regra do gen.py)
SOFT = ("de", "a", "o", "em", "do", "da", "com", "e", "um", "uma")
chunks, cur = [], []
ws = [w for w in W if w[0] < cta - 0.05]
for i, w in enumerate(ws):
    cur.append(w)
    nxt = ws[i + 1] if i + 1 < len(ws) else None
    joined = nxt and ((w[2].lower() == "claude" and nxt[2].lower().startswith("code")) or (w[2].lower() in SOFT and nxt[3] == w[3]))
    if not joined and (w[2][-1] in ".,?!" or len(cur) >= 3 or not nxt or nxt[0] - w[1] > 0.3 or nxt[3] != w[3]):
        chunks.append(cur); cur = []
out = []
for i, c in enumerate(chunks):
    a = c[0][0] - 0.04
    nb = chunks[i + 1][0][0] - 0.04 if i + 1 < len(chunks) else cta
    out.append({"a": round(max(0, a), 3), "b": round(min(nb, c[-1][1] + 0.5), 3), "words": c})

cfg = {"dur": DUR, "segZooms": seg_z, "punches": punches, "scenes": scenes, "keys": keys, "chunks": out}
vol = {"whoosh": 0.3, "pop": 0.35, "ding": 0.3, "thump": 0.6}
dur = {"whoosh": 0.45, "pop": 0.12, "ding": 0.5, "thump": 0.5}
sfx = sorted((round(t, 2), n) for t, n in sfx if t is not None)
tags = "\n      ".join(f'<audio id="sfx{i}" src="assets/{n}.wav" data-start="{t}" data-duration="{dur[n]}" data-track-index="{2 + i % 3}" data-volume="{vol[n]}"></audio>' for i, (t, n) in enumerate(sfx))
hook = spec["hook"] or ["", ""]
h = (open("split_template.html").read().replace("__CFG__", json.dumps(cfg, ensure_ascii=False)).replace("__SFX__", tags)
     .replace("__DUR__", str(DUR)).replace("__HOOK1__", hook[0]).replace("__HOOK2__", hook[1]))
open("comp_split/index.html", "w").write(h)
if os.path.exists("comp_split/clip.mp4"): os.remove("comp_split/clip.mp4")
shutil.copy(f"cuts/{name}.mp4", "comp_split/clip.mp4")
print(name, "scenes", [(k, v["a"], v["b"]) for k, v in scenes.items()])
