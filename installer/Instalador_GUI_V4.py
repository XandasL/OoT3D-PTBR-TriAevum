# -*- coding: utf-8 -*-
"""Interface gráfica do instalador PT-BR OoT3D / TriAevum V4."""

from pathlib import Path
import contextlib
import importlib.util
import io
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

TITLE = "Tradução PT-BR - Ocarina of Time 3D"

APP_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
CORE_PATH = RESOURCE_DIR / "Instalador_Traducao_PTBR_OoT3D_V4.py"
CREDITS_PATH = RESOURCE_DIR / "CREDITOS.txt"


def load_core():
    if not CORE_PATH.exists():
        raise RuntimeError(f"Núcleo V4 não encontrado:\n{CORE_PATH}")

    spec = importlib.util.spec_from_file_location("oot3d_ptbr_v4_core", CORE_PATH)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)

    # O núcleo precisa procurar o TriAevum ao lado do EXE/script real.
    core.BASE = APP_DIR

    embedded = RESOURCE_DIR / "TraducaoCompleta" / "citra" / "romfs"
    external = APP_DIR / "TraducaoCompleta" / "citra" / "romfs"
    if embedded.exists():
        core.TRAD_ROOT = embedded
    elif external.exists():
        core.TRAD_ROOT = external
    else:
        raise RuntimeError("Payload TraducaoCompleta/citra/romfs não encontrado.")

    # Em --onefile, não deixe o marcador dentro do diretório temporário _MEIPASS.
    if hasattr(core, "MARKER"):
        core.MARKER = APP_DIR / "traducao_ptbr_v4_instalada.json"

    return core


class QueueWriter(io.TextIOBase):
    def __init__(self, q):
        self.q = q

    def write(self, text):
        if text:
            self.q.put(("log", text))
        return len(text)

    def flush(self):
        pass


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITLE)
        self.geometry("760x600")
        self.minsize(680, 520)
        self.q = queue.Queue()
        self.busy = False
        self.core = None

        header = tk.Frame(self, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(
            header,
            text="The Legend of Zelda: Ocarina of Time 3D",
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Tradução PT-BR • Instalador V4",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            header,
            text="TriAevum • compatibilidade TopScreen / Single Screen",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(7, 0))

        buttons = tk.Frame(self, padx=24)
        buttons.pack(fill="x")
        self.install_button = tk.Button(
            buttons,
            text="Instalar tradução",
            height=2,
            font=("Segoe UI", 10, "bold"),
            command=lambda: self.start("install"),
        )
        self.restore_button = tk.Button(
            buttons,
            text="Restaurar original",
            height=2,
            command=lambda: self.start("restore"),
        )
        self.status_button = tk.Button(
            buttons,
            text="Verificar status",
            height=2,
            command=lambda: self.start("status"),
        )
        self.install_button.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.restore_button.pack(side="left", fill="x", expand=True, padx=6)
        self.status_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.state_label = tk.Label(self, text="Pronto.", anchor="w", padx=24, pady=12)
        self.state_label.pack(fill="x")

        self.log = scrolledtext.ScrolledText(
            self, font=("Consolas", 9), wrap="word", state="disabled"
        )
        self.log.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        footer = tk.Frame(self, padx=24, pady=(0, 18))
        footer.pack(fill="x")
        tk.Button(footer, text="Créditos", command=self.show_credits).pack(side="left")
        tk.Button(footer, text="Abrir pasta", command=self.open_folder).pack(
            side="left", padx=8
        )
        tk.Button(footer, text="Sair", command=self.destroy).pack(side="right")

        self.after(80, self.poll)

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_busy(self, value):
        self.busy = value
        state = "disabled" if value else "normal"
        for button in (
            self.install_button,
            self.restore_button,
            self.status_button,
        ):
            button.configure(state=state)

    def start(self, action):
        if self.busy:
            return

        if action == "install":
            ok = messagebox.askyesno(
                TITLE,
                "Instalar a Tradução PT-BR V4?\n\n"
                "A instalação será validada e backups serão criados antes das alterações.",
            )
            if not ok:
                return
        elif action == "restore":
            ok = messagebox.askyesno(
                TITLE,
                "Restaurar os arquivos originais salvos pela V4?",
            )
            if not ok:
                return

        self.set_busy(True)
        self.state_label.configure(text="Processando…")
        self.append_log("\n" + "=" * 65 + "\n")
        threading.Thread(target=self.worker, args=(action,), daemon=True).start()

    def worker(self, action):
        writer = QueueWriter(self.q)
        try:
            if self.core is None:
                self.core = load_core()

            function = {
                "install": self.core.install,
                "restore": self.core.restore,
                "status": self.core.status,
            }[action]

            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                function()

            self.q.put(("done", action))
        except Exception as exc:
            self.q.put(("error", str(exc)))

    def poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "log":
                    self.append_log(data)
                elif kind == "done":
                    self.set_busy(False)
                    self.state_label.configure(text="Concluído.")
                    if data == "install":
                        messagebox.showinfo(
                            TITLE,
                            "Tradução PT-BR V4 instalada com sucesso.",
                        )
                    elif data == "restore":
                        messagebox.showinfo(TITLE, "Arquivos originais restaurados.")
                elif kind == "error":
                    self.set_busy(False)
                    self.state_label.configure(text="Operação interrompida.")
                    self.append_log("\nERRO: " + data + "\n")
                    messagebox.showerror(TITLE, data)
        except queue.Empty:
            pass

        self.after(80, self.poll)

    def show_credits(self):
        if CREDITS_PATH.exists():
            text = CREDITS_PATH.read_text(encoding="utf-8-sig")
        else:
            text = "CREDITOS.txt não encontrado."

        window = tk.Toplevel(self)
        window.title("Créditos")
        window.geometry("640x460")
        box = scrolledtext.ScrolledText(window, wrap="word", font=("Segoe UI", 10))
        box.pack(fill="both", expand=True, padx=15, pady=15)
        box.insert("1.0", text)
        box.configure(state="disabled")

    def open_folder(self):
        try:
            os.startfile(APP_DIR)
        except Exception as exc:
            messagebox.showerror(TITLE, str(exc))


if __name__ == "__main__":
    InstallerApp().mainloop()
