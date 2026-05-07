import json
import sys
import base64
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


APP_TITLE = "License Generator"
DEFAULT_OUTPUT_NAME = "license.dat"
SETTINGS_FILE = "app_settings.json"
DEFAULT_PRODUCT = "AutoClickMed"


def canonical_json(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def get_app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_private_key(path: str):
    pem = Path(path).read_bytes()
    return serialization.load_pem_private_key(pem, password=None)


def sign_payload(private_key, payload: str) -> bytes:
    return private_key.sign(
        payload.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def build_payload(name: str, hwid: str) -> str:
    payload_data = {
        "name": name.strip(),
        "hwid": hwid.strip(),
        "exp": "lifetime",
        "product": DEFAULT_PRODUCT
    }
    return canonical_json(payload_data)


class LicenseGeneratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("760x460")
        self.root.minsize(760, 460)

        self.bg = "#081423"
        self.panel = "#0d1b2a"
        self.panel2 = "#10243a"
        self.text = "#e6eef8"
        self.muted = "#9bb1c9"
        self.entry_bg = "#0a1727"
        self.accent = "#1f6feb"
        self.accent2 = "#2b7fff"
        self.border = "#17304d"
        self.success = "#19c37d"

        self.settings_path = get_app_base_dir() / SETTINGS_FILE

        self.private_key_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd()))
        self.name_var = tk.StringVar()
        self.hwid_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto para gerar.")

        self.load_settings()
        self.build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        try:
            if not self.settings_path.exists():
                return

            data = json.loads(self.settings_path.read_text(encoding="utf-8"))

            private_key = str(data.get("private_key_path", "")).strip()
            output_dir = str(data.get("output_dir", "")).strip()

            if private_key:
                self.private_key_var.set(private_key)

            if output_dir:
                self.output_dir_var.set(output_dir)
        except Exception:
            pass

    def save_settings(self):
        try:
            data = {
                "private_key_path": self.private_key_var.get().strip(),
                "output_dir": self.output_dir_var.get().strip()
            }
            self.settings_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass

    def on_close(self):
        self.save_settings()
        self.root.destroy()

    def build_ui(self):
        self.root.configure(bg=self.bg)

        outer = tk.Frame(self.root, bg=self.bg)
        outer.pack(fill="both", expand=True, padx=18, pady=16)

        header = tk.Frame(outer, bg=self.bg)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(
            header,
            text="License Generator",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI Semibold", 18)
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"Gerador offline de {DEFAULT_OUTPUT_NAME} | Produto fixo: {DEFAULT_PRODUCT} | Licença vitalícia",
            bg=self.bg,
            fg=self.muted,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        card = tk.Frame(
            outer,
            bg=self.panel,
            highlightthickness=1,
            highlightbackground=self.border,
            bd=0
        )
        card.pack(fill="both", expand=True)

        content = tk.Frame(card, bg=self.panel)
        content.pack(fill="both", expand=True, padx=16, pady=16)

        content.grid_columnconfigure(1, weight=1)

        self.make_field(content, "Private key (.pem)", self.private_key_var, 0, browse="file")
        self.make_field(content, "Pasta de saída", self.output_dir_var, 1, browse="dir")
        self.make_field(content, "Nome do cliente", self.name_var, 2)
        self.make_field(content, "HWID", self.hwid_var, 3)

        info_box = tk.Frame(content, bg=self.panel)
        info_box.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(14, 0))

        tk.Label(
            info_box,
            text=f"Produto: {DEFAULT_PRODUCT}",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI Semibold", 10)
        ).pack(anchor="w")

        tk.Label(
            info_box,
            text="Validade: Vitalícia",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        spacer = tk.Frame(content, bg=self.panel, height=18)
        spacer.grid(row=5, column=0, columnspan=3, sticky="ew")

        bottom = tk.Frame(content, bg=self.panel)
        bottom.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        bottom.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            bottom,
            textvariable=self.status_var,
            bg=self.panel,
            fg=self.success,
            anchor="w",
            justify="left",
            wraplength=500,
            font=("Segoe UI", 9)
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        generate_btn = tk.Button(
            bottom,
            text="Gerar license.dat",
            command=self.generate_license,
            bg=self.accent,
            fg="white",
            activebackground=self.accent2,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=18,
            pady=10
        )
        generate_btn.grid(row=0, column=1, sticky="e")

    def make_field(self, parent, label_text, variable, row, browse=None):
        tk.Label(
            parent,
            text=label_text,
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI Semibold", 10)
        ).grid(row=row, column=0, sticky="w", pady=(0 if row == 0 else 8, 5))

        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg=self.entry_bg,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.border,
            highlightcolor=self.accent,
            font=("Segoe UI", 10)
        )
        entry.grid(row=row, column=1, sticky="ew", ipady=7)

        if browse == "file":
            cmd = self.browse_key
        elif browse == "dir":
            cmd = self.browse_dir
        else:
            cmd = None

        if cmd:
            tk.Button(
                parent,
                text="Procurar",
                command=cmd,
                bg=self.panel2,
                fg=self.text,
                activebackground=self.accent2,
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 9),
                padx=12,
                pady=7
            ).grid(row=row, column=2, sticky="ew", padx=(8, 0))
        else:
            tk.Frame(parent, bg=self.panel, width=88).grid(row=row, column=2, padx=(8, 0))

    def browse_key(self):
        current = self.private_key_var.get().strip()
        initial_dir = ""

        if current:
            current_path = Path(current)
            if current_path.exists():
                initial_dir = str(current_path.parent)

        path = filedialog.askopenfilename(
            title="Selecione a private key",
            initialdir=initial_dir if initial_dir else str(get_app_base_dir()),
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if path:
            self.private_key_var.set(path)
            self.save_settings()

    def browse_dir(self):
        current = self.output_dir_var.get().strip()
        initial_dir = current if current and Path(current).exists() else str(get_app_base_dir())

        path = filedialog.askdirectory(
            title="Selecione a pasta de saída",
            initialdir=initial_dir
        )
        if path:
            self.output_dir_var.set(path)
            self.save_settings()

    def generate_license(self):
        try:
            private_key_path = self.private_key_var.get().strip()
            output_dir = self.output_dir_var.get().strip()
            name = self.name_var.get().strip()
            hwid = self.hwid_var.get().strip()

            if not private_key_path:
                raise ValueError("Selecione a private key (.pem).")
            if not Path(private_key_path).exists():
                raise ValueError("A private key selecionada não existe.")
            if not output_dir:
                raise ValueError("Selecione a pasta de saída.")
            if not Path(output_dir).exists():
                raise ValueError("A pasta de saída não existe.")
            if not name:
                raise ValueError("Informe o nome do cliente.")
            if not hwid:
                raise ValueError("Informe o HWID.")

            payload = build_payload(name=name, hwid=hwid)

            private_key = load_private_key(private_key_path)
            signature = sign_payload(private_key, payload)
            sig_b64 = base64.b64encode(signature).decode("ascii")

            content = payload + "\n" + "SIG:" + sig_b64 + "\n"

            out_path = Path(output_dir) / DEFAULT_OUTPUT_NAME
            out_path.write_text(content, encoding="utf-8")

            self.save_settings()

            self.status_var.set(f"Licença criada com sucesso em: {out_path}")
            messagebox.showinfo("Sucesso", f"Arquivo criado:\n{out_path}")

        except Exception as e:
            self.status_var.set("Erro ao gerar licença.")
            messagebox.showerror("Erro", str(e))


def main():
    root = tk.Tk()
    LicenseGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()