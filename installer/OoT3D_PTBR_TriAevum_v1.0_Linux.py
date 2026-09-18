# -*- coding: utf-8 -*-
"""
Tradução PT-BR de Ocarina of Time 3D para TriAevum — protótipo Linux/Flatpak.

Esta camada NÃO reimplementa a lógica de patch do núcleo V4.
Ela detecta a área persistente do Flatpak, localiza com cautela o perfil
TriAevum preparado e então configura o núcleo V4 já validado.

IMPORTANTE:
- Este protótipo destina-se especificamente ao TriAevum v0.6.0-alpha.2c,
  cuja distribuição Linux oficial utiliza Flatpak.
- Releases posteriores podem usar outro formato de empacotamento e NÃO devem
  ser tratadas automaticamente como compatíveis com esta versão do instalador.
- Esta versão ainda precisa de validação em uma instalação Linux real.
- Se a detecção for ambígua, a instalação é bloqueada.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

APP_TITLE = "Tradução PT-BR - Ocarina of Time 3D / TriAevum v0.6.0-alpha.2c (Linux Flatpak)"
APP_ID = "io.github.coccofresco.TriAevum"
CORE_FILENAME = "Instalador_Traducao_PTBR_OoT3D_V4.py"
PAYLOAD_RELATIVE = Path("TraducaoCompleta") / "citra" / "romfs"
MARKER_FILENAME = "traducao_ptbr_v4_instalada.json"


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def bundled_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent


def flatpak_root() -> Path:
    """Área persistente padrão do aplicativo Flatpak no host."""
    override = os.environ.get("TRIAEVUM_FLATPAK_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".var" / "app" / APP_ID


def locate_core() -> Path | None:
    for p in (bundled_dir() / CORE_FILENAME, app_dir() / CORE_FILENAME):
        if p.is_file():
            return p
    return None


def locate_payload() -> Path | None:
    for p in (bundled_dir() / PAYLOAD_RELATIVE, app_dir() / PAYLOAD_RELATIVE):
        if p.is_dir():
            return p
    return None


def import_core(path: Path):
    spec = importlib.util.spec_from_file_location("oot3d_ptbr_core_v4_linux", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o núcleo: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def unique_existing(paths):
    seen = set()
    result = []
    for p in paths:
        try:
            p = p.resolve()
        except OSError:
            continue
        key = str(p)
        if key not in seen and p.exists():
            seen.add(key)
            result.append(p)
    return result


def find_launch_profiles(root: Path):
    """Procura perfis sem seguir symlinks externos nem sair da área Flatpak."""
    found = []
    if not root.is_dir():
        return found
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {"cache", ".cache"}]
        if "TriAevum.launch.json" in files:
            found.append(Path(base) / "TriAevum.launch.json")
    return unique_existing(found)


def find_process_manifests(root: Path):
    found = []
    if not root.is_dir():
        return found
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {"cache", ".cache"}]
        if "process-manifest.json" in files:
            found.append(Path(base) / "process-manifest.json")
    return unique_existing(found)


def candidate_profile_roots(root: Path):
    launches = find_launch_profiles(root)
    roots = [p.parent for p in launches]
    if not roots:
        for manifest in find_process_manifests(root):
            for parent in (manifest.parent, *manifest.parents):
                try:
                    parent.relative_to(root)
                except ValueError:
                    break
                if (parent / "data").is_dir():
                    roots.append(parent)
                    break
    return unique_existing(roots)


def locate_topscreen(profile_root: Path):
    root = profile_root / "data" / "mods" / "topscreen"
    if not root.is_dir():
        return []
    return list(root.rglob("atlas_overrides.o3tu"))


def inspect_candidate(profile_root: Path):
    return {
        "root": profile_root,
        "launch": profile_root / "TriAevum.launch.json",
        "topscreen": locate_topscreen(profile_root),
    }


def choose_profile(flat_root: Path):
    candidates = candidate_profile_roots(flat_root)
    valid = []
    for root in candidates:
        info = inspect_candidate(root)
        if info["launch"].is_file() and len(info["topscreen"]) == 1:
            valid.append(info)

    if len(valid) == 1:
        return valid[0]
    if not candidates:
        raise RuntimeError(
            "Não encontrei uma instalação preparada do TriAevum dentro da área "
            f"Flatpak:\n{flat_root}\n\n"
            "Prepare Ocarina of Time 3D pelo TriAevum/Forge e execute o jogo "
            "ao menos uma vez."
        )
    if not valid:
        raise RuntimeError(
            "Encontrei dados do TriAevum, mas nenhum perfil pôde ser validado "
            "com TriAevum.launch.json + exatamente um atlas_overrides.o3tu.\n\n"
            "Nenhum arquivo será modificado."
        )
    raise RuntimeError(
        "Foram encontrados vários perfis compatíveis do TriAevum. "
        "A instalação foi bloqueada para evitar alterar o perfil errado.\n\n"
        + "\n".join(str(x["root"]) for x in valid)
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x650")
        self.minsize(760, 520)
        self.core_path = None
        self.payload_dir = None
        self.profile = None
        self.core = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self.build_ui()
        self.after(100, self.initial_detection)

    def build_ui(self):
        header = ttk.Frame(self, padding=(18, 16, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Tradução PT-BR — Ocarina of Time 3D",
                  font=("Sans", 17, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="TriAevum v0.6.0-alpha.2c • Linux / Flatpak • protótipo para validação").grid(
            row=1, column=0, sticky="w", pady=(4, 0))

        buttons = ttk.Frame(self, padding=(18, 8))
        buttons.grid(row=1, column=0, sticky="ew")
        for col in range(3):
            buttons.columnconfigure(col, weight=1)
        self.install_btn = ttk.Button(buttons, text="Instalar tradução", command=self.install_translation)
        self.install_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.restore_btn = ttk.Button(buttons, text="Restaurar original", command=self.restore_original)
        self.restore_btn.grid(row=0, column=1, sticky="ew", padx=6)
        self.status_btn = ttk.Button(buttons, text="Verificar status", command=self.verify_status)
        self.status_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        sf = ttk.LabelFrame(self, text="Status", padding=(12, 8))
        sf.grid(row=2, column=0, sticky="ew", padx=18, pady=(2, 8))
        sf.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Aguardando detecção...")
        ttk.Label(sf, textvariable=self.status_var, wraplength=820).grid(row=0, column=0, sticky="w")

        lf = ttk.LabelFrame(self, text="Log", padding=(10, 8))
        lf.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 8))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)
        self.log = ScrolledText(lf, wrap="word", font=("Monospace", 10), state="disabled")
        self.log.grid(row=0, column=0, sticky="nsew")

        footer = ttk.Frame(self, padding=(18, 6, 18, 14))
        footer.grid(row=4, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, text="Linux v1.0 • alvo: TriAevum v0.6.0-alpha.2c Flatpak • pré-validação").grid(row=0, column=0)
        ttk.Button(footer, text="Sair", command=self.destroy).grid(row=0, column=1)

    def write_log(self, text=""):
        self.log.configure(state="normal")
        self.log.insert("end", str(text) + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update_idletasks()

    def refresh_paths(self, verbose=False):
        self.core_path = locate_core()
        self.payload_dir = locate_payload()
        self.profile = None
        fr = flatpak_root()
        if verbose:
            self.write_log(f"Área Flatpak esperada: {fr}")
            self.write_log("[OK] Área Flatpak encontrada." if fr.is_dir() else "[ERRO] Área Flatpak ainda não existe.")
            self.write_log("[OK] Núcleo V4 encontrado." if self.core_path else "[ERRO] Núcleo V4 não encontrado.")
            self.write_log("[OK] Payload PT-BR encontrado." if self.payload_dir else "[ERRO] Payload PT-BR não encontrado.")
        if fr.is_dir():
            try:
                self.profile = choose_profile(fr)
                if verbose:
                    self.write_log(f"[OK] Perfil TriAevum: {self.profile['root']}")
                    self.write_log(f"[OK] Launch profile: {self.profile['launch']}")
                    self.write_log(f"[OK] TopScreen: {self.profile['topscreen'][0]}")
            except Exception as e:
                if verbose:
                    self.write_log(f"[AVISO] {e}")
        if verbose:
            self.write_log("")

    def initial_detection(self):
        self.write_log("=== TRADUÇÃO PT-BR / TRIAEVUM LINUX ===")
        self.write_log("Alvo desta edição: TriAevum v0.6.0-alpha.2c para Linux/Flatpak.")
        self.write_log("Não presuma compatibilidade com releases posteriores ou outros formatos de pacote.")
        self.write_log("Esta edição ainda requer validação em Linux real.")
        self.write_log("")
        self.refresh_paths(True)
        if self.profile and self.core_path and self.payload_dir:
            self.status_var.set("TriAevum detectado. Clique em “Verificar status”.")
        else:
            self.status_var.set("Detecção incompleta. Consulte o log.")

    def configure_core(self):
        self.refresh_paths(False)
        if not self.profile:
            raise RuntimeError("Perfil TriAevum Linux não validado.")
        if not self.core_path:
            raise RuntimeError("Núcleo V4 não encontrado.")
        if not self.payload_dir:
            raise RuntimeError("Payload PT-BR não encontrado.")
        if self.core is None:
            self.core = import_core(self.core_path)
        root = self.profile["root"]
        self.core.BASE = root
        self.core.LAUNCH = self.profile["launch"]
        self.core.TRAD_ROOT = self.payload_dir
        self.core.MARKER = root / MARKER_FILENAME
        expected = self.profile["topscreen"][0].resolve()
        located = self.core.locate_o3tu().resolve()
        if located != expected:
            raise RuntimeError(
                "A localização TopScreen do núcleo divergiu da detecção Linux. "
                "Nenhum arquivo será alterado."
            )

    def run_core(self, func_name):
        self.configure_core()
        func = getattr(self.core, func_name, None)
        if not callable(func):
            raise RuntimeError(f"Função {func_name}() não encontrada no núcleo V4.")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = func()
        return stdout.getvalue(), stderr.getvalue(), result

    def verify_status(self):
        self.write_log("=" * 72)
        self.write_log("VERIFICANDO STATUS")
        self.write_log("=" * 72)
        try:
            out, err, result = self.run_core("status")
            if out:
                self.write_log(out.rstrip())
            if err:
                self.write_log("=== STDERR ===")
                self.write_log(err.rstrip())
            if result is not None:
                self.write_log(f"Retorno: {result!r}")
            self.status_var.set("Verificação concluída. Consulte o log.")
        except Exception:
            self.write_log(traceback.format_exc().rstrip())
            self.status_var.set("Não foi possível validar a instalação.")

    def set_busy(self, busy):
        state = "disabled" if busy else "normal"
        for b in (self.install_btn, self.restore_btn, self.status_btn):
            b.configure(state=state)

    def install_translation(self):
        self.refresh_paths(False)
        if not (self.profile and self.core_path and self.payload_dir):
            messagebox.showerror("Instalação",
                "A instalação Linux ainda não pôde ser validada. Use “Verificar status” e consulte o log.")
            return
        if not messagebox.askyesno("Instalar tradução PT-BR",
            "Feche o TriAevum antes de continuar.\n\n"
            "O núcleo V4 validará o RomFS e criará backups antes de alterar arquivos.\n\n"
            "Deseja continuar?"):
            return
        self._start_worker("install")

    def restore_original(self):
        self.refresh_paths(False)
        if not (self.profile and self.core_path):
            messagebox.showerror("Restauração", "TriAevum Linux não foi localizado.")
            return
        if not messagebox.askyesno("Restaurar original",
            "Esta operação utilizará os backups V4 para restaurar os arquivos originais.\n\nDeseja continuar?"):
            return
        self._start_worker("restore")

    def _start_worker(self, action):
        self.set_busy(True)
        self.status_var.set("Processando...")
        threading.Thread(target=self._worker, args=(action,), daemon=True).start()

    def _worker(self, action):
        try:
            out, err, result = self.run_core(action)
            self.after(0, lambda: self._finish(True, action, out, err, result, None))
        except Exception:
            tb = traceback.format_exc()
            self.after(0, lambda: self._finish(False, action, "", "", None, tb))

    def _finish(self, ok, action, out, err, result, tb):
        if out:
            self.write_log(out.rstrip())
        if err:
            self.write_log("=== STDERR ===")
            self.write_log(err.rstrip())
        if result is not None:
            self.write_log(f"Retorno: {result!r}")
        self.set_busy(False)
        if ok:
            self.status_var.set("Operação concluída.")
            messagebox.showinfo("Concluído",
                "Operação concluída sem exceção.\n\nFaça uma nova verificação de status antes de abrir o jogo.")
        else:
            self.write_log("=== EXCEÇÃO ===")
            self.write_log(tb.rstrip())
            self.status_var.set("Operação não concluída. Consulte o log.")
            messagebox.showerror("Erro", "A operação não foi concluída. Consulte o log.")


if __name__ == "__main__":
    App().mainloop()
