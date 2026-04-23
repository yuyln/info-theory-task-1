from unidecode import unidecode
import re
from math import log2
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import sys
import os
import subprocess as sp
from matplotlib import rcParams, cycler

FixPlot = lambda lx, ly: rcParams.update({"figure.figsize": (lx, ly)})
try:
    from plot import FixPlot as FixPlot_
    FixPlot = FixPlot_
except:
    pass

def fix_fig(path: str):
    local = path.split(".bak.pdf")[0]
    sp.run(["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", "-dCompressFonts=true", "-dPDFSETTINGS=/prepress", f"-sOutputFile={local}.pdf", path])

IGNORE_SPACE = True
def normalize(data: str) -> str:
    data = unidecode(data)
    data = data.lower()
    for i in range(0xff):
        if not (0x61 <= i <= 0x7a or i == 0x20):
            data = data.replace(chr(i), " ") #removes everything that is not lowercase ascii characters and spaces
    data = re.sub(" +", " ", data)
    if IGNORE_SPACE:
        data = data.replace(" ", "")

    return data

letters = [*[f"{chr(ord('a') + i)}" for i in range(26)], " "]
if IGNORE_SPACE:
    letters.pop()

languages = ["br", "en", "fr", "it", "de", "es"]
mapping = {"br": "Português",
           "en": "Inglês",
           "es": "Espanhol",
           "de": "Alemão",
           "it": "Italiano",
           "fr": "Francês",}

p1 = {l: {i: 0 for i in letters} for l in languages}
p2 = {l: {i: {j: 0 for j in letters} for i in letters} for l in languages}

def p(l: str, a: str, b: str = "") -> float:
    if b == "":
        return p1[l][a]
    if b[0] == "|":
        return p2[l][b[1]][a]
    return p1[l][b] * p2[l][b][a]

def info(l: str, a: str, b: str = "") -> float:
    if p(l, a, b) < 1e-15:
        return 0
    return -log2(p(l, a, b))

def H(l: str, cond: bool = False) -> float:
    H = 0
    if cond == False:
        for c in letters:
            H -= p(l, c) * log2(p(l, c))
    else:
        for c in letters:
            for c2 in letters:
                if p(l, c, "|"+c2) > 0:
                    H -= p(l, c, c2) * log2(p(l, c, "|"+c2))
    return H

def KLD(l1: str, l2: str) -> float:
    D = 0
    for c in letters:
        D += p(l1, c) * log2(p(l1, c) / p(l2, c))
    return D


for l in languages:
    data = ""
    try:
        with open(f"livro-{l}.txt", "r") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Language {l} not found, skipping")
        continue

    data = normalize(data)
    n = len(data)
    for idx in range(0, n):
        c = data[idx]
        p1[l][c] += 1
        if idx + 1 < n:
            c2 = data[idx + 1]
            p2[l][c][c2] += 1 # p(c2|c)
    for c1 in letters:
        p1[l][c1] /= n
        total_p2 = 0
        for c2 in letters:
            total_p2 += p2[l][c1][c2]
        for c2 in letters:
            p2[l][c1][c2] /= (total_p2 + 1e-15)

def make_fig1():
    norm_ls = mpl.colors.Normalize(vmin=0, vmax=len(languages) - 1, clip=False)
    map_ls = cm.ScalarMappable(norm=norm_ls, cmap=mpl.colormaps["rainbow"])
    letters_order = letters.copy()
    letters_order.sort(key=lambda x: p("br", x), reverse=True)
    x = np.arange(len(letters_order))
    width = 0.15
    multiplier = 0

    FixPlot(24, 8)
    fig, ax = plt.subplots(nrows=2)

    for idx, l in enumerate(languages):
        offset = width * multiplier
        ps = [p(l, x) for x in letters_order]
        i_s = [info(l, x) for x in letters_order]
        rects = ax[0].bar(x + offset, ps, width, label=mapping[l], color=map_ls.to_rgba(idx))
        rects = ax[1].bar(x + offset, i_s, width, label=mapping[l], color=map_ls.to_rgba(idx))
        multiplier += 1

    for i in range(len(letters_order)):
        if letters_order[i] == " ":
            letters_order[i] = "``space''"
    ax[0].set_ylabel("$p(c)$")
    ax[1].set_ylabel("$I(c)$ [bit]")
    ax[0].legend(ncols=6)
    for i in range(2):
        ymin = np.min(ax[i].get_ylim())
        ymax = np.max(ax[i].get_ylim())

        y_mean = (ymax + ymin) / 2.0
        y_diff = ymax - ymin

        ymin = y_mean - y_diff / 2.0 * 2
        ymin = 0
        ymax = y_mean + y_diff / 2.0 * 2
        ax[i].set_ylim((ymin, ymax))

        ax[i].set_xticks(x + 2.5 * width, letters_order)
        ax[i].tick_params(axis="x", which="minor", bottom=False, top=False)
        ax[i].text(0.01, 0.95, f"({chr(ord('a') + i)})", ha="left", va="top", transform=ax[i].transAxes)

    fig.savefig("fig1.bak.pdf", facecolor="white", bbox_inches="tight", dpi=275)
    fix_fig("fig1.bak.pdf")

