# The Legend of Zelda: Ocarina of Time 3D — Tradução PT-BR para TriAevum

Port da tradução brasileira de **The Legend of Zelda: Ocarina of Time 3D** para execução através do **TriAevum**.

O objetivo deste projeto é disponibilizar a tradução completa em PT-BR no port nativo, preservando os textos, menus, interface e recursos gráficos traduzidos, além da compatibilidade com as modificações de interface utilizadas pelo TriAevum.

> **Status:** tradução completa funcionando e instalador V4 validado em uma instalação limpa compatível do TriAevum.

## 🇧🇷 O que está traduzido

- Diálogos e textos do jogo em PT-BR
- Nomes de locais, mensagens e placas
- Menus e interface
- Texturas e elementos gráficos com texto
- Tela de título e recursos da tradução original
- Interface do slot europeu utilizada pelo runtime
- Compatibilidade com TopScreen / Single Screen

## 📥 Download

A versão pública do instalador será disponibilizada na seção **Releases** deste repositório.

> O instalador final ainda está sendo preparado para distribuição. Evite baixar builds ou arquivos de desenvolvimento como se fossem uma versão final.

## 🛠️ Instalação

Quando a primeira versão pública estiver disponível:

1. Tenha uma instalação funcional e compatível do TriAevum para Ocarina of Time 3D.
2. Baixe o instalador mais recente na seção **Releases**.
3. Coloque o instalador na pasta principal do TriAevum.
4. Execute o instalador.
5. Escolha **Instalar tradução**.
6. Após a conclusão, inicie o jogo normalmente pelo TriAevum.

O instalador verifica a instalação antes de aplicar o port e mantém backups dos arquivos necessários para permitir restauração.

## 🔄 Restauração

O instalador possui uma opção para restaurar os arquivos originais salvos antes da instalação da tradução.

Recomendamos não apagar manualmente os arquivos de backup criados pelo instalador enquanto desejar manter essa possibilidade.

## 🎮 Compatibilidade

Este port foi desenvolvido especificamente para a estrutura utilizada pelo **TriAevum** e leva em consideração a adaptação de recursos USA → EUR realizada pelo runtime.

Também foi ajustado para preservar o funcionamento do **TopScreen / Single Screen**, incluindo os recursos de interface que dependem do sistema de substituição de texturas do TriAevum.

Mais informações sobre versões testadas e limitações serão adicionadas em `docs/compatibilidade.md`.

## 📷 Screenshots

Screenshots da tradução rodando no TriAevum serão adicionadas aqui antes do lançamento público.

## ❤️ Créditos

Este projeto é um **port para TriAevum de uma tradução PT-BR existente**. A tradução original não foi criada por este repositório.

Os créditos completos da tradução original e do trabalho de port serão mantidos em [`CREDITOS.md`](CREDITOS.md), no instalador e nos locais exigidos pela autorização concedida para distribuição.

## ⚠️ Aviso importante

Este repositório **não distribui ROM, dump ou cópia de The Legend of Zelda: Ocarina of Time 3D**.

O usuário precisa possuir separadamente os arquivos compatíveis e necessários para executar o jogo. O projeto distribui apenas os componentes do port/tradução cuja distribuição esteja autorizada.

**The Legend of Zelda** e demais marcas relacionadas pertencem aos seus respectivos detentores. Este é um projeto de fãs e não possui afiliação oficial com a Nintendo.

## 🧪 Estado do projeto

- [x] Port dos textos PT-BR
- [x] Port dos recursos gráficos da tradução
- [x] Menus PT-BR no runtime EUR
- [x] Compatibilidade com TopScreen / Single Screen
- [x] Instalação completa validada
- [x] Backup e restauração
- [ ] Interface gráfica do instalador
- [ ] Pacote `.exe` para distribuição
- [ ] Documentação final
- [ ] Release pública v1.0.0

## 📄 Estrutura planejada

```text
OoT3D-PTBR-TriAevum/
├── README.md
├── CREDITOS.md
├── installer/
└── docs/
    ├── instalacao.md
    └── compatibilidade.md
```

---

### Sobre o projeto

O port nasceu da necessidade de adaptar uma tradução originalmente preparada para a estrutura de mods do Citra à forma como o TriAevum organiza e carrega os recursos de Ocarina of Time 3D. O processo incluiu adaptação dos arquivos de mensagem, recursos de interface e compatibilidade com as modificações gráficas do runtime.
