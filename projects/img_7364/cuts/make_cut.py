"""Corta pausas do source/sdr.mp4 -> cuts/clean.mp4 (+ congela o final p/ CTA) e grava cuts/clean.json."""
import json, subprocess
SEGS = [  # tempos no source
    [0.00, 3.70, "P1"],   # Claude Code é bom, isso todo mundo já sabe, mas ele é caro também
    [3.92, 6.92, "P2"],   # Mas tem um modelo que chegou, super novo, que é o JED
    [7.22, 11.00, "P3"],  # E ele está dando o que falar... entregar mais e custar menos
    [11.33, 14.12, "P4"], # A gente vai ter uma live, vai começar agora na Jornada de Dados
    [14.25, 19.38, "P5"], # Eu estou esperando você. Não deixe de assistir... amanhã,
    [19.58, 22.00, "P6"], # mostrando o que aprendeu, vai fazer a diferença
]
TAIL = 1.4
f, c, t, out = [], "", 0.0, []
for i, (a, b, p) in enumerate(SEGS):
    d = b - a
    out.append([a, b, round(t, 3), i, p]); t += d
    f.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
    f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.02:.3f}:d=0.02[a{i}]")
    c += f"[v{i}][a{i}]"
f.append(f"{c}concat=n={len(SEGS)}:v=1:a=1[vc][ac]")
f.append(f"[vc]tpad=stop_mode=clone:stop_duration={TAIL}[v]")
f.append(f"[ac]apad=pad_dur={TAIL}[a]")
open("cuts/clean.filter.txt", "w").write(";\n".join(f))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "source/sdr.mp4", "-filter_complex_script", "cuts/clean.filter.txt",
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-r", "30",
                "-c:a", "aac", "-b:a", "256k", "cuts/clean.mp4"], check=True)
json.dump({"segments": out, "duration": round(t + TAIL, 3), "speech_end": round(t, 3)}, open("cuts/clean.json", "w"), indent=1)
print("dur", round(t + TAIL, 2))
