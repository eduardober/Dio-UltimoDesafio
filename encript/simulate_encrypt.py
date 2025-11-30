#!/usr/bin/env python3
# Simulação segura de ransomware: não usa criptografia real, apenas base64.
# Opera estritamente dentro da pasta "workdir".

import os
import base64

WORKDIR = "workdir"
ALLOWED_EXT = [".txt", ".log", ".md"]

def safe_path(path):
    # Garante que o script nunca saia da pasta de laboratório
    return os.path.abspath(path).startswith(os.path.abspath(WORKDIR))

os.makedirs(WORKDIR, exist_ok=True)

for fname in os.listdir(WORKDIR):
    fpath = os.path.join(WORKDIR, fname)

    if not safe_path(fpath):
        print("Ignorado (fora do workdir):", fpath)
        continue

    if os.path.isfile(fpath) and any(fname.endswith(ext) for ext in ALLOWED_EXT):
        with open(fpath, "rb") as f:
            data = f.read()

        encoded = base64.b64encode(data).decode("utf-8")
        newname = fpath + ".encsim"

        with open(newname, "w", encoding="utf-8") as nf:
            nf.write("SIM_ENCRIPTADO\n")
            nf.write(encoded)

        os.remove(fpath)
        print("Arquivo simulado como criptografado:", newname)

# cria nota de resgate educacional
with open(os.path.join(WORKDIR, "nota_de_resgate.txt"), "w", encoding="utf-8") as rn:
    rn.write("=== Finalizado ===\n")

print("Simulação concluída!")
