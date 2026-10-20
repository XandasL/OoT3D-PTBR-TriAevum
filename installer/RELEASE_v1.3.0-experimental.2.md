# Tradução PT-BR v1.3.0 experimental.2 — TriAevum beta.1.1

## Texto para a pré-release

Tradução completa de Ocarina of Time 3D para TriAevum v0.8.0-beta.1.1,
com os textos e as texturas nativas em português. Permite escolher a fonte
original do jogo ou a fonte HD 128.

Se a instalação for interrompida, basta abrir o instalador e clicar novamente
em **Instalar / aplicar fonte**. O processo verifica a operação anterior,
recupera os dados íntegros e aplica a escolha atual. **Restaurar original**
também retoma operações interrompidas. Estados divergentes são preservados
para revisão, sem sobrescrever alterações externas.

O instalador mantém o RomFS original e cria os dados traduzidos separadamente.
Saves, executáveis, ajustes gráficos e packs de terceiros são preservados.
A tradução das texturas nativas continua disponível sem pack HD.

O Henriko é instalado e configurado separadamente no TriAevum. Para o pack
original 5.0a, o arquivo opcional de compatibilidade disponível na pasta
`compatibility/henriko-5.0a-ptbr-v1.3.0` permite que suas imagens em inglês
substituam as texturas traduzidas correspondentes. Ele não inclui imagens.
Não há importação do SingleScreen nem layout PlayStation nesta versão.

### Como testar

1. Use inicialmente uma cópia da instalação preparada pelo Forge beta.1.1.
2. Abra o instalador Windows ou Linux e selecione a pasta do TriAevum.
3. Escolha **Original do jogo** ou **Fonte HD 128** e instale com o jogo fechado.
4. Para trocar a fonte, selecione a outra opção e instale novamente.
5. Para remover a tradução e recuperar a fonte anterior, use **Restaurar original**.

Restaure instalações de versões antigas com o instalador correspondente antes
de migrar, caso o novo instalador informe incompatibilidade.

### Validação e limites

- 24 testes automatizados, incluindo interrupções, recuperação e recusa de alterações externas.
- Builds Windows e Linux com testes do executável empacotado aprovados no GitHub Actions.
- Windows: fluxo de instalação da GUI exercitado com RomFS real, 126 recursos
  traduzidos, fonte original e HD 128, retomada após ativação interrompida e
  restauração interrompida. Perfil e fonte anteriores restaurados exatamente;
  save, configuração, pack e RomFS original preservados.
- O RomFS traduzido continua idêntico ao validado anteriormente no jogo.
  Esta rodada não repetiu a execução do jogo nem a inspeção visual da GUI;
  exercitou seus workers de instalação/restauração e o autoteste Tk do executável.
- Linux ainda não tem validação de jogo. Nem todos os menus/cenários foram
  conferidos visualmente. Não há certificação contra falhas físicas de disco/energia.

## Preparação da publicação

Estado: **pronta para criar uma pré-release; nenhuma release ou tag publicada**.

- Tag proposta: `v1.3.0-experimental.2`.
- Commit dos binários: `d3ae51bc9c6e3bb679c6755569e7060578781cf0`.
- Branch: `feat/v1.3.0-full-ptbr-native-textures`.
- [Build Windows/Linux aprovada](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39510581440).
- [Safety smoke aprovado](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39510581445).
- Artefatos CI: `OoT3D-PTBR-v1.3.0-experimental.2-Windows` (12305981458) e
  `OoT3D-PTBR-v1.3.0-experimental.2-Linux` (12305531774).
- Ao publicar, extrair os artefatos CI e anexar os ZIPs de distribuição e seus
  arquivos `.sha256`. Manter o relatório de autoteste como evidência.
- Compatibilidade Henriko: pode ser anexada separadamente como ZIP de
  `pack.json` e instruções, sem PNGs. Não mesclar no instalador.
- Os hashes do pacote local e do CI podem diferir: conferir cada pacote com
  o `.sha256` gerado pela mesma build. O relatório local está em
  `V1.3.0_EXPERIMENTAL2_VALIDACAO.json`.

Até a publicação, os bloqueios de release dos documentos experimentais anteriores
continuam em vigor. Estes resultados permitem preparar a primeira pré-release;
não promovem o protótipo a versão estável nem alteram a compatibilidade declarada.
