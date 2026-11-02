#!/usr/bin/env bash
# OoT3D PT-BR v2.0 — ativador Linux, codigo aberto.
# Opera apenas em arquivos locais: verifica o O3RO, preserva um backup do
# perfil e adiciona --romfs-overlay ao JSON. Nao baixa arquivos nem altera
# o executavel, a RomFS, os saves ou os pacotes de texturas.
set -euo pipefail
falhar() { printf 'ERRO: %s\n' "$*" >&2; exit 1; }
comando() { command -v "$1" >/dev/null 2>&1 || falhar "Comando necessario nao encontrado: $1"; }
for c in jq sha256sum mktemp chmod mv cat; do comando "$c"; done
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
BASE="${1:-$DIR}"
[[ -d "$BASE" ]] || falhar "Diretorio do TriAevum nao encontrado: $BASE"
BASE="$(cd -- "$BASE" && pwd -P)"
PERFIL="$BASE/data/TriAevum.launch.json"
MOD="$BASE/data/mods/OoT3D-PTBR/OoT3D-PTBR.o3ro"
BACKUP="$PERFIL.backup-antes-ptbr.json"
ESPERADO='4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3'
[[ -f "$PERFIL" ]] || falhar "Perfil nao encontrado: $PERFIL"
[[ -f "$MOD" ]] || falhar "O3RO nao encontrado: $MOD"
ATUAL="$(sha256sum -- "$MOD")"
[[ "${ATUAL%% *}" == "$ESPERADO" ]] || falhar 'SHA-256 do O3RO nao corresponde ao mod validado.'
jq -e '(.arguments | type == "array") and
       (all(.arguments[]; type == "string")) and
       ([.arguments[] | select(. == "--romfs-overlay")] | length <= 1) and
       ((.arguments | index("--romfs-overlay")) as $i |
         $i == null or (($i + 1 < (.arguments | length)) and
         (.arguments[$i + 1] | startswith("--") | not)))' "$PERFIL" >/dev/null \
  || falhar 'Perfil JSON invalido ou argumento --romfs-overlay incompleto/duplicado.'
NOVO="$(mktemp "${PERFIL}.tmp.XXXXXXXX")" || falhar 'Nao foi possivel criar temporario.'
trap 'rm -f -- "$NOVO"' EXIT
jq --arg mod "$MOD" '
  (.arguments | index("--romfs-overlay")) as $i |
  if $i == null then .arguments += ["--romfs-overlay", $mod]
  else .arguments[$i + 1] = $mod end
' "$PERFIL" > "$NOVO" || falhar 'Falha ao gerar novo perfil JSON.'
chmod --reference="$PERFIL" "$NOVO"
if [[ ! -e "$BACKUP" ]]; then
  ( set -C; cat -- "$PERFIL" > "$BACKUP" ) || falhar 'Nao foi possivel criar backup sem sobrescrever o anterior.'
  printf 'Backup criado: %s\n' "$BACKUP"
else
  printf 'Backup existente preservado: %s\n' "$BACKUP"
fi
mv -f -- "$NOVO" "$PERFIL" || falhar 'Nao foi possivel atualizar o perfil.'
trap - EXIT
printf 'Traducao PT-BR ativada com sucesso.\n'
printf 'Perfil: %s\n' "$PERFIL"
printf 'TriAevum, RomFS, saves e texturas pessoais nao foram alterados.\n'
