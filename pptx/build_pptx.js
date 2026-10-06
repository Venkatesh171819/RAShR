// RAShR PowerPoint -- geometry-first deck, designed independently of the Beamer deck.
// Run:  node build_pptx.js   (needs pptxgenjs; figures read from ../figures)
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");

const FIG = path.resolve(__dirname, "../figures");
const DIMS = JSON.parse(fs.readFileSync(path.join(FIG, "dims.json")));
const R = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../results/simulation_results.json")));

const THEME = {
  name: "RAShR", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "10213A", lt1: "FFFFFF", dk2: "17406F", lt2: "F4F7FB",
            accent1: "1F6FEB", accent2: "0FA3B1", accent3: "D1495B", accent4: "F28F3B", accent5: "7B4FB5", accent6: "17A398",
            hlink: "1F6FEB", folHlink: "7B4FB5" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.33 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Repeated Angular Shorth Regression (RAShR)";
pres.author = "RAShR educational package";
const S = pres.SchemeColor;
const W = 13.33, H = 7.5, MX = 0.6;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({ title: "RASHR_TITLE", background: { color: "10213A" }, objects: [],
  slideNumber: undefined });
pres.defineSlideMaster({ title: "RASHR_SECTION", background: { color: "17406F" }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 2.7, w: 11.5, h: 1.2, fontFace: "Cambria", fontSize: 44, bold: true, color: S.background1, margin: 0, align: "left" }, text: "" } },
  { placeholder: { options: { name: "body", type: "body", x: 0.9, y: 4.0, w: 11.0, h: 1.0, fontFace: "Calibri", fontSize: 20, color: "CFE0FA", margin: 0, align: "left" }, text: "" } },
]});
pres.defineSlideMaster({ title: "RASHR_CONTENT", background: { color: "FFFFFF" },
  slideNumber: { x: 12.3, y: 7.05, w: 0.6, h: 0.3, fontFace: "Calibri", fontSize: 11, color: "5B6B82", align: "right" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.35, w: 12.1, h: 0.85, fontFace: "Cambria", fontSize: 30, bold: true, color: S.text1, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { text: { text: "RAShR · Repeated Angular Shorth Regression", options: { x: MX, y: 7.05, w: 6, h: 0.3, fontSize: 11, color: "5B6B82", fontFace: "Calibri", margin: 0 } } },
  ]});


// ---- tiny math markup: _x, _{...} -> subscript runs, ^x, ^{...} -> superscript; unicode sub/superscripts are normalised first
const SUBMAP = { "ₓ": "x", "ᵢ": "i", "ⱼ": "j", "₀": "0", "₁": "1", "₂": "2" };
function normMath(s) {
  s = s.replace(/₍([^₎]*)₎/g, (m, g) => "_{(" + g.replace(/[ₓᵢⱼ]/g, c => SUBMAP[c]) + ")}");
  s = s.replace(/([ₓᵢⱼ₀₁₂])/g, c => "_" + SUBMAP[c]);
  s = s.replace(/ᴳ/g, "^G");
  s = s.replace(/([α-ωΑ-Ω])\u0302/g, "$1-hat");
  return s;
}
function mathRuns(line, base) {
  const out = []; const re = /([_^])(\{[^}]*\}|[A-Za-z0-9])/g; let last = 0, m;
  while ((m = re.exec(line)) !== null) {
    if (m.index > last) out.push({ text: line.slice(last, m.index), options: { ...base } });
    let g = m[2]; if (g[0] === "{") g = g.slice(1, -1); g = g.replace(/[_{}]/g, "");
    out.push({ text: g, options: { ...base, [m[1] === "_" ? "subscript" : "superscript"]: true } });
    last = re.lastIndex;
  }
  if (last < line.length) out.push({ text: line.slice(last), options: { ...base } });
  return out;
}
function runs(text, base = {}) {
  text = normMath(text);
  if (!/[_^]/.test(text)) return text;            // plain string: leave untouched
  const lines = text.split("\n"), out = [];
  lines.forEach((ln, i) => { const r = mathRuns(ln, base); if (i < lines.length - 1 && r.length) r[r.length - 1].options.breakLine = true; out.push(...r); });
  return out;
}

