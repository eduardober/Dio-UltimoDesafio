#!/usr/bin/env python3
# Cria arquivos de teste na pasta workdir para simulação.
import os

WORKDIR = "workdir"
os.makedirs(WORKDIR, exist_ok=True)

for i in range(1, 6):
    fname = os.path.join(WORKDIR, f"arquivo_teste_{i}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Arquivo de teste número {i}\n")
        f.write(f"Senha simulada: senha_demo_{i}\n")

print("Arquivos de teste criados na pasta ./workdir/")
