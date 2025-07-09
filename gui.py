
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

try:
    import customtkinter as ctk
    USE_CUSTOM = True
except ImportError:  # pragma: no cover - optional dependency
    ctk = tk  # type: ignore
    USE_CUSTOM = False

from utils import install_mod


class InstallerApp:

        self.root = root
        if USE_CUSTOM:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
        self.root.title("SpectrumB Bonelab Bodycam Installer")
        self.root.geometry("600x420")

        self.folder_path = tk.StringVar()
        self.backup_var = tk.BooleanVar()

        self.build_ui()

    def build_ui(self) -> None:
        padding = {"padx": 10, "pady": 10}

        header = ctk.CTkLabel(self.root, text="SpectrumB Bonelab Bodycam Installer", font=("Arial", 20, "bold"))
        header.pack(**padding)

        frame = ctk.CTkFrame(self.root)
        frame.pack(fill="both", expand=True, **padding)

        # Step 1: select folder
        path_frame = ctk.CTkFrame(frame)
        path_frame.pack(fill="x", **padding)
        path_label = ctk.CTkLabel(path_frame, text="1. Select Bonelab Game Folder:")
        path_label.pack(side="left")
        browse_btn = ctk.CTkButton(path_frame, text="Browse", command=self.browse)
        browse_btn.pack(side="right")

        # Display selected path
        self.path_display = ctk.CTkEntry(frame, textvariable=self.folder_path, state="readonly")
        self.path_display.pack(fill="x", **padding)

        # Step 2: backup checkbox
        self.backup_chk = ctk.CTkCheckBox(frame, text="2. Backup existing ReShade files", variable=self.backup_var)
        self.backup_chk.pack(anchor="w", **padding)

        # Step 3: install button
        self.install_btn = ctk.CTkButton(frame, text="Install", state="disabled", command=self.install)
        self.install_btn.pack(**padding)

        # Progress bar and percentage label
        self.progress = ctk.CTkProgressBar(frame, width=400)
        self.progress.pack(**padding)
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(frame, text="0%")
        self.progress_label.pack(**padding)

        # Log box
        log_label = ctk.CTkLabel(frame, text="Output:")
        log_label.pack(anchor="w", **padding)
        self.log_box = scrolledtext.ScrolledText(frame, height=8, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True, **padding)

    def update_progress(self, fraction: float) -> None:
        self.progress.set(fraction)
        percent = int(fraction * 100)
        self.progress_label.configure(text=f"{percent}%")
        self.root.update_idletasks()

    def browse(self) -> None:
        directory = filedialog.askdirectory(title="Select Bonelab Folder")
        if directory:
            self.folder_path.set(directory)
            self.install_btn.configure(state="normal")
            self.log(f"Selected folder: {directory}")
            self.update_progress(0)

    def log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def install(self) -> None:
        target = self.folder_path.get()
        if not target:
            messagebox.showerror("Error", "Please select the Bonelab folder.")
            return

        install_mod(target, self.backup_var.get(), self.log, self.update_progress)

        self.log("Installation complete!")
        messagebox.showinfo("Success", "Installation complete!")
        self.install_btn.configure(state="disabled")


def run_app() -> None:
    root = ctk.CTk() if USE_CUSTOM else tk.Tk()
    app = InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