// ------------------------------------------------------------------ helpers
const sh = () => ({ type: "outer", color: "10213A", opacity: 0.10, blur: 6, offset: 2, angle: 90 });
function img(slide, name, x, y, w, h, alt) {
  const [iw, ih] = DIMS[name]; const r = Math.min(w / iw, h / ih); const dw = iw * r, dh = ih * r;
  slide.addImage({ path: path.join(FIG, name + ".png"), x: x + (w - dw) / 2, y: y + (h - dh) / 2, w: dw, h: dh, altText: alt || name, objectName: name });
}
function card(slide, x, y, w, h, title, body, o = {}) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: o.fill || S.background2 }, line: { color: o.line || "E3E8F0", width: 0.75 }, shadow: sh(), objectName: "card-" + title });
  slide.addText(runs(title), { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.4, fontSize: o.tsize || 16, bold: true, color: o.tcolor || S.text1, fontFace: "Calibri", margin: 0, isTextBox: true, valign: "top" });
  slide.addText(runs(body), { x: x + 0.2, y: y + 0.55, w: w - 0.4, h: h - 0.65, fontSize: o.size || 14, color: S.text1, fontFace: "Calibri", margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 4 });
}
function chip(slide, x, y, w, h, text, o = {}) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.1, fill: { color: o.fill || S.background2 }, line: { color: o.line || "D5DCE8", width: 0.75 }, objectName: "chip-" + text });
  slide.addText(runs(text), { x, y, w, h, fontSize: o.size || 14, bold: true, color: o.color || S.text1, align: "center", valign: "middle", fontFace: "Calibri", margin: 4, isTextBox: true });
}
function flow(slide, x, y, labels, wEach, h, gap, hlFrom = 99) {
  labels.forEach((t, i) => {
    const xx = x + i * (wEach + gap);
    chip(slide, xx, y, wEach, h, t, i >= hlFrom ? { fill: S.accent1, line: S.accent1, color: S.background1 } : {});
    if (i < labels.length - 1) slide.addText("›", { x: xx + wEach, y, w: gap, h, fontSize: 20, color: "5B6B82", align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
}
function eq(slide, text, x, y, w, h = 0.7, size = 20) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.1, fill: { color: S.background2 }, line: { color: "E3E8F0", width: 0.75 }, objectName: "eq-bg" });
  slide.addText(runs(text), { x, y, w, h, fontSize: size, fontFace: "Cambria", italic: true, color: S.text1, align: "center", valign: "middle", margin: 6, isTextBox: true });
}
const EQD = JSON.parse(fs.readFileSync(path.join(FIG, "eq_dims.json")));
function eqImg(slide, key, x, y, w, h) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.1, fill: { color: S.background2 }, line: { color: "E3E8F0", width: 0.75 }, objectName: "eq-bg-" + key });
  const [iw, ih] = EQD[key]; const r = Math.min((w - 0.3) / (iw / 300), (h - 0.2) / (ih / 300), 1.15); const dw = iw / 300 * r, dh = ih / 300 * r;
  slide.addImage({ path: path.join(FIG, "eq_" + key + ".png"), x: x + (w - dw) / 2, y: y + (h - dh) / 2, w: dw, h: dh, altText: "formula " + key, objectName: "eq-" + key });
}
function stat(slide, x, y, w, big, label, color) {
  slide.addText(big, { x, y, w, h: 0.9, fontSize: 44, bold: true, fontFace: "Cambria", color: color || S.accent1, margin: 0, align: "left", isTextBox: true });
  slide.addText(runs(label), { x, y: y + 0.9, w, h: 0.5, fontSize: 14, color: "5B6B82", margin: 0, isTextBox: true, valign: "top" });
}
function cap(slide, text, x, y, w, h = 0.5) {
  slide.addText(runs(text), { x, y, w, h, fontSize: 12, color: "5B6B82", italic: true, margin: 0, isTextBox: true, valign: "top" });
}
function content(title, section, notes) {
  const s = pres.addSlide({ masterName: "RASHR_CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(num, title, sub, sec) {
  const s = pres.addSlide({ masterName: "RASHR_SECTION", sectionTitle: sec || title });
  s.addText(num, { x: 0.9, y: 1.7, w: 3, h: 0.9, fontSize: 40, bold: true, color: S.accent2, fontFace: "Cambria", margin: 0, isTextBox: true });
  s.addText(title, { placeholder: "title" }); s.addText(sub, { placeholder: "body" });
  return s;
}

// ================================================================== 1 TITLE
pres.addSection({ title: "Start" });
{
  const s = pres.addSlide({ masterName: "RASHR_TITLE", sectionTitle: "Start" });
  s.addText("RAShR", { x: 0.9, y: 1.2, w: 7, h: 0.8, fontSize: 24, bold: true, color: S.accent2, fontFace: "Calibri", margin: 0, isTextBox: true, charSpacing: 6 });
  s.addText("Repeated Angular Shorth Regression", { x: 0.9, y: 2.0, w: 8.2, h: 1.9, fontSize: 48, bold: true, color: S.background1, fontFace: "Cambria", margin: 0, isTextBox: true, valign: "top" });
  s.addText("Fit a line by asking which direction pairwise chords agree on, not which line has small residuals.", { x: 0.9, y: 4.2, w: 7.4, h: 1.1, fontSize: 20, color: "CFE0FA", fontFace: "Calibri", margin: 0, isTextBox: true, valign: "top" });
  s.addText("Based on “Robust Linear Regression via the Repeated Angular Shorth” — V. Dharavath & V. Srivastava, NIT Warangal", { x: 0.9, y: 6.4, w: 9, h: 0.5, fontSize: 14, color: "9FB7DE", fontFace: "Calibri", margin: 0, isTextBox: true });
  // circle motif: chords and a shorth arc drawn natively
  const cx = 10.6, cy = 3.7, r = 2.1;
  s.addShape(pres.ShapeType.ellipse, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { color: "10213A", transparency: 100 }, line: { color: "9FB7DE", width: 2 }, objectName: "motif-circle" });
  [[20, "3E7CE0"], [28, "3E7CE0"], [33, "3E7CE0"], [38, "3E7CE0"], [44, "3E7CE0"], [150, "D1495B"]].forEach(([deg, col], i) => {
    const a = (-2 * deg * Math.PI) / 180, px = cx + r * Math.cos(a), py = cy + r * Math.sin(a);
    s.addShape(pres.ShapeType.ellipse, { x: px - 0.11, y: py - 0.11, w: 0.22, h: 0.22, fill: { color: col }, line: { color: "FFFFFF", width: 1 }, objectName: "motif-dot" + i });
  });
  s.addText("angles on the\nprojective circle", { x: cx - 1.2, y: cy - 0.45, w: 2.4, h: 0.9, fontSize: 16, color: "CFE0FA", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addNotes("Title. The whole deck follows one story: coherent contamination fools residual-based fits; pairwise chord directions, concentrated twice with the shorth, do not get fooled — within limits.");
}

// ================================================================== PROBLEM
pres.addSection({ title: "Problem" });
{
  const s = content("A robust fit can still follow the wrong line", "Problem",
    "Figure re-created from the paper's setting (seed 3). Paper values: OLS -0.53, LMS -0.20, MM -0.26, RAShR +2.02, truth +2.00.");
  img(s, "fig1_motivation", MX, 1.35, 7.9, 5.2, "Scatter: 62 majority points on y=1+2x, 38 compact leverage cluster, OLS/LMS/MM negative slopes, RAShR positive");
  stat(s, 8.9, 1.5, 1.9, "+2.02", "RAShR slope (paper)", S.accent1);
  stat(s, 10.9, 1.5, 1.9, "−0.20", "LMS slope (paper)", S.accent3);
  stat(s, 8.9, 3.1, 1.9, "−0.26", "MM slope (paper)", S.accent3);
  stat(s, 10.9, 3.1, 1.9, "−0.53", "OLS slope (paper)", "5B6B82");
  card(s, 8.9, 4.75, 3.85, 1.85, "Why surprising?", "High breakdown means the estimate stays bounded — not that it follows the dominant structure.", { fill: "FFF8F0", line: "F28F3B", size: 14 });
  cap(s, "Our re-creation; paper's exact sample not available.", MX, 6.6, 7.9, 0.3);
}
{
  const s = content("Vocabulary, built up step by step", "Problem");
  const items = [
    ["Outlier vs contamination", "Outlier: one unusual point. Contamination: observations not following the main pattern — possibly many."],
    ["Coherent contamination", "Contaminated points related to each other: a compact cluster or a competing line."],
    ["High leverage", "x far from the bulk of the x-values → strong pull on the slope."],
    ["Breakdown point", "Fraction that can be replaced before the estimate can be driven arbitrarily far: a boundedness guarantee."],
    ["Residual-based method", "Judges candidate lines by residuals yᵢ − ŷᵢ: LMS, LTS, MM…"],
    ["Chord", "The segment joining two points. It has a direction; it is not a regression line."],
  ];
  items.forEach((it, i) => card(s, MX + (i % 3) * 4.1, 1.5 + Math.floor(i / 3) * 2.65, 3.9, 2.45, it[0], it[1], { size: 15 }));
}
{
  const s = content("Why residuals mislead: a narrow strip through the cluster", "Problem",
    "W(l) is the smallest half-width of a vertical strip around l containing half of the mass. Proposition 3 formalises this for population LMS.");
  img(s, "fig10_lms_attraction", MX, 1.35, 7.6, 5.3, "LMS strips around the true line and around a line through the cluster");
  eqImg(s, "strip", 8.5, 1.5, 4.25, 0.9);
  card(s, 8.5, 2.7, 4.25, 3.9, "Reading the picture", "• The true line needs positive width because of noise.\n• A line through a point-mass cluster only needs a little extra mass from the majority.\n• As contamination → ½, that width → 0.\n• Proved for population LMS only; LTS/MM are studied empirically.", { size: 14 });
}
{
  const s = pres.addSlide({ masterName: "RASHR_SECTION", sectionTitle: "Problem" });
  s.addText("The central shift", { placeholder: "title" });
  s.addText("", { placeholder: "body" });
  s.addText([{ text: "Instead of asking ", options: { color: "CFE0FA" } }, { text: "“Which line produces small residuals?”", options: { color: "F28F3B", bold: true } }], { x: 0.9, y: 3.9, w: 11.5, h: 0.6, fontSize: 24, fontFace: "Calibri", margin: 0, isTextBox: true });
  s.addText([{ text: "RAShR asks ", options: { color: "CFE0FA" } }, { text: "“Which direction receives the strongest agreement from pairwise chords?”", options: { color: "FFFFFF", bold: true } }], { x: 0.9, y: 4.6, w: 11.8, h: 1.1, fontSize: 26, fontFace: "Calibri", margin: 0, isTextBox: true, valign: "top" });
}

// ================================================================== RELATED WORK
pres.addSection({ title: "Related work" });
{
  const s = content("Related work as one story: pairwise slopes → pairwise directions", "Related work");
  const rows = [
    ["Theil–Sen", "median of all pairwise slopes", "breakdown ≈ 29%"],
    ["Repeated median", "median of per-anchor medians", "50% breakdown; rank effect"],
    ["LMS / LTS", "narrow strip / trimmed residuals", "coherent cluster can win"],
    ["MM", "robust start + M-step", "efficient, inherits start"],
    ["RANSAC", "2-point models, count inliers", "strong on some geometries"],
    ["Hough transform", "votes in parameter space", "mode seeking"],
    ["Shorth", "shortest half-interval", "→ RAShR building block"],
    ["Directional regression", "orientation as geometry", "→ same spirit"],
  ];
  rows.forEach((r, i) => {
    const x = MX + (i % 4) * 3.05, y = 1.5 + Math.floor(i / 4) * 2.6; const hl = i >= 6;
    card(s, x, y, 2.9, 2.4, r[0], r[1] + "\n" + r[2], { size: 14, fill: hl ? "E8F1FE" : S.background2, line: hl ? "1F6FEB" : "E3E8F0" });
  });
  s.addText("Each method: geometric object → what it measures → limitation → link to RAShR", { x: MX, y: 6.75, w: 12, h: 0.3, fontSize: 12, color: "5B6B82", italic: true, margin: 0, isTextBox: true });
}
{
  const s = content("Siegel's repeated median: median of local medians", "Related work");
  img(s, "fig12_repeated_median", MX, 1.4, 12.1, 3.1, "Repeated median in three steps");
  flow(s, MX, 4.6, ["1 anchor", "2 chords", "3 slopes", "4 local median", "5 all anchors", "6 median of medians"], 1.8, 0.55, 0.26);
  eqImg(s, "rm", MX, 5.55, 6.4, 0.8);
  card(s, 7.3, 5.45, 5.4, 1.4, "Bridge to RAShR", "Keep the pairwise-geometric idea; replace slope/median aggregation by angular concentration through the shorth.", { fill: "E8F1FE", line: "1F6FEB", size: 14 });
}

// ================================================================== RASHR
pres.addSection({ title: "RAShR" });
divider("02", "RAShR", "points → chords → directions → projective angles → angular shorth → local directions → repeated shorth → slope → intercept → line");
{
  const s = content("The whole path, in one picture", "RAShR");
  flow(s, MX, 1.6, ["points", "standardize", "chords", "directions φ", "projective angles"], 2.2, 0.6, 0.28, 99);
  flow(s, MX, 2.9, ["angular shorth", "local θᵢ, wᵢ", "repeated shorth θ̂", "slope β̂", "intercept α̂"], 2.2, 0.6, 0.28, 0);
  img(s, "p_filmstrip_anchor", MX, 4.2, 12.1, 2.6, "One anchor step by step");
}
{
  const s = content("Step 1 — Angles depend on units, so standardize robustly", "RAShR");
  img(s, "p_filmstrip_scale", MX, 1.3, 12.1, 3.2, "Raw → centred → scaled data");
  eqImg(s, "std", MX, 4.75, 7.2, 0.85);
  card(s, 8.1, 4.65, 4.6, 2.1, "Details from the paper", "1.4826·MAD = normal-consistent scale. If MAD = 0, use the standard deviation of that coordinate.", { size: 14 });
  cap(s, "original data → robust centre → robust scale → standardized data", MX, 5.8, 7.2, 0.4);
}
{
  const s = content("Step 2 — A chord is a vector; its direction is atan2", "RAShR");
  img(s, "p_chord_fan", MX, 1.3, 7.4, 5.4, "Chords from one anchor to all other points");
  eqImg(s, "phi", 8.3, 1.5, 4.45, 0.9);
  card(s, 8.3, 2.65, 4.45, 3.9, "Why atan2?", "• It uses the vector (Δu, Δv), not the ratio Δv/Δu.\n• A nearly vertical chord (Δu ≈ 0) is harmless.\n• Majority–majority chords (blue) fan out near the true direction; chords to the cluster (red) all share one very different direction as seen from this anchor.", { size: 14 });
}
{
  const s = content("Step 3 — The projective circle: a line has no orientation", "RAShR");
  img(s, "fig3_projective_circle", MX, 1.3, 8.1, 4.0, "Projective circle and wrap-around");
  eqImg(s, "dpi", MX, 5.5, 5.4, 0.8);
  card(s, 9.0, 1.4, 3.75, 2.6, "20° ≡ 200°", "Opposite directions are the same unoriented line, so directions live on [0, π) with 0 and π glued.", { size: 14 });
  card(s, 9.0, 4.15, 3.75, 2.55, "Wrap-around", "5° and 175° are only 10° apart. An ordinary real interval cannot represent an arc crossing the seam.", { size: 14, fill: "FFF8F0", line: "F28F3B" });
}
{
  const s = content("Step 4 — Angular shorth: the shortest arc holding half the angles", "RAShR");
  img(s, "fig4_angular_shorth", MX, 1.3, 12.1, 3.1, "Angular shorth windows");
  flow(s, MX, 4.5, ["on circle", "sort", "copy + π", "slide h-windows", "measure widths", "shortest wins", "midpoint"], 1.58, 0.6, 0.17, 6);
  eqImg(s, "ash", MX, 5.4, 7.4, 0.8);
  card(s, 8.3, 5.3, 4.45, 1.55, "Shorth ≠ median", "Median angle = middle-ranked. Shorth = centre of the strongest concentrated half. Ties → smallest left endpoint.", { size: 13 });
}
{
  const s = content("Step 5 — Local direction: what one anchor sees", "RAShR");
  img(s, "p_circle_anchor", MX, 1.3, 5.3, 5.4, "Anchor's chord directions on the projective circle");
  eqImg(s, "local", 6.2, 1.5, 6.55, 0.85);
  card(s, 6.2, 2.6, 3.2, 2.2, "Small wᵢ", "Strong directional agreement from anchor i.", { size: 15, fill: "E8F7F8", line: "0FA3B1" });
  card(s, 9.55, 2.6, 3.2, 2.2, "Large wᵢ", "Weak agreement; no clear direction from this anchor.", { size: 15, fill: "FFF8F0", line: "F28F3B" });
  card(s, 6.2, 5.0, 6.55, 1.7, "On the circle", "Blue dots: chords to majority points. Red dots: chords to the cluster. The teal arc is the shortest half-window; its midpoint is θᵢ.", { size: 14 });
}
{
  const s = content("Step 6 — Repeated: the same shorth, twice", "RAShR");
  img(s, "p_two_level", MX, 1.3, 12.1, 4.2, "Local shorth at six anchors, then outer shorth over all local directions");
  eqImg(s, "outer", MX, 5.7, 3.8, 0.85);
  card(s, 4.6, 5.6, 4.0, 1.25, "Local aggregation", "inside each anchor's n − 1 chords (h_L = ⌈(n−1)/2⌉)", { size: 13 });
  card(s, 8.75, 5.6, 4.0, 1.25, "Outer aggregation", "across the n local directions (h_O = ⌈n/2⌉)", { size: 13 });
}
{
  const s = content("Step 7 — Back to the original scale", "RAShR");
  {
    const keys = ["chip_theta", "chip_tan", "chip_sy", "chip_sx", "chip_beta"];
    keys.forEach((k, i) => { const xx = MX + i * 2.48; const last = i === 4;
      s.addShape(pres.ShapeType.roundRect, { x: xx, y: 1.4, w: 2.2, h: 0.6, rectRadius: 0.1, fill: { color: last ? S.accent1 : S.background2 }, line: { color: last ? S.accent1 : "D5DCE8", width: 0.75 }, objectName: "chip-" + k });
      const kk = last ? "chip_beta_w" : k; const [iw, ih] = EQD[kk]; const hh = 0.34, ww = iw / ih * hh;
      s.addImage({ path: path.join(FIG, "eq_" + kk + ".png"), x: xx + (2.2 - ww) / 2, y: 1.4 + (0.6 - hh) / 2, w: ww, h: hh, altText: k });
      if (i < 4) s.addText("›", { x: xx + 2.2, y: 1.4, w: 0.28, h: 0.6, fontSize: 20, color: "5B6B82", align: "center", valign: "middle", margin: 0, isTextBox: true }); });
  }
  eqImg(s, "slope", MX, 2.4, 12.1, 0.8);
  img(s, "p_intercept", MX, 3.4, 8.2, 3.4, "Intercepts implied by each point; median chooses vertical position");
  card(s, 9.0, 3.5, 3.75, 3.2, "Honest caveat", "α̂ is a median over all observations. With 38% contamination at (15, −10) it can be pulled even when β̂ is right; the paper evaluates the slope.", { size: 14, fill: "FFF8F0", line: "F28F3B" });
}
{
  const s = content("Algorithm and cost", "RAShR");
  const steps = ["raw observations", "robust standardization", "pairwise chord directions", "local shortest half-window", "local directions θᵢ", "second angular shorth", "original-scale slope β̂", "median intercept α̂", "final line"];
  steps.forEach((t, i) => chip(s, MX, 1.35 + i * 0.58, 4.3, 0.46, t, i === 8 ? { fill: S.accent1, line: S.accent1, color: S.background1 } : {}));
  stat(s, 5.6, 1.5, 3.3, "O(n² log n)", "time: n anchors × sort n−1 angles");
  stat(s, 9.3, 1.5, 3.4, "O(n)", "extra memory, one anchor at a time");
  card(s, 5.6, 3.3, 7.15, 1.55, "vs exhaustive subset search", "Direct LMS/LTS subset search is O(n³) in the paper's implementations. Same order as a direct repeated median.", { size: 14 });
  card(s, 5.6, 5.05, 7.15, 1.7, "Deterministic", "No random sampling. Ties go to the smallest left endpoint, so the same data always give the same line.", { size: 14, fill: "E8F7F8", line: "0FA3B1" });
}

// ================================================================== THEORY
pres.addSection({ title: "Theory" });
divider("03", "Theory through geometry", "statement → meaning → geometry → experiment → significance", "Theory");
{
  const s = content("Proposition 1 — Exact fit (and Corollary 1)", "Theory");
  img(s, "fig13_exact_fit", MX, 1.3, 7.8, 3.6, "Exact fit with contamination");
  card(s, 8.6, 1.4, 4.15, 3.4, "Statement", "If yᵢ = α* + β*xᵢ with distinct xᵢ, then (α̂, β̂) = (α*, β*).\nAll chords share one direction → all shorth widths are 0.", { size: 14 });
  card(s, MX, 5.05, 12.15, 1.75, "Corollary 1 — exact fit under contamination", "If the majority lies exactly on a line, no contaminated point is on it, and |B| < ⌈(n−1)/2⌉, the line is recovered wherever the contamination is: a group smaller than the half-sample cannot form a competing zero-width window. (Shared with LMS and the repeated median.)", { size: 14, fill: "E8F7F8", line: "0FA3B1" });
}
{
  const s = content("Proposition 2 — Translation and positive-scale equivariance", "Theory");
  img(s, "fig14_equivariance", MX, 1.3, 12.1, 3.2, "Original, rescaled data, and y→y+γx");
  eqImg(s, "equiv", MX, 4.7, 7.6, 0.85);
  card(s, 8.4, 4.6, 4.35, 2.2, "Limitation", "Not fully affine equivariant: y → y + γx changes s_y, so it is not a simple rotation of the standardized data.", { size: 14, fill: "FFF8F0", line: "F28F3B" });
  cap(s, "Standardization removes translation and positive rescaling, so the same chords and shorths are selected.", MX, 5.7, 7.6, 0.6);
}
{
  const s = content("Separation: lemma, local condition, outer condition", "Theory");
  img(s, "fig5_local_directions", MX, 1.3, 5.2, 4.2, "Majority anchors vs contaminated anchors: local directions and widths");
  card(s, 6.1, 1.4, 3.2, 3.0, "Lemma 1", "If every arc with ≥ h elements that touches B is strictly wider than A's shortest arc, then ASh(A ∪ B) = ASh(A).", { size: 13 });
  card(s, 9.5, 1.4, 3.25, 3.0, "(L) Local", "At each majority anchor, majority–majority chords form a narrower half-window than any involving contamination.", { size: 13, fill: "E8F1FE", line: "1F6FEB" });
  card(s, 6.1, 4.6, 3.2, 2.2, "(O) Outer", "Majority-anchor directions form a narrower half-sample window than any involving contaminated anchors.", { size: 13, fill: "E8F1FE", line: "1F6FEB" });
  card(s, 9.5, 4.6, 3.25, 2.2, "Size", "|G| > n/2 ⇒ |G|−1 ≥ h_L and |G| ≥ h_O: both stages can be built from majority points alone.", { size: 13 });
}
{
  const s = content("Theorem 1 — Zero influence of separated contamination", "Theory",
    "Cluster at cx=10,18,26,36 with majority fixed. In our run RAShR stays at the same slope; paper reports 2.058 on its sample.");
  img(s, "p_filmstrip_move", MX, 1.3, 12.1, 2.9, "Cluster moved horizontally; RAShR line does not move");
  eqImg(s, "thm1", MX, 4.4, 5.6, 0.85);
  card(s, 6.5, 4.35, 6.25, 2.45, "What it says", "Once (L), (O) and |G| > n/2 hold, moving, adding or removing contaminated points does not change β̂.\nCaveat: the standardization medians/MADs must stay unchanged — contamination can still affect Eq. (2).", { size: 14 });
  cap(s, "Paper: slope exactly 2.058 once the cluster is far enough (its sample). Ours differs (different sample); the constancy is the point.", MX, 5.4, 5.6, 1.2);
}
{
  const s = content("Proposition 3 — Why coherent contamination can attract LMS", "Theory");
  card(s, MX, 1.4, 6.0, 2.5, "Model", "(X, Y) ~ (1−ε)P_G + ε δ_c, with P_G: Y = α* + β*X + e, e ~ N(0, σ²). The point mass c is at vertical distance Δ > 0 from the majority line.", { size: 14 });
  card(s, MX, 4.1, 6.0, 2.7, "Statement", "There is ε₀ < ½ such that for ε ∈ (ε₀, ½) every population LMS solution ℓ has |c_y − ℓ(c_x)| ≤ W(ℓ) with W(ℓ) → 0 as ε ↑ ½. The majority line is not an LMS solution.", { size: 14, fill: "E8F1FE", line: "1F6FEB" });
  img(s, "fig10_lms_attraction", 6.9, 1.4, 5.85, 3.6, "Strips around the true line and a line through the cluster");
  card(s, 6.9, 5.2, 5.85, 1.6, "Scope", "Proved for population LMS, asymptotically in ε ↑ ½. For LTS and MM only empirical evidence (Section 5), no theorem.", { size: 14, fill: "FFF8F0", line: "F28F3B" });
}
{
  const s = content("Remark — why “all chords near θ*” is too strong", "Theory");
  img(s, "fig11_all_chords_remark", MX, 1.3, 8.0, 3.7, "Near-vertical chords and the distribution of chord directions");
  card(s, 8.9, 1.4, 3.85, 3.6, "The problem", "Two points with almost equal x and a little vertical noise give a chord with an almost arbitrary direction. Requiring every majority chord within δ < π/8 of θ* is far too restrictive for noisy data.", { size: 14 });
  card(s, MX, 5.2, 12.15, 1.5, "What RAShR needs instead", "Concentration of a half-sample of chords — exactly what the shorth detects — not concentration of all of them.", { size: 15, fill: "E8F7F8", line: "0FA3B1" });
}

// ================================================================== EVIDENCE
pres.addSection({ title: "Evidence" });
divider("04", "Simulation evidence", "where RAShR helps — and where it does not", "Evidence");
{
  const s = content("Simulation design (paper, Section 5)", "Evidence");
  card(s, MX, 1.4, 6.0, 5.4, "Data", "n = 100, x ~ U[−5, 5], y = 1 + 2x + e, e ~ N(0, 1)\nA fraction f is replaced by:\n① compact leverage cluster at (15, −10), spread 0.3\n② competing line y = 5 − 1.25x + e_c, e_c ~ N(0, 0.5²)\n③ funnel: majority sd 0.2 + 0.6|x| plus a line with sd 0.3\nMetric |β̂ − 2|; failure = |β̂ − 2| > 0.5; 60 replications.", { size: 15 });
  card(s, 6.85, 1.4, 5.9, 2.7, "Competitors", "LMS · LTS (10 best elemental fits + 20 C-steps) · MM (LTS start, MAD scale, Tukey bisquare) · RANSAC (2-point samples, MAD-based threshold, 1000 trials)", { size: 14 });
  card(s, 6.85, 4.3, 5.9, 2.5, "Reproducibility note", "All curves in this deck come from our re-implementation with fixed seeds. Some constants (e.g. RANSAC's threshold) are not fully specified, so we compare patterns; the paper's own numbers are shown separately.", { size: 14, fill: "FFF8F0", line: "F28F3B" });
}
{
  const s = content("Limitation first: RAShR is not universally better", "Evidence");
  const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "10213A" }, align: "center", fontSize: 14 } });
  const c = (t, b) => ({ text: t, options: { align: "center", fontSize: 14, bold: !!b, color: b ? "1F6FEB" : "10213A" } });
  const l = (t) => ({ text: t, options: { align: "left", fontSize: 14, color: "10213A" } });
  s.addText("Paper — median |β̂ − 2|", { x: MX, y: 1.3, w: 6, h: 0.4, fontSize: 16, bold: true, color: S.text1, margin: 0, isTextBox: true });
  s.addTable([[hdr("setting"), hdr("RAShR"), hdr("MM"), hdr("RANSAC")],
    [l("Clean data"), c("0.033"), c("0.024", 1), c("0.022", 1)],
    [l("20% vertical contamination"), c("0.040"), c("0.027", 1), c("0.037")],
    [l("10% bad leverage"), c("0.041"), c("0.020", 1), c("0.021")]],
    { x: MX, y: 1.75, w: 7.3, colW: [3.1, 1.4, 1.4, 1.4], rowH: 0.45, border: { type: "solid", color: "E3E8F0", pt: 1 } });
  const S2 = R.standard, nm = { clean: "Clean", vertical20: "20% vertical", leverage10: "10% bad leverage", line20: "20% competing line" };
  const rows = Object.keys(S2).map(k => { const m = ["RAShR", "LMS", "LTS", "MM", "RANSAC"]; const mn = Math.min(...m.map(q => S2[k][q].med_abs_err));
    return [l(nm[k]), ...m.map(q => c(S2[k][q].med_abs_err.toFixed(3), S2[k][q].med_abs_err === mn))]; });
  s.addText("This project's re-implementation (100 reps)", { x: MX, y: 4.0, w: 8, h: 0.4, fontSize: 16, bold: true, color: S.text1, margin: 0, isTextBox: true });
  s.addTable([[hdr("setting"), hdr("RAShR"), hdr("LMS"), hdr("LTS"), hdr("MM"), hdr("RANSAC")], ...rows],
    { x: MX, y: 4.45, w: 9.0, colW: [2.6, 1.28, 1.28, 1.28, 1.28, 1.28], rowH: 0.4, border: { type: "solid", color: "E3E8F0", pt: 1 } });
  card(s, 8.3, 1.4, 4.45, 2.4, "Take-away", "At low contamination or in standard settings MM is generally the more efficient choice. RAShR's advantage needs a contaminating group that is both large and geometrically coherent.", { size: 14, fill: "E8F1FE", line: "1F6FEB" });
}
{
  const s = content("Failure rate vs contamination (our re-implementation)", "Evidence",
    "Native charts built from results/simulation_results.json (60 replications). Paper's own values are on the next slide.");
  const fr = R.fracs; const labels = fr.map(f => Math.round(f * 100) + "%");
  const M = ["RAShR", "LMS", "LTS", "MM", "RANSAC"], col = { RAShR: "1F6FEB", LMS: "E4572E", LTS: "17A398", MM: "F2A541", RANSAC: "7B4FB5" };
  [["compact", "(a) compact leverage cluster"], ["line", "(b) competing line"], ["funnel", "(c) funnel majority + line"]].forEach(([k, t], i) => {
    s.addChart(pres.charts.LINE, M.map(m => ({ name: m, labels, values: fr.map(f => R[k][f.toFixed(2)][m].fail) })),
      { x: MX + i * 4.1, y: 1.35, w: 4.0, h: 4.4, chartColors: M.map(m => col[m]), lineSize: 2.5, lineDataSymbolSize: 5,
        showTitle: true, title: t, titleFontSize: 14, titleColor: "10213A", titleFontFace: "+mn-lt",
        valAxisMinVal: 0, valAxisMaxVal: 1, valAxisLabelFontSize: 10, catAxisLabelFontSize: 10, valAxisLabelFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt",
        valAxisLabelColor: "5B6B82", catAxisLabelColor: "5B6B82", valGridLine: { color: "E3E8F0", size: 0.75 }, catGridLine: { style: "none" },
        showLegend: i === 0, legendPos: "b", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: "10213A", valAxisLabelFormatCode: "0%" });
  });
  s.addText("Failure = |β̂ − 2| > 0.5. Below ≈30% the high-breakdown methods behave alike; between ≈35% and 46% they separate. Compact cluster at 46%: every method fails.", { x: MX, y: 5.95, w: 12.1, h: 0.8, fontSize: 15, color: S.text1, margin: 0, isTextBox: true, valign: "top" });
}
{
  const s = content("What the paper reports (Figure 2 text)", "Evidence");
  const big = (x, y, w, h, title, lines) => card(s, x, y, w, h, title, lines, { size: 14 });
  big(MX, 1.4, 4.0, 3.9, "(a) Compact leverage", "36%: RAShR 0 · LMS 2 · LTS/MM 23 · RANSAC 50\n40%: RAShR 0 · LMS 58 · LTS/MM 100 · RANSAC 77\n44%: RAShR succeeds in 40% of samples; every competitor fails in ≥ 97%\n46%: all methods fail");
  big(4.75, 1.4, 4.0, 3.9, "(b) Competing line", "RAShR: no failures through 46%\nAt 46%: LMS 60 · LTS/MM 93 · RANSAC 12 · RAShR 0\nRANSAC remains a strong competitor on this geometry");
  big(8.9, 1.4, 3.85, 3.9, "(c) Funnel + line", "40%: RAShR 0 · LMS 25 · LTS 62 · MM 60 · RANSAC 5\n44%: RAShR 3 · LMS 83 · LTS 100 · MM 98 · RANSAC 40\n46%: RAShR 8");
  card(s, MX, 5.5, 12.15, 1.3, "Not a general “near-50%” guarantee", "A finite regime (≈ 35–46%) in which RAShR can stay near the majority line after several established methods have begun to follow the competing structure. All numbers: failure rate in %.", { size: 14, fill: "FFF8F0", line: "F28F3B" });
}
{
  const s = content("Figure 3 geometry: a moving cluster, and the 2.058 plateau", "Evidence");
  img(s, "fig9_cluster_move", MX, 1.3, 7.2, 4.3, "Slope as the 36-point cluster moves horizontally");
  stat(s, 8.3, 1.5, 4.4, "2.058", "RAShR slope once the cluster is far enough (paper's sample)", S.accent1);
  card(s, 8.3, 3.2, 4.45, 3.5, "Reading it", "RAShR's slope becomes exactly constant — consistent with Theorem 1. Residual-based fits (LTS, MM, RANSAC) jump to the cluster when it is closer; each has a different switching point.", { size: 14 });
  cap(s, "Our sample's plateau value differs from 2.058 (different majority sample); constancy is the point.", MX, 5.7, 7.2, 0.6);
}
{
  const s = content("When the advantage disappears", "Evidence");
  img(s, "fig15_directions", MX, 1.3, 6.8, 3.4, "Failure rate by cluster direction");
  img(s, "fig16_spread", 7.6, 1.3, 5.15, 3.4, "Failure rate by cluster spread");
  card(s, MX, 4.9, 6.1, 1.9, "Direction ≈ 30° / −150°", "Cluster on the extension of the majority line. −150° ≡ 30° on the projective circle, so chord directions overlap and separation is lost (paper: 78% and 75% failure at distance 30).", { size: 13, fill: "FFF8F0", line: "F28F3B" });
  card(s, 6.85, 4.9, 5.9, 1.9, "Compactness", "Spread 0.05: RAShR 0 failures, LMS 25%, LTS/MM ≈ 98% (paper). Spread 1 or 3: all fail ≤ 2% — the cluster is no longer a compact coherent group.", { size: 13 });
}

