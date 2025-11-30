#!/usr/bin/env python3
# Restaura arquivos ".encsim" gerados pela simulação.
# Decodifica o base64 e recria o conteúdo original.

import os
import base64

WORKDIR = "workdir"

for fname in os.listdir(WORKDIR):
    if fname.endswith(".encsim"):
        path = os.path.join(WORKDIR, fname)

        with open(path, "r", encoding="utf-8") as f:
            header = f.readline()
            encoded = f.read()

        try:
            data = base64.b64decode(encoded)
            original_name = path.replace(".encsim", "")

            with open(original_name, "wb") as f_out:
                f_out.write(data)

            os.remove(path)
            print("Arquivo restaurado:", original_name)

        except Exception as e:
            print("Erro ao restaurar:", path, e)
