"""Pipeline:  visuals (Manim)  ->  narration script  ->  voice (TTS)  ->  sync  ->  final video.
  python build_video.py tts [--engine espeak|edge|piper]   # build/audio/*.wav + build/durations.json
  python build_video.py render [--quality low|high]        # silent scene clips (60 fps by default); writes build/timings/
  python build_video.py mux                                # place each segment's audio at its true start time, concat, SRT
  python build_video.py all                                # tts -> render -> mux
Order matters: tts first (scene pacing follows the audio length), then render, then mux."""
import argparse, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(ROOT, "build"); sys.path.insert(0, ROOT)
from narration import NARRATION
SCENES = list(NARRATION)
Q = {"low": ("-ql", 15, "480p15"), "medium": ("-qm", 30, "720p30"), "high": ("-qk" if False else "-qh", 60, "1080p60")}

def run(c, **k): print("$", " ".join(c)); subprocess.run(c, check=True, **k)

def render(quality):
    flag, fps, folder = Q[quality]; media = os.path.join(B, "media")
    for s in SCENES:
        run([sys.executable, "-m", "manim", flag, "--fps", str(fps), "scenes.py", s, "--media_dir", media], cwd=ROOT)
    return folder

def mux(folder):
    media = os.path.join(B, "media", "videos", "scenes", folder); out = os.path.join(B, "out"); os.makedirs(out, exist_ok=True)
    clips = []; t_global = 0.0; srt = []
    def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    for s in SCENES:
        tm = json.load(open(os.path.join(B, "timings", s + ".json"))); v = os.path.join(media, s + ".mp4"); o = os.path.join(out, s + ".mp4")
        ins, flt, labs = ["-i", v], [], []
        for k, st in enumerate(tm["starts"]):
            ins += ["-i", os.path.join(B, "audio", f"{s}_{k}.wav")]; ms = int(st * 1000 + 150)
            flt.append(f"[{k+1}:a]adelay={ms}|{ms}[a{k}]"); labs.append(f"[a{k}]")
            srt.append((t_global + st + 0.15, t_global + st + 0.15 + json.load(open(os.path.join(B, "durations.json")))[s][k], NARRATION[s][k]))
        flt.append("".join(labs) + f"amix=inputs={len(labs)}:normalize=0,apad[aout]")
        run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(flt), "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", o])
        clips.append(o); t_global += tm["total"]
    lst = os.path.join(out, "list.txt"); open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    final = os.path.join(out, "rashr_explainer.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", final])
    with open(os.path.join(out, "rashr_explainer.srt"), "w") as f:
        for i, (a, b, t) in enumerate(srt, 1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
    print("final:", final)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("step", choices=["tts", "render", "mux", "all"]); ap.add_argument("--quality", default="high", choices=list(Q)); ap.add_argument("--engine", default="kokoro")
    a = ap.parse_args()
    if a.step in ("tts", "all"): run([sys.executable, "tts.py", "--engine", a.engine], cwd=ROOT)
    f = Q[a.quality][2]
    if a.step in ("render", "all"): f = render(a.quality)
    if a.step in ("mux", "all"): mux(f)