// ================================================================== SUMMARY
{
  const s = pres.addSlide({ masterName: "RASHR_TITLE", sectionTitle: "Evidence" });
  s.addText("When is RAShR useful?", { x: 0.9, y: 0.7, w: 11.5, h: 0.9, fontSize: 40, bold: true, color: S.background1, fontFace: "Cambria", margin: 0, isTextBox: true });
  const cols = [
    ["Use it when", "≈ 35–46% of the data form a compact, coherent structure that is angularly separated from the majority line, and a deterministic estimator is wanted.", "0FA3B1"],
    ["Prefer MM / RANSAC when", "Data are clean or lightly contaminated, contamination is diffuse or arbitrary, or efficiency matters most.", "F28F3B"],
    ["Known limits", "Cluster on the line's extension (≈ 30°, −150°); compact cluster at 46%: all fail; not fully affine equivariant; scales and intercept use all data.", "D1495B"],
  ];
  cols.forEach(([t, b, c], i) => {
    const x = 0.9 + i * 4.0;
    s.addShape(pres.ShapeType.roundRect, { x, y: 2.0, w: 3.75, h: 3.4, rectRadius: 0.12, fill: { color: "17406F" }, line: { color: c, width: 2 }, objectName: "sum-card" + i });
    s.addText(t, { x: x + 0.25, y: 2.15, w: 3.3, h: 0.5, fontSize: 20, bold: true, color: c, margin: 0, isTextBox: true });
    s.addText(b, { x: x + 0.25, y: 2.75, w: 3.3, h: 2.5, fontSize: 16, color: "FFFFFF", margin: 0, valign: "top", isTextBox: true });
  });
  s.addText("direction, not residual → concentrate twice → robust slope", { x: 0.9, y: 5.9, w: 11.5, h: 0.6, fontSize: 22, italic: true, color: "CFE0FA", fontFace: "Cambria", margin: 0, isTextBox: true });
  s.addText("Companions: Manim video · HTML deck · Beamer · notebooks · Streamlit lab", { x: 0.9, y: 6.7, w: 11.5, h: 0.4, fontSize: 14, color: "9FB7DE", margin: 0, isTextBox: true });
}

(async () => {
  const out = path.resolve(__dirname, "rashr_presentation.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("written", out);
})();
