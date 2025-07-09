from __future__ import annotations

"""Graphical user interface for the SpectrumB Bonelab Bodycam Installer."""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

try:
    import customtkinter as ctk
    _USE_CUSTOM = True
except Exception:  # pragma: no cover - optional dependency
    ctk = tk  # type: ignore
    _USE_CUSTOM = False

from utils import install_mod


class InstallerApp:
    """Main application window."""

    def __init__(self, root: tk.Tk | ctk.CTk) -> None:
        self.root = root
        if _USE_CUSTOM:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
        self.root.title("SpectrumB Bonelab Bodycam Installer")
        self.root.geometry("600x420")
        self.folder = tk.StringVar()
        self.backup = tk.BooleanVar()
        self._build_widgets()

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        padding = {"padx": 10, "pady": 10}

        header = ctk.CTkLabel(
            self.root,
            text="SpectrumB Bonelab Bodycam Installer",
            font=("Arial", 20, "bold"),
        )
        header.pack(**padding)

        frame = ctk.CTkFrame(self.root)
        frame.pack(fill="both", expand=True, **padding)

        # --- folder selection
        path_frame = ctk.CTkFrame(frame)
        path_frame.pack(fill="x", **padding)

        label = ctk.CTkLabel(path_frame, text="1. Select Bonelab Game Folder:")
        label.pack(side="left")

        browse = ctk.CTkButton(path_frame, text="Browse", command=self._browse)
        browse.pack(side="right")

        self.path_entry = ctk.CTkEntry(frame, textvariable=self.folder, state="readonly")
        self.path_entry.pack(fill="x", **padding)

        # --- backup checkbox
        self.backup_chk = ctk.CTkCheckBox(
            frame,
            text="2. Backup existing ReShade files",
            variable=self.backup,
        )
        self.backup_chk.pack(anchor="w", **padding)

        # --- install button
        self.install_btn = ctk.CTkButton(
            frame, text="Install", state="disabled", command=self._install
        )
        self.install_btn.pack(**padding)

        # --- progress bar
        self.progress = ctk.CTkProgressBar(frame, width=400)
        self.progress.pack(**padding)
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(frame, text="0%")
        self.progress_label.pack(**padding)

        # --- log output
        log_label = ctk.CTkLabel(frame, text="Output:")
        log_label.pack(anchor="w", **padding)

        self.log_box = scrolledtext.ScrolledText(frame, height=8, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True, **padding)

    # ------------------------------------------------------------------
    def _browse(self) -> None:
        directory = filedialog.askdirectory(title="Select Bonelab Folder")
        if directory:
            self.folder.set(directory)
            self.install_btn.configure(state="normal")
            self._log(f"Selected folder: {directory}")
            self._update_progress(0)

    # ------------------------------------------------------------------
    def _log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    # ------------------------------------------------------------------
    def _update_progress(self, fraction: float) -> None:
        self.progress.set(fraction)
        self.progress_label.configure(text=f"{int(fraction * 100)}%")
        self.root.update_idletasks()

    # ------------------------------------------------------------------
    def _install(self) -> None:
        target = self.folder.get()
        if not target:
            messagebox.showerror("Error", "Please select the Bonelab folder.")
            return
        install_mod(target, self.backup.get(), self._log, self._update_progress)
        self._log("Installation complete!")
        messagebox.showinfo("Success", "Installation complete!")
        self.install_btn.configure(state="disabled")


# ----------------------------------------------------------------------

def run_app() -> None:
    """Launch the installer UI."""
    root = ctk.CTk() if _USE_CUSTOM else tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
