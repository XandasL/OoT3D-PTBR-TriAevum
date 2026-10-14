# -*- coding: utf-8 -*-
"""
Instalador v1.2.0 da tradução PT-BR de Ocarina of Time 3D para TriAevum.
Alvo: TriAevum v0.8.0-beta.1; base alpha.2c preservada. Linux pendente de validação no jogo.
Preparado para distribuição como executável único (PyInstaller one-file).
"""

import contextlib
import importlib.util
import io
import os
import sys
import traceback
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText


APP_VERSION = "1.2.0"
APP_TITLE = "Tradução PT-BR / TriAevum v0.8.0-beta.1"
CORE_FILENAME = "Instalador_Traducao_PTBR_OoT3D_V4_compat_test.py"
PAYLOAD_RELATIVE = Path("TraducaoCompleta") / "citra" / "romfs"


def app_dir() -> Path:
    """Pasta real do script/EXE."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def bundled_dir() -> Path:
    """Pasta dos recursos embutidos pelo PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent


def hd_module():
    path = bundled_dir() / "hd_textures.py"
    spec = importlib.util.spec_from_file_location("ptbr_hd_extension", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hd_bundle():
    for path in (bundled_dir() / "hd-runtime", app_dir() / "hd-runtime",
                 Path(__file__).resolve().parent.parent / "build" / "hd-runtime"):
        if (path / "manifest.json").is_file():
            return path
    return None


def is_triaevum_root(path: Path) -> bool:
    if not path.is_dir() or not (path / "data").is_dir():
        return False

    if (path / "TriAevum.launch.json").is_file():
        return True

    try:
        return any(p.is_file() for p in path.glob("TriAevum*.exe"))
    except OSError:
        return False


def detect_triaevum_root(start: Path) -> Path | None:
    """
    Procura a raiz começando pela pasta da GUI e subindo pelos pais.
    Funciona tanto com:
      raiz/installer/GUI.py
    quanto com:
      raiz/GUI.exe
    """
    candidates = [start, *start.parents]
    for candidate in candidates:
        if is_triaevum_root(candidate):
            return candidate
    if sys.platform == "linux":
        data_home = os.environ.get("XDG_DATA_HOME", "")
        linux_candidates = [
            (Path(data_home) / "TriAevum") if data_home and Path(data_home).is_absolute() else Path.home() / ".local/share/TriAevum",
            Path.home() / ".var/app/io.github.coccofresco.TriAevum/data/TriAevum",
        ]
        matches = [path for path in linux_candidates if is_triaevum_root(path)]
        if len(matches) == 1:
            return matches[0]
    return None


def locate_core(gui_dir: Path, root: Path | None) -> Path | None:
    candidates = [
        bundled_dir() / CORE_FILENAME,
        gui_dir / CORE_FILENAME,
    ]
    if root:
        candidates += [
            root / "installer" / CORE_FILENAME,
            root / CORE_FILENAME,
        ]

    seen = set()
    for p in candidates:
        key = str(p)
        if key not in seen:
            seen.add(key)
            if p.is_file():
                return p
    return None


def locate_payload(gui_dir: Path, root: Path | None) -> Path | None:
    candidates = [
        bundled_dir() / PAYLOAD_RELATIVE,
        gui_dir / PAYLOAD_RELATIVE,
    ]
    if root:
        candidates += [
            root / "installer" / PAYLOAD_RELATIVE,
            root / PAYLOAD_RELATIVE,
        ]

    seen = set()
    for p in candidates:
        key = str(p)
        if key not in seen:
            seen.add(key)
            if p.is_dir():
                return p
    return None


def import_core(core_path: Path):
    spec = importlib.util.spec_from_file_location("oot3d_ptbr_core_v4", core_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível criar o spec para: {core_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("900x650")
        self.minsize(760, 520)

        self.gui_dir = app_dir()
        self.root_dir: Path | None = None
        self.core_path: Path | None = None
        self.payload_dir: Path | None = None
        self.core = None
        self.selected_root = None

        self.columnconfigure(0, weight=1)
        # Somente a linha do log expande verticalmente.
        self.rowconfigure(3, weight=1)

        self._build_ui()
        self.after(100, self.initial_detection)

    def _build_ui(self):
        header = ttk.Frame(self, padding=(18, 16, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Tradução PT-BR — Ocarina of Time 3D",
            font=("Segoe UI", 17, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="TriAevum v0.8.0-beta.1 • Fonte HD e acentos PT-BR • Single Screen",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        buttons = ttk.Frame(self, padding=(18, 8))
        buttons.grid(row=1, column=0, sticky="ew")
        for col in range(3):
            buttons.columnconfigure(col, weight=1)

        self.install_btn = ttk.Button(
            buttons, text="Instalar tradução", command=self.install_translation
        )
        self.install_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.restore_btn = ttk.Button(
            buttons, text="Restaurar original", command=self.restore_original
        )
        self.restore_btn.grid(row=0, column=1, sticky="ew", padx=6)

        self.status_btn = ttk.Button(
            buttons, text="Verificar status", command=self.verify_status
        )
        self.status_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        self.hd_install_btn = ttk.Button(buttons, text="Adicionar texturas HD (Windows 0.8)",
                                         command=self.install_hd)
        self.hd_install_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 6), pady=(8, 0))
        self.hd_restore_btn = ttk.Button(buttons, text="Remover suporte HD", command=self.restore_hd)
        self.hd_restore_btn.grid(row=1, column=2, sticky="ew", padx=(6, 0), pady=(8, 0))
        if sys.platform != "win32" or hd_bundle() is None:
            self.hd_install_btn.configure(state="disabled")
        if sys.platform != "win32":
            self.hd_restore_btn.configure(state="disabled")

        status_frame = ttk.LabelFrame(self, text="Status", padding=(12, 8))
        status_frame.grid(row=2, column=0, sticky="ew", padx=18, pady=(2, 8))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Aguardando detecção...")
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            wraplength=820,
        ).grid(row=0, column=0, sticky="w")

        log_frame = ttk.LabelFrame(self, text="Log", padding=(10, 8))
        log_frame.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 8))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log = ScrolledText(
            log_frame,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
        )
        self.log.grid(row=0, column=0, sticky="nsew")

        ttk.Button(status_frame, text="Selecionar pasta do TriAevum", command=self.select_root).grid(row=1, column=0, sticky="w", pady=(6, 0))

        footer = ttk.Frame(self, padding=(18, 6, 18, 14))
        footer.grid(row=4, column=0, sticky="ew")
        footer.columnconfigure(1, weight=1)

        ttk.Button(footer, text="Leia-me", command=self.open_credits).grid(
            row=0, column=0, padx=(0, 6)
        )
        ttk.Label(footer, text="v1.2 • TriAevum v0.8.0-beta.1").grid(
            row=0, column=1
        )
        ttk.Button(footer, text="Sair", command=self.destroy).grid(
            row=0, column=2, padx=(6, 0)
        )

    def write_log(self, text=""):
        self.log.configure(state="normal")
        self.log.insert("end", str(text) + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update_idletasks()

    def initial_detection(self):
        self.write_log("=== TRADUÇÃO PT-BR PARA OCARINA OF TIME 3D ===")
        self.refresh_paths(log=True)
        if self.root_dir is not None and app_dir() != self.root_dir:
            self.write_log("")
            self.write_log("Aviso: este instalador foi projetado para ficar diretamente na pasta raiz do TriAevum.")

        if self.root_dir and self.core_path and self.payload_dir:
            self.status_var.set(
                "Arquivos necessários detectados. Clique em “Verificar status”."
            )
        else:
            self.status_var.set(
                "Detecção incompleta. Consulte o log antes de verificar o status."
            )

    def select_root(self):
        if getattr(self, "operation_busy", False):
            return
        selected = filedialog.askdirectory(title="Selecione a pasta que contém TriAevum.launch.json")
        if not selected:
            return
        root = Path(selected).resolve()
        if not is_triaevum_root(root):
            messagebox.showerror("Pasta do TriAevum", "Selecione o perfil preparado pelo Forge, contendo TriAevum.launch.json e data.")
            return
        self.selected_root = root
        self.core = None
        self.refresh_paths(log=True)
        self.status_var.set("Pasta selecionada. Clique em Verificar status.")

    def refresh_paths(self, log=False):
        self.root_dir = self.selected_root or detect_triaevum_root(self.gui_dir)
        self.core_path = locate_core(self.gui_dir, self.root_dir)
        self.payload_dir = locate_payload(self.gui_dir, self.root_dir)

        if log:
            if self.root_dir:
                self.write_log("[OK] Instalação do TriAevum detectada.")
            else:
                self.write_log("[ERRO] Pasta raiz do TriAevum não encontrada.")

            if self.core_path:
                self.write_log("[OK] Núcleo do instalador encontrado.")
            else:
                self.write_log("[ERRO] Núcleo do instalador não encontrado.")

            if self.payload_dir:
                self.write_log("[OK] Arquivos da tradução encontrados.")
            else:
                self.write_log("[ERRO] Arquivos da tradução não encontrados.")

            self.write_log("")

    def verify_status(self):
        self.write_log("=" * 72)
        self.write_log("VERIFICANDO INSTALAÇÃO")
        self.write_log("=" * 72)

        self.refresh_paths(log=True)

        if self.root_dir is None:
            self.status_var.set("Raiz do TriAevum não encontrada.")
            self.write_log(
                "ERRO: não encontrei uma pasta contendo data\\ e "
                "TriAevum.launch.json ou TriAevum*.exe."
            )
            return

        if self.core_path is None:
            self.status_var.set("Núcleo V4 não encontrado.")
            self.write_log(f"ERRO: não encontrei {CORE_FILENAME}.")
            return

        if self.payload_dir is None:
            self.write_log(
                "AVISO: TraducaoCompleta/citra/romfs não foi encontrada."
            )
            self.write_log(
                "O status ainda será tentado, pois este teste é de diagnóstico."
            )
            self.write_log("")

        try:
            self.write_log("Preparando verificação...")
            self.core = import_core(self.core_path)
            self.write_log("[OK] Núcleo carregado.")
            self.write_log("")

            # Ajusta somente o contexto de caminhos esperado pelo núcleo V4.
            self.core.BASE = self.root_dir
            self.core.LAUNCH = self.root_dir / "TriAevum.launch.json"
            self.core.TRAD_ROOT = self.payload_dir
            self.core.MARKER = self.root_dir / "traducao_ptbr_v4_instalada.json"

            self.write_log("[OK] Instalador preparado.")
            self.write_log("")

            status_func = getattr(self.core, "diagnostic", None)
            if not callable(status_func):
                raise AttributeError(
                    "O núcleo importado não possui uma função status() chamável."
                )


            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()

            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(
                stderr_buffer
            ):
                result = status_func()

            stdout_text = stdout_buffer.getvalue()
            stderr_text = stderr_buffer.getvalue()

            if stdout_text:
                self.write_log(stdout_text.rstrip("\n"))
            else:
                self.write_log("(core.status() não escreveu em stdout)")

            if stderr_text:
                self.write_log("")
                self.write_log("=== STDERR DE core.status() ===")
                self.write_log(stderr_text.rstrip("\n"))

            if result is not None:
                self.write_log("")
                self.write_log(f"Retorno de core.status(): {result!r}")

            self.write_log("")
            self.write_log("VERIFICAR STATUS — concluído sem exceção.")
            self.status_var.set("Verificação concluída. Consulte o log para detalhes.")

        except Exception:
            self.status_var.set("Erro durante o diagnóstico. Consulte o log.")
            self.write_log("")
            self.write_log("=== EXCEÇÃO ===")
            self.write_log(traceback.format_exc().rstrip())
            self.write_log("")
            self.write_log(
                "Nenhuma chamada a install() ou restore() foi feita por esta GUI."
            )

    def configure_core_paths(self):
        """Configura no núcleo V4 os caminhos detectados pela GUI."""
        if self.core is None:
            if self.core_path is None:
                raise RuntimeError("Núcleo V4 não encontrado.")
            self.core = import_core(self.core_path)

        self.core.BASE = self.root_dir
        self.core.LAUNCH = self.root_dir / "TriAevum.launch.json"
        self.core.TRAD_ROOT = self.payload_dir
        self.core.MARKER = self.root_dir / "traducao_ptbr_v4_instalada.json"

    def set_operation_buttons(self, busy):
        self.operation_busy = busy
        state = "disabled" if busy else "normal"
        self.install_btn.configure(state=state)
        self.restore_btn.configure(state=state)
        self.status_btn.configure(state=state)
        self.hd_install_btn.configure(state="normal" if not busy and sys.platform == "win32" and hd_bundle() else "disabled")
        self.hd_restore_btn.configure(state="normal" if not busy and sys.platform == "win32" else "disabled")

    def install_hd(self):
        self.refresh_paths(log=False)
        if self.root_dir is None or hd_bundle() is None:
            messagebox.showerror("Texturas HD", "Selecione a instalação e use um pacote com o runtime HD incluído.")
            return
        selected = filedialog.askdirectory(title="Selecione o pacote 4K com os menus traduzidos e TopScreen")
        if selected:
            self.set_operation_buttons(True)
            self.status_var.set("Validando e instalando suporte HD...")
            threading.Thread(target=self._hd_worker, args=(Path(selected),), daemon=True).start()

    def restore_hd(self):
        self.refresh_paths(log=False)
        if self.root_dir is None:
            messagebox.showerror("Texturas HD", "Selecione a instalação do TriAevum.")
            return
        self.set_operation_buttons(True)
        self.status_var.set("Removendo suporte HD...")
        threading.Thread(target=self._hd_worker, args=(None,), daemon=True).start()

    def _hd_worker(self, selected):
        try:
            module = hd_module()
            if selected is None:
                changed = module.restore(self.root_dir)
                message = "Suporte HD removido; tradução e preferências HD preservadas." if changed else "Não há instalação HD registrada."
            else:
                result = module.install(self.root_dir, selected, hd_bundle())
                message = "Suporte HD instalado. Abra TriAevum-PTBR-HD.exe.\n" + str(result)
            self.after(0, lambda text=message: self._hd_finished(True, text))
        except Exception:
            error = traceback.format_exc()
            self.after(0, lambda text=error: self._hd_finished(False, text))

    def _hd_finished(self, success, text):
        self.write_log(text)
        self.status_var.set("Suporte HD atualizado." if success else "Falha no componente HD. Consulte o log.")
        self.set_operation_buttons(False)
        (messagebox.showinfo if success else messagebox.showerror)("Texturas HD", text)

    def install_translation(self):
        self.refresh_paths(log=False)

        if self.root_dir is None or self.core_path is None or self.payload_dir is None:
            messagebox.showerror(
                "Instalação",
                "Não foi possível localizar a raiz do TriAevum, o núcleo V4 "
                "ou o payload da tradução completa."
            )
            return

        if not messagebox.askyesno(
            "Instalar tradução PT-BR",
            "O instalador validará a base original, criará backups "
            "e aplicará a tradução PT-BR completa + compatibilidade TopScreen.\n\n"
            "A instalação pode levar alguns minutos. Aguarde até a conclusão.\n\n"
            "Deseja continuar?"
        ):
            self.write_log("Instalação cancelada pelo usuário.")
            return

        self.set_operation_buttons(True)
        self.status_var.set("Instalando tradução PT-BR V4...")

        self.write_log("=" * 72)
        self.write_log("INSTALANDO TRADUÇÃO PT-BR")
        self.write_log("=" * 72)
        self.write_log("Preparando arquivos da tradução...")
        self.write_log("")

        threading.Thread(target=self._install_worker, daemon=True).start()

    def _install_worker(self):
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        try:
            self.configure_core_paths()

            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                result = self.core.install()

            stdout_text = stdout_buffer.getvalue()
            stderr_text = stderr_buffer.getvalue()

            self.after(
                0,
                lambda: self._install_finished(
                    True, stdout_text, stderr_text, result, None
                )
            )

        except Exception:
            stdout_text = stdout_buffer.getvalue()
            stderr_text = stderr_buffer.getvalue()
            error_text = traceback.format_exc()

            self.after(
                0,
                lambda: self._install_finished(
                    False, stdout_text, stderr_text, None, error_text
                )
            )

    def _install_finished(self, success, stdout_text, stderr_text, result, error_text):
        if stdout_text:
            self.write_log(stdout_text.rstrip("\n"))

        if stderr_text:
            self.write_log("")
            self.write_log("=== STDERR ===")
            self.write_log(stderr_text.rstrip("\n"))

        if result is not None:
            self.write_log("")
            self.write_log(f"Retorno de core.install(): {result!r}")

        if success:
            self.write_log("")
            self.write_log("INSTALAR TRADUÇÃO — concluído sem exceção.")
            self.status_var.set("Instalação concluída. Verificando status...")
            self.set_operation_buttons(False)

            messagebox.showinfo(
                "Instalação",
                "A instalação terminou sem exceção.\n\n"
                "O status será verificado agora."
            )
            self.verify_status()

        else:
            self.write_log("")
            self.write_log("=== EXCEÇÃO DURANTE INSTALL ===")
            self.write_log(error_text.rstrip())
            self.status_var.set("Falha na instalação. Consulte o log.")
            self.set_operation_buttons(False)

            messagebox.showerror(
                "Instalação",
                "A instalação não foi concluída.\n\n"
                "Consulte o log para detalhes."
            )

    def restore_original(self):
        self.refresh_paths(log=False)

        if self.root_dir is None or self.core_path is None:
            messagebox.showerror(
                "Restauração",
                "Não foi possível localizar a raiz do TriAevum ou o núcleo V4."
            )
            return

        if not messagebox.askyesno(
            "Restaurar original",
            "Esta operação restaurará o RomFS, o manifesto e o TopScreen "
            "usando os backups V4.\n\n"
            "A tradução PT-BR V4 será removida.\n\n"
            "Deseja continuar?"
        ):
            self.write_log("Restauração cancelada pelo usuário.")
            return

        self.set_operation_buttons(True)
        self.status_var.set("Restaurando arquivos originais...")

        self.write_log("=" * 72)
        self.write_log("RESTAURANDO ARQUIVOS ORIGINAIS")
        self.write_log("=" * 72)
        self.write_log("Preparando restauração...")
        self.write_log("")

        threading.Thread(target=self._restore_worker, daemon=True).start()

    def _restore_worker(self):
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        try:
            self.configure_core_paths()
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                if (self.root_dir / "data/mods/ptbr-hd/installation.json").is_file():
                    hd_module().restore(self.root_dir)
                    print("[OK] Componente HD removido antes da restauração da tradução.")
                result = self.core.restore()

            stdout_text = stdout_buffer.getvalue()
            stderr_text = stderr_buffer.getvalue()
            self.after(
                0,
                lambda: self._restore_finished(
                    True, stdout_text, stderr_text, result, None
                )
            )
        except Exception:
            stdout_text = stdout_buffer.getvalue()
            stderr_text = stderr_buffer.getvalue()
            error_text = traceback.format_exc()
            self.after(
                0,
                lambda: self._restore_finished(
                    False, stdout_text, stderr_text, None, error_text
                )
            )

    def _restore_finished(self, success, stdout_text, stderr_text, result, error_text):
        if stdout_text:
            self.write_log(stdout_text.rstrip("\n"))

        if stderr_text:
            self.write_log("")
            self.write_log("=== STDERR ===")
            self.write_log(stderr_text.rstrip("\n"))

        if result is not None:
            self.write_log("")
            self.write_log(f"Retorno de core.restore(): {result!r}")

        if success:
            self.write_log("")
            self.write_log("RESTAURAR ORIGINAL — concluído sem exceção.")
            self.status_var.set("Restauração concluída. Verificando status...")
            self.set_operation_buttons(False)
            messagebox.showinfo(
                "Restauração",
                "A restauração terminou sem exceção.\n\n"
                "O status será verificado agora."
            )
            self.verify_status()
        else:
            self.write_log("")
            self.write_log("=== EXCEÇÃO DURANTE RESTORE ===")
            self.write_log(error_text.rstrip())
            self.status_var.set("Falha na restauração. Consulte o log.")
            self.set_operation_buttons(False)
            messagebox.showerror(
                "Restauração",
                "A restauração não foi concluída.\n\nConsulte o log para detalhes."
            )

    def open_credits(self):
        """Abre um LEIA-ME resumido em uma janela interna."""
        readme_text = 'LEIA-ME — Tradução PT-BR para Ocarina of Time 3D\n\nSOBRE\nAdaptação da tradução brasileira de The Legend of Zelda: Ocarina of Time 3D para o TriAevum.\nCOMPATIBILIDADE VALIDADA\nTriAevum v0.8.0-beta.1 Windows x64: tradução e fonte HD testadas pelo usuário. Correção do til preparada para conferência final. Linux x86_64 (AppImage/Flatpak): validação no jogo pendente. Base v0.6.0-alpha.2c preservada.\n\nEste projeto não distribui o jogo ou ROM.\n\nCOMO INSTALAR\n1. Windows: coloque o instalador ao lado de TriAevum.launch.json. Linux: selecione o perfil de dados preparado pelo Forge.\n2. Feche o jogo e o TriAevum.\n3. Clique em “Verificar status”.\n4. Clique em “Instalar tradução” e aguarde a conclusão.\n5. Abra o jogo e confira a tradução.\n\nCOMO RESTAURAR\n1. Abra o instalador.\n2. Clique em “Restaurar original”.\n3. Confirme e aguarde a restauração dos backups.\n\nIMPORTANTE\n• Não apague os backups criados pelo instalador enquanto a tradução estiver instalada.\n• Se a validação falhar, não force a instalação.\n• A versão 0.8 mantém a fonte HD original e corrige os códigos de ã/õ/Ã/Õ.\n• No Linux, selecione a pasta com TriAevum.launch.json; não selecione o arquivo AppImage.\n• Recomenda-se testar a tradução antes de instalar outros mods.\n\nCRÉDITOS — TRADUÇÃO PT-BR ORIGINAL\nProjeto Zelda Brasil – Heroes of Time\nCatatau Game Dev e Traduções\nElite dos Quatro Traduções\nJumpManClub Brasil Traduções\nTRADU-ROMS\n\nPORT PARA TRIAEVUM\nXandasL — port, adaptação e empacotamento do instalador.\n\nAUTORIZAÇÃO\nO port e a distribuição da tradução completa são realizados com autorização do responsável pela tradução, mantendo os devidos créditos dentro e fora do jogo.\n\nAVISO\nProjeto feito por fãs, sem afiliação oficial com a Nintendo.\nThe Legend of Zelda e demais propriedades relacionadas pertencem aos seus respectivos detentores.\n'

        window = tk.Toplevel(self)
        window.title("LEIA-ME - Tradução PT-BR Ocarina of Time 3D")
        window.geometry("700x560")
        window.minsize(560, 420)
        window.transient(self)

        frame = ttk.Frame(window, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="LEIA-ME — Tradução PT-BR",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        viewer = tk.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 10),
            padx=12,
            pady=10,
            yscrollcommand=scrollbar.set,
        )
        viewer.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=viewer.yview)

        viewer.insert("1.0", readme_text)
        viewer.configure(state="disabled")

        ttk.Button(frame, text="Fechar", command=window.destroy).pack(
            anchor="e", pady=(10, 0)
        )

        window.focus_set()


