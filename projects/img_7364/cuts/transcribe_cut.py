"""Retranscreve cuts/clean.mp4 e grava palavras [a, b, texto, idx_frase] em cuts/clean.json."""
import json, subprocess
MODEL = "/Users/lucianogalvao/.cache/whisper/ggml-large-v3-turbo.bin"
FIX = {"Cloud": "Claude", "JED.": "JEV.", "JED": "JEV", "JEV,": "JEV."}
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "cuts/clean.mp4", "-vn", "-ac", "1", "-ar", "16000", "transcript/clean.wav"], check=True)
subprocess.run(["whisper-cli", "-m", MODEL, "-f", "transcript/clean.wav", "-l", "pt", "-ojf", "-of", "transcript/clean",
                "-ml", "1", "-sow", "--prompt", "Claude Code, JEV"], check=True, capture_output=True)
d = json.load(open("transcript/clean.json")); cut = json.load(open("cuts/clean.json")); segs = cut["segments"]
w = []
for s in d["transcription"]:
    t = s["text"].strip()
    if not t: continue
    a, b = s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
    if a > cut["speech_end"] - 0.05: continue  # alucinação no final congelado
    pi = max([sg[3] for sg in segs if sg[2] <= a + 0.08] or [0])
    w.append([round(a, 2), round(b, 2), FIX.get(t, t), pi])
# "aquele caro também é" = reconhecimento de "ele é caro também"
for i in range(len(w) - 3):
    if [x[2] for x in w[i:i + 4]] == ["aquele", "caro", "também", "é."]:
        a0, b0 = w[i][0], w[i + 3][1]; step = (b0 - a0) / 4; pi = w[i][3]
        w[i:i + 4] = [[round(a0 + k * step, 2), round(a0 + (k + 1) * step, 2), x, pi] for k, x in enumerate(["ele", "é", "caro", "também."])]
        break
cut["words"] = w
json.dump(cut, open("cuts/clean.json", "w"), ensure_ascii=False, indent=1)
print(" ".join(f"{x[0]}:{x[2]}" for x in w))
