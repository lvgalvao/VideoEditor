"""Retranscreve cada corte e grava as palavras (com índice da frase) em cuts/<nome>.json."""
import json, subprocess, sys
from spec import VARIATIONS, FIX
MODEL = "/Users/lucianogalvao/.cache/whisper/ggml-large-v3-turbo.bin"
NUM = {"Quatro": "4", "quatro": "4"}
for n in VARIATIONS:
    if len(sys.argv) > 1 and n not in sys.argv[1:]:
        continue
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"cuts/{n}.mp4", "-vn", "-ac", "1", "-ar", "16000", f"transcript/{n}.wav"], check=True)
    subprocess.run(["whisper-cli", "-m", MODEL, "-f", f"transcript/{n}.wav", "-l", "pt", "-ojf", "-of", f"transcript/{n}",
                    "-ml", "1", "-sow", "--prompt", "Desafio Claude Code. Claude Code."], check=True, capture_output=True)
    d = json.load(open(f"transcript/{n}.json"))
    cut = json.load(open(f"cuts/{n}.json"))
    segs = cut["segments"]
    w = []
    for s in d["transcription"]:
        t = s["text"].strip()
        if not t:
            continue
        a, b = s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
        if a > cut["speech_end"] - 0.05:  # alucinação do Whisper no final congelado/silencioso
            continue
        pi = max([sg[3] for sg in segs if sg[2] <= a + 0.08] or [0])
        t = FIX.get(t, t)
        t = NUM.get(t.rstrip(","), t.rstrip(",")) + ("," if t.endswith(",") else "")
        w.append([round(a, 2), round(b, 2), t, pi])
    # correções de reconhecimento conhecidas: P9 é sempre "Então, venha participar."
    p9 = [i for i, x in enumerate(w) if cut["segments"] and any(sg[4] == "P9" and sg[3] == x[3] for sg in segs)]
    if p9:
        a, b = w[p9[0]][0], w[p9[-1]][1]
        fixed = [[a, a + 0.35, "Então,"], [a + 0.37, a + 0.6, "venha"], [a + 0.62, b, "participar."]]
        w = w[:p9[0]] + [x + [w[p9[0]][3]] for x in fixed] + w[p9[-1] + 1:]
    for i in range(1, len(w)):
        if w[i][2] == "e" and w[i - 1][2] == "dias":
            w[i][2] = "que"
        if w[i][2] == "em" and i + 1 < len(w) and w[i + 1][2].startswith("2026"):
            w[i][2] = "de"  # a fala é "de 2026"
    cut["words"] = w
    json.dump(cut, open(f"cuts/{n}.json", "w"), ensure_ascii=False, indent=1)
    print(n, " ".join(x[2] for x in w))
