"""Gera comp/index.html a partir de cuts/clean.json: python3 gen.py"""
import json, shutil, os
V = json.load(open("cuts/clean.json"))
W, SEGS, DUR = V["words"], V["segments"], V["duration"]

def pr(i):  # (início, fim) da frase i na timeline de saída
    s = SEGS[i]; return s[2], s[2] + s[1] - s[0]
def word(i, prefix, n=1):
    k = 0
    for w in W:
        if w[3] == i and w[2].lower().strip('.,?').startswith(prefix.lower()):
            k += 1
            if k == n: return w[0]

groups, sfx = [], []
def G(gid, a, b, items=(), instant=False, snd="whoosh"):
    groups.append({"id": gid, "a": round(a, 2), "b": round(b, 2), "items": [[s, round(t, 2), f] for s, t, f in items], "instant": instant})
    if not instant: sfx.append((a, snd))
    for _, t, _ in items: sfx.append((t, "pop"))

cta = word(5, "vai")
G("g-hook", 0, word(0, "mas") - 0.02, instant=True)
G("g-caro", word(0, "mas") - 0.05, pr(0)[1] + 0.05, [["#c1", word(0, "caro"), {"y": 60}]])
G("g-jed", pr(1)[0], pr(1)[1] + 0.1, [["#j1", word(1, "super"), {"y": 30}], ["#j2", word(1, "jev"), {"scale": 2.6}]])
G("g-vs", pr(2)[0], pr(2)[1] + 0.1, [["#v1", word(2, "entregar"), {"x": -160}], ["#v2", word(2, "custar"), {"x": 160}]])
G("g-live", pr(3)[0], word(4, "não") - 0.05, [["#l1", word(3, "agora"), {"y": 30}], ["#l2", word(3, "jornada"), {"y": 30}]])
G("g-emp", word(4, "não"), cta - 0.05, [["#e1", word(4, "empresa"), {"x": -140}], ["#e2", word(5, "mostrando"), {"x": 140}]])
G("g-stamp", word(5, "diferen") - 0.1, DUR, snd="thump")
sfx.append((cta, "ding"))

seg_z = [[round(s[2], 3), 1.0 if i % 2 == 0 else 1.1] for i, s in enumerate(SEGS)]
def zoom_at(t):
    z = 1.0
    for a, s in seg_z:
        if a <= t: z = s
    return z
punches = []
for t, b in [(word(0, "caro"), pr(0)[1]), (word(1, "jev"), pr(1)[1]), (word(5, "diferen"), DUR)]:
    punches.append([t, b, zoom_at(t) + 0.14, zoom_at(b + 0.01)])

chunks, cur = [], []
ws = [w for w in W if w[0] < cta - 0.05]
for i, w in enumerate(ws):
    cur.append(w)
    nxt = ws[i + 1] if i + 1 < len(ws) else None
    joined = nxt and ((w[2].lower() == "claude" and nxt[2].lower().startswith("code"))
                      or (w[2].lower() in ("de", "a", "o", "em", "na", "no", "do", "da", "com", "e", "um", "uma", "por", "tua") and nxt[3] == w[3]))
    if not joined and (w[2][-1] in ".,?!" or len(cur) >= 3 or not nxt or nxt[0] - w[1] > 0.3 or nxt[3] != w[3]):
        chunks.append(cur); cur = []
out = []
for i, c in enumerate(chunks):
    a = c[0][0] - 0.04
    nb = chunks[i + 1][0][0] - 0.04 if i + 1 < len(chunks) else cta
    out.append({"a": round(max(0, a), 3), "b": round(min(nb, c[-1][1] + 0.5), 3), "words": c})

cfg = {"dur": DUR, "segZooms": seg_z, "punches": punches, "groups": groups, "chunks": out, "cta": round(cta, 2)}
vol = {"whoosh": 0.3, "pop": 0.35, "ding": 0.3, "thump": 0.6}
dur = {"whoosh": 0.45, "pop": 0.12, "ding": 0.5, "thump": 0.5}
sfx = sorted((round(t, 2), n) for t, n in sfx if t is not None and t > 0.05)
tags = "\n      ".join(f'<audio id="sfx{i}" src="assets/{n}.wav" data-start="{t}" data-duration="{dur[n]}" data-track-index="{2 + i % 3}" data-volume="{vol[n]}"></audio>' for i, (t, n) in enumerate(sfx))
h = open("comp_template.html").read().replace("__CFG__", json.dumps(cfg, ensure_ascii=False)).replace("__SFX__", tags).replace("__DUR__", str(DUR))
open("comp/index.html", "w").write(h)
if os.path.exists("comp/clip.mp4"): os.remove("comp/clip.mp4")
shutil.copy("cuts/clean.mp4", "comp/clip.mp4")
print("dur", DUR, "cta", cta, [(g["id"], g["a"], g["b"]) for g in groups])
print(" | ".join(" ".join(w[2] for w in c["words"]) for c in out))
