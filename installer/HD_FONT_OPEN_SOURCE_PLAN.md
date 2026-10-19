# Fonte HD PT-BR independente — proposta e critérios de aceite

## Fonte candidata: Noto Sans Regular

A candidata inicial é **Noto Sans Regular**, do projeto Noto Fonts,
sob **SIL Open Font License 1.1 (OFL-1.1)**.
Fontes: https://github.com/google/fonts/tree/main/ofl/notosans
e https://openfontlicense.org/ofl-faq/

Não incluir arquivos SingleScreen/TopScreen, atlas proprietários ou glifos
extraídos de pacotes de terceiros na distribuição. Antes de incorporar uma
versão da Noto Sans, registrar a origem, versão/commit, SHA-256, declaração
de copyright e o texto OFL correspondente. Se o arquivo for modificado,
observar os Reserved Font Names, quando aplicáveis. Conservar avisos e
licença na distribuição.

## Estado atual

- `qbf_coverage.py`: inspeciona códigos de glifos em arquivos QBF1.
- `open_font_probe.py`: valida a cobertura Unicode PT-BR de um TTF/OTF.
- **Ainda não há** conversor TTF→QBF, rasterizador, fonte incorporada,
  patch da ROM, opção na interface ou build HD independente.
- O instalador atual **continua exigindo** `font_coverage.zip` na base beta.
  Não remover a verificação até que uma substituição segura seja testada.

## Verificação de uma fonte local

```sh
python -m pip install fonttools
python installer/open_font_probe.py caminho/para/NotoSans-Regular.ttf
python -m unittest test_qbf_coverage -v
```

## Etapas obrigatórias antes de ativar a função

1. Investigar formato QBF1 real: cabeçalho, índices, bitmaps, ordem dos
   pixels, métricas, mapeamento e limites de memória; não deduzir formato
   somente pelos primeiros 16 bytes.
2. Rasterizar glifos OFL em resolução HD e converter ao QBF com
   métricas compatíveis, sem copiar bitmaps protegidos do jogo.
3. Verificar toda a cobertura original + PT-BR e testar rejeição de
   fontes inválidas, limites e rollback.
4. Comparar screenshots no jogo: acentos, quebras de linha, menus,
   texto corrido e símbolos especiais.
5. Integrar ao instalador com opção clara e fallback seguro.
6. Rodar testes e builds Windows/Linux; só depois abrir PR de integração.

Uma fonte OFL permite redistribuição mediante cumprimento de seus termos;
não implica permissão para redistribuir assets de terceiros.
