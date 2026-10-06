import json, base64, io, re
from PIL import Image
from paper_values import PAPER
R = json.load(open("results/simulation_results.json"))
def strip(sc): return {f: {m: {"fail": d["fail"], "med_abs_err": d["med_abs_err"]} for m, d in v.items()} for f, v in sc.items()}
paper = {}
for sc in ["compact", "line", "funnel"]:
    paper[sc] = {f"{f:.2f}": d for f, d in PAPER[sc].items()}
# paper: compact@44% RAShR fails 60% (succeeds 40%); others >=97% -> shown only for RAShR
data = {"fracs": R["fracs"], **{k: strip(R[k]) for k in ["compact", "line", "funnel"]}, "standard": strip(R["standard"]) if False else R["standard"],
        "move": R["move"], "paper": paper}
for k in data["standard"]:
    data["standard"][k] = {m: {"med_abs_err": d["med_abs_err"], "fail": d["fail"]} for m, d in data["standard"][k].items()}
t = open("html/template.html").read()
def img(m):
    im = Image.open(f"figures/{m.group(1)}.png").convert("RGB")
    if im.width > 1500: im = im.resize((1500, int(im.height * 1500 / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
t = re.sub(r"\{\{IMG:(\w+)\}\}", img, t)
t = t.replace("{{DATA}}", json.dumps(data))
open("html/rashr_presentation.html", "w").write(t)
print(len(t)//1024, "KB")
# extract script for node tests
js = re.findall(r"<script>(.*?)</script>", t, re.S)[-1]
open("/tmp/deck.js", "w").write(js)