def make_fig2():
    norm_ps = mpl.colors.Normalize(vmin=0, vmax=1, clip=False)
    map_ps = cm.ScalarMappable(norm=norm_ps, cmap=mpl.colormaps["jet"])
    letters_order = letters.copy()
    letters_order.sort(key=lambda x: p("br", x), reverse=True)
    x = np.arange(len(letters_order))

    FixPlot(3 * 8, 2 * 8)
    fig, ax = plt.subplots(nrows=2, ncols=3)
    for idx, l in enumerate(languages):
        row = idx // 3
        col = idx % 3
        data = np.zeros((len(letters), len(letters)))
        for i, c1 in enumerate(letters):
            for j, c2 in enumerate(letters):
                data[i, j] = p(l, c1, "|"+c2)
        ax[row, col].imshow(data, cmap=map_ps.get_cmap(), norm=norm_ps, origin="lower")
        ax[row, col].set_aspect(1)
        ax[row, col].text(0.5, 1.01, mapping[l], transform=ax[row, col].transAxes, ha="center", va="bottom")
        ax[row, col].set_xticks(np.arange(len(letters)))
        ax[row, col].set_yticks(np.arange(len(letters)))
        ax[row, col].set_xticklabels([])
        ax[row, col].set_yticklabels([])
        ax[row, col].tick_params(axis="both", which="minor", bottom=False, top=False, left=False, right=False)
        ax[row, col].text(0.01, 0.99, f"({chr(ord('a') + row * 3 + col)})", ha="left", va="top", transform=ax[row, col].transAxes, color="white")
        ax[row, col].set_ylabel("$c_1$")
        ax[row, col].set_xlabel("$c_2$")
        ax[row, col].set_xticklabels(letters)
        ax[row, col].set_yticklabels(letters)
    fig.subplots_adjust(hspace=0.2, wspace=0.2)

    pos0 = ax[0, 0].get_position()
    pos1 = ax[0, -1].get_position()
    dx = pos1.x1 - pos0.x0
    dy = 0.025
    pad = 0.05
    bar = fig.add_axes((pos0.x0, pos0.y1 + pad, dx, dy))
    cbar = fig.colorbar(map_ps, cax=bar, location="top")
    cbar.set_label("$p(c_1|c_2)$")

    fig.savefig("fig2.bak.pdf", facecolor="white", bbox_inches="tight", dpi=275)
    fix_fig("fig2.bak.pdf")

def make_fig3():
    FixPlot(12, 12)
    fig, ax = plt.subplots()
    ls = [mapping[l] for l in languages]
    hs = [H(l) for l in languages]
    hs_cond = [H(l, True) for l in languages]
    print(hs)
    print(hs_cond)
    print(ls)

    ax.bar(ls, hs, color="#ff0000", label="$H(X)$")
    ax.bar(ls, hs_cond, color="#8000ff", label="$H(X|Y)$")
    ax.legend()
    ax.set_ylabel("$H$ [bit]")
    ax.set_ylim((0, 5))
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_aspect(np.ptp(ax.get_xlim()) / np.ptp(ax.get_ylim()))
    fig.savefig("fig3.bak.pdf", facecolor="white", bbox_inches="tight", dpi=275)
    fix_fig("fig3.bak.pdf")

def make_fig4():
    FixPlot(12, 12)
    fig, ax = plt.subplots()
    ls = [mapping[l] for l in languages]
    ds = np.zeros((len(ls), len(ls)))
    for i, l1 in enumerate(languages):
        for j, l2 in enumerate(languages):
            ds[i, j] = KLD(l2, l1)

    norm_ds = mpl.colors.Normalize(vmin=0, vmax=ds.max(), clip=False)
    map_ds = cm.ScalarMappable(norm=norm_ds, cmap=mpl.colormaps["rainbow"])
    ax.imshow(ds, cmap=map_ds.get_cmap(), norm=norm_ds, origin="lower")
    ax.set_xticks(np.arange(len(ls)))
    ax.set_yticks(np.arange(len(ls)))
    ax.set_xticklabels(ls)
    ax.set_yticklabels(ls)
    ax.set_xlabel("$q$")
    ax.set_ylabel("$p$")

    pos0 = ax.get_position()
    pos1 = ax.get_position()
    dx = pos1.x1 - pos0.x0
    dy = 0.025
    pad = 0.05
    bar = fig.add_axes((pos0.x0, pos0.y1 + pad, dx, dy))
    cbar = fig.colorbar(map_ds, cax=bar, location="top")
    cbar.set_label("$D(q||p)$")
    print(KLD("en", "br"))

    fig.savefig("fig4.bak.pdf", facecolor="white", bbox_inches="tight", dpi=275)
    fix_fig("fig4.bak.pdf")

