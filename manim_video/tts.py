"""Voice generation.  Engines (pick with --engine):
  kokoro  (default)  Kokoro-82M neural voice (Apache-2.0) via kokoro-onnx; offline once the two model files are in voices/
  espeak             offline, open-source (GPL) eSpeak NG; robotic fallback
  edge    Microsoft Edge neural voices via the `edge-tts` package (needs internet; en-US-AndrewNeural)
  piper   Piper neural TTS (needs a downloaded .onnx voice; set PIPER_MODEL)
No engine imitates any real person's voice.  Output: build/audio/<scene>_<k>.wav and build/durations.json"""
import argparse, asyncio, json, os, subprocess, wave
from narration import NARRATION
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "build", "audio")

def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.decode().strip())

_K = None
def kokoro_model():
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        vd = os.path.join(ROOT, "voices"); os.makedirs(vd, exist_ok=True)
        base = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
        for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
            if not os.path.exists(os.path.join(vd, f)):
                import urllib.request; print("downloading", f); urllib.request.urlretrieve(base + f, os.path.join(vd, f))
        _K = Kokoro(os.path.join(vd, "kokoro-v1.0.onnx"), os.path.join(vd, "voices-v1.0.bin"))
    return _K

def say(engine, text, wav):
    if engine == "kokoro":
        import soundfile as sf, numpy as np
        k = kokoro_model(); s, sr = k.create(text, voice=os.environ.get("KOKORO_VOICE", "am_michael"), speed=0.97, lang="en-us")
        sf.write(wav, np.concatenate([s, np.zeros(int(0.12 * sr), dtype=s.dtype)]), sr)
    elif engine == "espeak":
        subprocess.run(["espeak-ng", "-v", "en-us+f3", "-s", "158", "-p", "52", "-g", "4", "-w", wav, text], check=True)
    elif engine == "edge":
        import edge_tts
        mp3 = wav[:-4] + ".mp3"
        asyncio.run(edge_tts.Communicate(text, os.environ.get("EDGE_VOICE", "en-US-AndrewNeural"), rate="-4%").save(mp3))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "44100", "-ac", "1", wav], check=True)
    elif engine == "piper":
        subprocess.run(["piper", "--model", os.environ["PIPER_MODEL"], "--output_file", wav], input=text.encode(), check=True)
    else: raise SystemExit("unknown engine")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--engine", default="kokoro"); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); durs = {}
    for sid, segs in NARRATION.items():
        durs[sid] = []
        for k, t in enumerate(segs):
            w = os.path.join(OUT, f"{sid}_{k}.wav"); say(a.engine, t, w); durs[sid].append(round(dur(w), 3))
    json.dump(durs, open(os.path.join(ROOT, "build", "durations.json"), "w"), indent=1)
    print("total narration seconds:", round(sum(map(sum, durs.values())), 1))
