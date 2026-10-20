# Cobertura HD 128 aprovada no teste local

Este diretório contém apenas o bitmap de cobertura A4 de 128 × 128 por glifo
e seu contrato de integridade. Não contém QBF nativo, ROM, executável,
atlas SingleScreen, Henriko, PNG de UI ou Noto Sans.

Proveniência: cobertura produzida no estudo SVG de 128 do projeto e aprovada
pelo usuário no jogo. Extraída do `font_coverage.zip` local aprovado, separando
os pixels HD da fonte nativa. O QBF nativo continua sendo lido dos dados do
usuário durante a instalação; caracteres, índices e métricas são preservados.

SHA-256 da cobertura QBF reconstruída:
`6923bff33e4df8da6d393d37f46d3298b12cb3e6f5cc2f492f9161bcec9b6b97`.

O contrato verifica fonte nativa, diretório, bitmap e cobertura reconstruída.
Não substituir esse asset pela fonte HD 64 do SingleScreen ou por upscale.
O bitmap representa 208 posições; o diretório nativo tem 199 entradas.
A autorização de distribuição da tradução continua documentada nos créditos
do projeto. A inclusão desta cobertura não inclui assets de packs externos.
