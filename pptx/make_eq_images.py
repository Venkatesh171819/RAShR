"""Typeset every display formula of the deck as a transparent PNG (matplotlib mathtext, STIX fonts) so that
hats, subscripts and fractions look identical in PowerPoint, Keynote and LibreOffice."""
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
plt.rcParams["mathtext.fontset"] = "stix"
EQ = {
 "strip":  r"$W(\ell)=\inf\{\,w:\ \Pr(|Y-\ell(X)|\leq w)\geq\frac{1}{2}\,\}$",
 "rm":     r"$\hat{\beta}_{\mathrm{RM}}=\mathrm{med}_{i}\ \mathrm{med}_{j\neq i}\ \dfrac{y_j-y_i}{x_j-x_i}$",
 "std":    r"$u_i=\dfrac{x_i-\mathrm{med}\,x}{s_x},\quad v_i=\dfrac{y_i-\mathrm{med}\,y}{s_y},\quad s=1.4826\cdot\mathrm{MAD}$",
 "phi":    r"$\varphi_{ij}=\mathrm{atan2}(v_j-v_i,\ u_j-u_i)\ \mathrm{mod}\ \pi$",
 "dpi":    r"$d_\pi(a,b)=\min\{\,|a-b|,\ \pi-|a-b|\,\}$",
 "ash":    r"$\mathrm{ASh}_h(A)=\frac{1}{2}\left(a_{(r^\star)}+a_{(r^\star+h-1)}\right)\ \mathrm{mod}\ \pi,\quad h=\lceil m/2\rceil$",
 "local":  r"$\Phi_i=\{\varphi_{ij}:j\neq i\},\quad \theta_i=\mathrm{ASh}(\Phi_i),\quad w_i=\mathrm{width}$",
 "outer":  r"$\hat{\theta}=\mathrm{ASh}\{\theta_1,\ldots,\theta_n\}$",
 "slope":  r"$\hat{\beta}=\dfrac{s_y}{s_x}\tan\hat{\theta},\qquad \hat{\alpha}=\mathrm{med}_i\,(y_i-\hat{\beta}x_i),\qquad \hat{y}=\hat{\alpha}+\hat{\beta}x$",
 "equiv":  r"$x'=a_x+b_xx,\ \ y'=a_y+b_yy\ \ (b_x,b_y>0)\ \Rightarrow\ \hat{\beta}'=\dfrac{b_y}{b_x}\hat{\beta}$",
 "thm1":   r"$\hat{\theta}=\mathrm{ASh}_{h_O}\{\,\mathrm{ASh}_{h_L}(\Phi_i^{G}):\ i\in G\,\}$",
 "chip_theta": r"$\hat{\theta}$", "chip_tan": r"$\tan\hat{\theta}$", "chip_sy": r"$\times\ s_y$", "chip_sx": r"$\div\ s_x$", "chip_beta": r"$\hat{\beta}$ (slope)", "chip_beta_w": r"$\hat{\beta}$ (slope)",
}
dims = {}
for k, s in EQ.items():
    fig = plt.figure(figsize=(0.1, 0.1)); fig.patch.set_alpha(0)
    fig.text(0, 0, s, fontsize=26 if not k.startswith("chip") else 20, color=("#FFFFFF" if k.endswith("_w") else "#10213A"))
    fig.savefig(f"../figures/eq_{k}.png", dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=True); plt.close(fig)
    from PIL import Image
    dims[k] = Image.open(f"../figures/eq_{k}.png").size
json.dump(dims, open("../figures/eq_dims.json", "w")); print(dims)
