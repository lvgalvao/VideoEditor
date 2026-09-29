"""Renderiza o corte de cada variação a partir de source/sdr.mp4 e gera o mapa de tempos."""
import json, subprocess, sys
from spec import PHRASES, VARIATIONS, FIX

TAIL = 1.2  # congela o último frame para o CTA respirar
WORDS = json.load(open("transcript/words_src.json"))

for name, v in VARIATIONS.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]:
        continue
    segs = []  # [src_a, src_b, out_a, phrase_idx]
    t = 0.0
    for pi, p in enumerate(v["phrases"]):
        for a, b in PHRASES[p]:
            segs.append([a, b, round(t, 3), pi, p])
            t += b - a
    dur = t
    words = []
    for a, b, o, pi, p in segs:
        for ws, we, txt in WORDS:
            if a - 0.02 <= ws < b - 0.05:
                words.append([round(o + ws - a, 3), round(o + min(we, b) - a, 3), FIX.get(txt, txt), pi])
    json.dump({"segments": segs, "words": words, "duration": round(dur + TAIL, 3), "speech_end": round(dur, 3)},
              open(f"cuts/{name}.json", "w"), ensure_ascii=False, indent=1)

    f, c = [], ""
    for i, (a, b, *_ ) in enumerate(segs):
        d = b - a
        f.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
        f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.02:.3f}:d=0.02[a{i}]")
        c += f"[v{i}][a{i}]"
    f.append(f"{c}concat=n={len(segs)}:v=1:a=1[vc][ac]")
    f.append(f"[vc]tpad=stop_mode=clone:stop_duration={TAIL}[v]")
    f.append(f"[ac]apad=pad_dur={TAIL}[a]")
    open(f"cuts/{name}.filter.txt", "w").write(";\n".join(f))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "source/sdr.mp4", "-filter_complex_script", f"cuts/{name}.filter.txt",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-r", "30",
                    "-c:a", "aac", "-b:a", "256k", f"cuts/{name}.mp4"], check=True)
    print(name, round(dur + TAIL, 2), "s")
