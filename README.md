# RAShR — Repeated Angular Shorth Regression: educational package

One story, five deliverables, one code base (`rashr_core.py` is the single source of truth for the estimator and simulator; `paper_values.py` holds the numbers reported in Dharavath & Srivastava).

| Deliverable | Where | How to use |
|---|---|---|
| A. Manim video (narrated, layman-first course: 27 scenes, ~26 min, 1080p **60 fps**, neural voice, subtitles; plain English, geometry of every concept, no author names) | `manim_video/rashr_explainer_720p60.mp4` (in the zip), full 1080p60 file delivered separately | rebuild: `cd manim_video && python build_video.py all` |
| B. PowerPoint (32 slides, geometry-first, speaker notes) | `pptx/rashr_presentation.pptx` | rebuild: `cd pptx && node build_pptx.js` (needs `pptxgenjs`) |
| C. Interactive HTML presentation (MathJax, 30 slides, 7 live demos) | `html/rashr_presentation.html` | open in a browser; rebuild with `python build_html.py` |
| D. Beamer research-seminar deck (38 frames: theory with proofs, native TikZ/pgfplots figures, appendix) | `beamer/rashr_beamer.pdf`, theme `beamer/beamerthemerashr.sty` | `cd beamer && python ../export_beamer_data.py && latexmk -xelatex rashr_beamer.tex` (xelatex; fonts Latin Modern, Inter) |
| E. Streamlit app (geometry mode + simulation lab) | `app/app.py`, `app/styles.css` | `streamlit run app/app.py` from this folder |
| Notebooks | `notebooks/*.ipynb` | run in any Python ≥3.10 with `requirements.txt`; seeds fixed |

## Setup
`pip install -r requirements.txt` (Manim additionally needs system `ffmpeg`, Pango/Cairo and a LaTeX with `dvisvgm`).

## Reproduce everything
```
python make_figures.py            # figures/fig*.png|pdf
python make_pptx_figures.py       # figures/p_*.png (deck-specific)
python run_simulations.py         # results/simulation_results.json (deterministic seeds; a few minutes)
python build_notebooks.py         # regenerates the notebooks
python build_html.py              # html/rashr_presentation.html
python ransac_sensitivity.py      # results/ransac_sensitivity.json (RANSAC threshold study)
python export_beamer_data.py      # beamer/data/* (CSV + TikZ snippets for the deck)
```

## Video pipeline (visuals → script → voice → sync → final)
`narration.py` is the script. `python build_video.py tts` creates one WAV per narration segment and `build/durations.json`; scenes pace themselves to those lengths (`common.SyncScene`); `render` writes silent clips (`--quality low|medium|high`, high = 1080p60) and records the true start time of every segment; `mux` places each segment at its recorded time, concatenates, and writes `build/out/rashr_explainer.mp4` plus `.srt` subtitles.
Voice engines (`--engine`): `kokoro` (default; Kokoro-82M neural voice, Apache-2.0, via `kokoro-onnx`; the two model files, 350 MB, are downloaded from GitHub releases into `manim_video/voices/` on first use and are *not* part of the zip), `espeak` (offline robotic fallback), `edge` (Microsoft neural voice via `edge-tts`, needs internet), `piper` (needs a downloaded voice; set `PIPER_MODEL`). Set `KOKORO_VOICE` to change the speaker (default `am_michael`). No engine imitates a real person. The final mux applies EBU R128 loudness normalisation.

## What to know before trusting the numbers
* **Simulation curves are a re-implementation.** The paper does not fully specify its RANSAC threshold or LTS/MM constants, so absolute numbers differ from the paper (e.g. RANSAC with the scikit-learn style threshold MAD(y) fails much earlier on the compact cluster than the paper's RANSAC; `results/ransac_sensitivity.json` and Appendix C of the Beamer deck show how strongly this one constant matters — with an oracle threshold RANSAC is far stronger, yet still fails at 44–46% compact contamination. In the sensitivity run RAShR fails 55% at 44% compact contamination versus 60% in the paper.). The qualitative pattern is reproduced. Decks show the paper's own numbers separately and label ours "re-implementation". I did not tune anything toward the paper's values.
* The cluster-move plateau is 2.11 on my sample versus 2.058 in the paper (different majority sample); only its constancy is the point.
* Fig. 1 uses seed 3, which reproduces the paper's pattern (OLS −0.53, LMS −0.21, MM −0.29, RAShR +2.02).
* Honest limits shown in every deliverable: MM/RANSAC win on clean data, vertical contamination and bad leverage; ≈30° / −150° cluster directions and non-compact clusters remove the advantage; at 46% a compact cluster defeats every method; Prop. 3 is for population LMS only; Theorem 1 needs the standardization medians/MADs to stay fixed; the method is not fully affine equivariant; the intercept is a median over all points.
* Statements were cross-checked against the paper text (Prop. 1–3, Cor. 1, Lemma 1, Thm 1, Remark 1, Section 5 numbers).