def bundle_self_test(report):
    import json
    import hashlib
    core_path = bundled_dir() / CORE_FILENAME
    core = import_core(core_path)
    core.TRAD_ROOT = bundled_dir() / PAYLOAD_RELATIVE
    items = core.collect_v4_items()
    expected = json.loads((bundled_dir() / "payload-manifest.json").read_text(encoding="utf-8"))
    paths = {str(item["source_rel"]): item["source"] for item in core.collect_translation()}
    if set(paths) != set(expected):
        raise RuntimeError("Arquivos do payload embutido não conferem.")
    for name, path in paths.items():
        if core.sha256_file(path) != expected[name]:
            raise RuntimeError(f"Payload embutido diferente: {name}")
    qm = (core.TRAD_ROOT / "message/us/us.qm").read_bytes()
    core.EXPECTED_CLEAN_ROMFS_SHA256 = core.BETA_ROMFS_SHA256
    converted = core.convert_qm_us_to_eu(qm)
    if len(converted) != len(qm):
        raise RuntimeError("Conversão QM alterou tamanho.")
    window = App()
    window.withdraw()
    window.update_idletasks()
    hd_enabled = sys.platform == 'win32' and hd_bundle() is not None
    if str(window.hd_install_btn.cget('state')) != ('normal' if hd_enabled else 'disabled'):
        raise RuntimeError('O estado da opção HD na interface não corresponde ao bundle.')
    window.destroy()
    result = {"ok": True, "tk_verified": True, "hd_ui_verified": True, "version": APP_VERSION, "platform": sys.platform,
              "translation_files": len(paths), "operations": len(items),
              "qm_sha256": hashlib.sha256(converted).hexdigest()}
    module = hd_module()
    result["hd_recipe_aliases"] = len(module.recipe()["aliases"])
    result["hd_runtime_included"] = hd_bundle() is not None
    if hd_bundle():
        module.validate_bundle(hd_bundle())
        result["hd_bundle_verified"] = True
    Path(report).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-report", type=Path)
    parser.add_argument("--root", type=Path)
    options = parser.parse_args()
    if options.self_test_report:
        bundle_self_test(options.self_test_report)
    else:
        app = App()
        if options.root:
            root = options.root.resolve()
            if not is_triaevum_root(root):
                raise RuntimeError("Perfil TriAevum inválido.")
            app.selected_root = root
        app.mainloop()
