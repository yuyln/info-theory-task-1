def FixPlot(lx: float, ly: float):
    from matplotlib import rcParams, cycler
    rcParams["font.family"] = "serif"
    rcParams["font.serif"] = ["Computer Modern"]
    rcParams["text.latex.preamble"] = "\\usepackage{libertine}\n\\usepackage{libertinust1math}"
    rcParams["text.usetex"] = True
    rcParams["font.size"] = 28
    rcParams["axes.linewidth"] = 1.1
    rcParams["axes.labelpad"] = 10.0
    plot_color_cycle = cycler("color", ["000000", "FE0000", "0000FE", "008001", "FD8000", "8c564b",
                                        "e377c2", "7f7f7f", "bcbd22", "17becf"])
    rcParams["axes.prop_cycle"] = plot_color_cycle
    rcParams["axes.xmargin"] = 0
    rcParams["axes.ymargin"] = 0
    rcParams["legend.fancybox"] = False
    rcParams["legend.framealpha"] = 1.0
    rcParams["legend.edgecolor"] = "black"
    rcParams["legend.fontsize"] = 22
    rcParams["xtick.labelsize"] = 22
    rcParams["ytick.labelsize"] = 22

    rcParams["ytick.right"] = True
    rcParams["xtick.top"] = True

    rcParams["xtick.direction"] = "in"
    rcParams["ytick.direction"] = "in"
    rcParams["axes.formatter.useoffset"] = False

    rcParams.update({"figure.figsize": (lx, ly),
                    "figure.subplot.left": 0.177, "figure.subplot.right": 0.946,
                     "figure.subplot.bottom": 0.156, "figure.subplot.top": 0.965,
                     #"axes.autolimit_mode": "round_numbers",
                     "xtick.major.size": 7,
                     "xtick.minor.size": 3.5,
                     "xtick.major.width": 1.1,
                     "xtick.minor.width": 1.1,
                     "xtick.major.pad": 5,
                     "xtick.minor.visible": True,
                     "ytick.major.size": 7,
                     "ytick.minor.size": 3.5,
                     "ytick.major.width": 1.1,
                     "ytick.minor.width": 1.1,
                     "ytick.major.pad": 5,
                     "ytick.minor.visible": True,
                     "lines.markersize": 10,
                     "lines.markeredgewidth": 0.8,
                     "mathtext.fontset": "cm"})
