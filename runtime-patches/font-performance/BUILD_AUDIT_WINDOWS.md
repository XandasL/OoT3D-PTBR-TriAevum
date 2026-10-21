# Auditoria de build — TriAevum beta.1.1 + A4 HD128 (21/10/2026)

## Escopo / invariantes

Somente checkout temporário de `coccofresco/TriAevum` em `v0.8.0-beta.1.1`, com um único arquivo C++ substituído (`runtime/three_ds_recomp/src/fast/oot3d/pica_texture_decode.cpp`). Branch `test/hd128-decoder-performance`. Não atualizar a fonte, o instalador PT-BR, `main`, os dados do jogo ou qualquer release.

## Auditoria dos três erros observados

| Execução | Erro raiz | Evidência | Correção |
| --- | --- | --- | --- |
| [39605583390](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39605583390) | CMake interpretou `\\a` em um caminho Windows como escape inválido | `CMakeLists.txt:8`, `Invalid character escape '\\a'` | `file(TO_CMAKE_PATH ...)` no teste |
| [39606843530](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39606843530) | Runner não tinha headers/loader Vulkan | `Could NOT find Vulkan (missing: Vulkan_LIBRARY Vulkan_INCLUDE_DIR)` | vcpkg instala `vulkan-headers` e `vulkan-loader` no checkout isolado |
| [39608798108](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39608798108) | CMake exige shaderc, além de Vulkan; dependência não existia | `runtime/three_ds_recomp/CMakeLists.txt:138` `THREE_DS_RECOMP_SHADERC_INCLUDE_DIR` | vcpkg instala shaderc em triplet DLL e configura caminhos obrigatórios |

Todas as falhas aconteceram **antes de compilar o executável final**. Não são evidência de erro no decodificador otimizado.

## Contrato real extraído da tag do TriAevum

1. `CMakeLists.txt` impõe Windows x64, C++20, vcpkg e bibliotecas zlib, bzip2, libzip, libpng, SDL2, GLEW, GLFW, nlohmann-json, tinyxml2, spdlog, libogg, libvorbis, opus e opusfile.
2. Vulkan é obrigatório para o renderer desse produto: `find_package(Vulkan REQUIRED)` em `runtime/three_ds_recomp/CMakeLists.txt:134`. Só fornecer `Vulkan::Vulkan` não resolve shaderc.
3. Shaderc requer três itens independentes: `shaderc/shaderc.hpp`, `shaderc_shared.lib` e `shaderc_shared.dll` (`runtime/three_ds_recomp/CMakeLists.txt:138–166`). Por isso o estágio do CI deve conferir presença dos três.
4. `OOT3D_DIRECT_AOT_PLUGIN=ON` habilita as dependências e a ligação oficial de `triaevum_title_aot_stub` com o executável (`CMake/oot3d/game.cmake`); a biblioteca de bootstrap não contém o título do usuário e **não pode ser distribuída como substituta de um módulo Forge real**.
5. O alvo oficial `triaevum_public_runtime` agrega executável e stub. O manifesto gerado por CMake `triaevum-runtime-targets-Release.json` registra caminhos reais do executável, módulo bootstrap e eventuais SDKs; não adivinhar diretórios da saída.
6. A lista de distribuição de referência `tools/triaevum_release/runtime_release_layout.example.json` contém explicitamente `shaderc_shared.dll`, biblioteca de título, recursos e licenças. Para o nosso objetivo o artefato é um **overlay de teste**, não um instalador nem pacote completo: incluir somente executável alterado, bibliotecas não privadas necessárias, checksum e instruções, usando os arquivos de uma instalação já preparada pelo Forge.
7. O projeto tem dependências condicionais pesadas de NRI, FidelityFX, CACAO, iMMERSE, DLSS e SDKs. Não desativá-las silenciosamente para esconder falhas: mudaria o runtime e prejudicaria um teste A/B fiel da fonte. Qualquer ausência ou incompatibilidade nova precisa ser registrada com sua configuração específica.
8. A DLL compartilhada shaderc pode ser obtida pela triplet vcpkg dinâmica `x64-windows`, distinta do conjunto normal `x64-windows-static`. Nunca presumir um arquivo apenas por seu nome no repositório: o build deve verificar sua existência real antes de empacotar.
9. O teste 33 casos de decodificação A4 já passou em Windows e Linux no run [39606843354](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39606843354). Esse teste NÃO confirma melhoria de desempenho no runtime.

## Gate e validação da próxima compilação

**Preflight:** confirmar SDK/toolchain CMake, modo VS2022 x64, triplets vcpkg, caminhos de Vulkan e shaderc e parâmetros de AOT. Falhar antes do compile com mensagem e diagnóstico, sem fabricar pacote.

**Build:** aceitar apenas `triaevum_public_runtime` completo; não renomear alvos ou adicionar stubs improvisados; conferir o manifesto gerado.

**Empacotamento:** copiar `TriAevum.exe` identificado pelo manifesto e `shaderc_shared.dll` requerido. Não publicar a biblioteca de bootstrap vazia (`triaevum_title_aot.dll`) nem arquivos privados, ROM, salvamentos ou o perfil da instalação.

**Uso:** aplicar apenas sobre uma **cópia descartável** de beta.1.1, preservando o `triaevum_title_aot.dll` já preparado no Forge do usuário. Não afirmar que o arquivo é executável com qualquer instalação até ser testado.

**Aceitação de desempenho:** mesmo save e sequência de 2400 frames, caches aquecidos, ordem A/B invertida, FPS, p95/p99, frames >33ms, WASAPI underruns, contagens de reconstrução e hash/capturas dos pixels. `NativeHdFontRuntime::Resolve` continua capaz de reconstruir o atlas inteiro; A4→RGBA rápido isoladamente pode não resolver upload/sincronização GPU.

**Limite epistemológico:** não é possível garantir compilação integral sem executar a compilação; a auditoria identifica os pré-requisitos e as falhas observáveis e reduz tentativas cegas. Próximo erro real do build deve vir acompanhado do log, não de alteração especulativa.