def make_fig5():
    norm_ls = mpl.colors.Normalize(vmin=0, vmax=len(languages) - 1, clip=False)
    map_ls = cm.ScalarMappable(norm=norm_ls, cmap=mpl.colormaps["rainbow"])
    FixPlot(6, 6)
    fig = plt.figure()
    axs = []
    pad_x = 0.25
    pad_y = 0.2
    for idx, l in enumerate(languages):
        if len(axs) == 0:
            axs.append(fig.add_axes((0, 0, 1, 1)))
        else:
            pos = axs[-1].get_position()
            dx = pos.x1 - pos.x0
            dy = pos.y1 - pos.y0
            if idx % 3 == 0:
                axs.append(fig.add_axes((0, pos.y0 - dy - pad_y, dx, dy)))
            else:
                axs.append(fig.add_axes((pos.x1 + pad_x, pos.y0, dx, dy)))

        ax = axs[-1]

        letters_order = letters.copy()
        letters_order.sort(key = lambda x: p(l, x))
        ps_l1 = [p(l, x) for x in letters_order]

        ax.text(0.5, 0.95, mapping[l], ha="center", va="top", transform=ax.transAxes)
        ax.text(0.9, 0.95, f"({chr(ord('a') + idx)})", ha="right", va="top", transform=ax.transAxes)
        for jdx, l2 in enumerate(languages):
            s = 100
            ps_l2 = [p(l2, x) for x in letters_order]
            zorder = 1
            if l2 == l: zorder = 0

            ax.scatter(ps_l1, ps_l2, s=s, color=map_ls.to_rgba(jdx), label=l2, zorder=zorder)

        ax.set_xlabel("$p$")
        ax.set_ylabel("$q$")
        ax.set_xlim((0, 0.2))
        ax.set_ylim((0, 0.2))
        ax.set_yticks(ax.get_xticks())
        yx = np.linspace(*ax.get_xlim())
        ax.plot(yx, yx, "--", lw=2)
        ax.set_aspect(np.ptp(ax.get_xlim()) / np.ptp(ax.get_ylim()))

    axs[0].legend()
    pos0 = axs[1].get_position()
    pos1 = axs[5].get_position()
    dx = pos1.x1 - pos0.x0
    dy = -(pos1.y0 - pos0.y1)
    axs.append(fig.add_axes((pos1.x1 + pad_x * 2, pos1.y0, dx, dy)))

    data = np.zeros((len(languages), len(languages)))
    for i, l1 in enumerate(languages):
        letters_order = letters.copy()
        letters_order.sort(key = lambda x: p(l1, x))
        ps_l1 = [p(l1, x) for x in letters_order]
        for j, l2 in enumerate(languages):
            ps_l2 = [p(l2, x) for x in letters_order]
            data[i, j] = KLD(l1, l2)#pearsonr(ps_l1, ps_l2).statistic

    ax = axs[-1]
    im = ax.imshow(data, origin="lower", cmap="rainbow")
    ax.set_xticks(np.arange(len(languages)))
    ax.set_yticks(np.arange(len(languages)))
    ax.set_xticklabels([mapping[l] for l in languages])
    ax.set_yticklabels([mapping[l] for l in languages])
    ax.set_xlabel("$p$")
    ax.set_ylabel("$q$")
    ax.text(-0.05, 0.99, "(g)", ha="left", va="top", transform=ax.transAxes)
    ax.set_aspect(1)

    pos0 = ax.get_position()
    pos1 = ax.get_position()
    dx = pos1.x1 - pos0.x0
    dy = 0.05
    pad = 0.05
    bar = fig.add_axes((pos0.x0, pos0.y1 + pad, dx, dy))
    cbar = fig.colorbar(im, cax=bar, location="top")
    cbar.set_label("$D(q||p)$")

    fig.savefig("fig5.bak.pdf", facecolor="white", bbox_inches="tight", dpi=275)
    fix_fig("fig5.bak.pdf")

if "fig1" in sys.argv:
    make_fig1()
if "fig2" in sys.argv:
    make_fig2()
if "fig3" in sys.argv:
    make_fig3()
if "fig4" in sys.argv:
    make_fig4()
if "fig5" in sys.argv:
    make_fig5()
