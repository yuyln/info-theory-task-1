import os
import subprocess as sp

def gen_tree(bdir: str, depth: int = -1) -> tuple[str]:
    if not bdir.endswith("/"): bdir += "/"
    entries = [(i, bdir) for i in os.scandir(bdir)]
    files = []
    while len(entries) > 0:
        entry, path = entries.pop()
        if not path.endswith("/"): path += "/"
        if entry.is_dir():
            for d in os.scandir(entry):
                entries.append((d, path + entry.name))
        else:
            files.append(path + entry.name)
    return files

files_all = [i[2:] for i in gen_tree("./")]
files_all = [i for i in files_all if not ".git" in i]
files = [i for i in files_all if i.endswith(".pdf") and ".bak" in i]
for i in files:
    local = i.split(".bak.pdf")[0]
    print(i, local)
    sp.run(["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", "-dCompressFonts=true", "-dPDFSETTINGS=/prepress", f"-sOutputFile={local}.pdf", i])
