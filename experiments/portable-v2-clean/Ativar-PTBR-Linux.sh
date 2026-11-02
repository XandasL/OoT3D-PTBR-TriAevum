#!/usr/bin/env bash
set -euo pipefail
# Ativador aberto e local. Nao baixa arquivos, nao instala dependencias.
# O diretorio padrao e a pasta onde este arquivo foi extraido.
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="${1:-$HERE}"
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERRO: Python 3.11+ e necessario para ativar a traducao." >&2
  exit 1
fi
python3 "$HERE/ativar_ptbr_linux.py" --runtime "$RUNTIME"
