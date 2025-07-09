import os
import shutil
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

try:
    import customtkinter as ctk
    USE_CUSTOM = True
except ImportError:
    ctk = tk  # fall back to tkinter
    USE_CUSTOM = False


class InstallerApp:
    def __init__(self, root):
        self.root = root
        if USE_CUSTOM:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
        self.root.title("SpectrumB Bonelab Bodycam Installer")
        self.root.geometry("600x420")
        self.folder_path = tk.StringVar()
        self.backup_var = tk.BooleanVar()

        self.build_ui()

    def update_progress(self, fraction):
        self.progress.set(fraction)
        percent = int(fraction * 100)
        self.progress_label.configure(text=f"{percent}%")
        self.root.update_idletasks()

    def build_ui(self):
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

        # display selected path
        self.path_display = ctk.CTkEntry(frame, textvariable=self.folder_path, state="readonly")
        self.path_display.pack(fill="x", **padding)

        # Step 2: backup checkbox
        self.backup_chk = ctk.CTkCheckBox(frame, text="2. Backup existing ReShade files", variable=self.backup_var)
        self.backup_chk.pack(anchor="w", **padding)

        # Step 3: install button
        self.install_btn = ctk.CTkButton(frame, text="Install", state="disabled", command=self.install)
        self.install_btn.pack(**padding)

        # progress bar and percentage label
        self.progress = ctk.CTkProgressBar(frame, width=400)
        self.progress.pack(**padding)
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(frame, text="0%")
        self.progress_label.pack(**padding)

        # log box
        log_label = ctk.CTkLabel(frame, text="Output:")
        log_label.pack(anchor="w", **padding)
        self.log_box = scrolledtext.ScrolledText(frame, height=8, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True, **padding)

    def browse(self):
        directory = filedialog.askdirectory(title="Select Bonelab Folder")
        if directory:
            self.folder_path.set(directory)
            self.install_btn.configure(state="normal")
            self.log(f"Selected folder: {directory}")
            self.update_progress(0)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def install(self):
        target = self.folder_path.get()
        if not target:
            messagebox.showerror("Error", "Please select the Bonelab folder.")
            return

        files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
        items = [
            "dxgi.dll",
            "ReShade.ini",
            "ReShadePreset.ini",
            "reshade-shaders",
            "SpectrumB Bodycam",
        ]
        total = len(items)
        step = 1 / total
        self.update_progress(0)
        if self.backup_var.get():
            backup_dir = os.path.join(target, "reshade_backup")
            os.makedirs(backup_dir, exist_ok=True)
            for item in items:
                src = os.path.join(target, item)
                if os.path.exists(src):
                    dest = os.path.join(backup_dir, item)
                    try:
                        shutil.move(src, dest)
                        self.log(f"Backed up {item}")
                    except Exception as e:
                        self.log(f"Failed to backup {item}: {e}")
        for idx, item in enumerate(items, 1):
            src = os.path.join(files_dir, item)
            dest = os.path.join(target, item)
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dest)
                self.log(f"Copied {item}")
            except Exception as e:
                self.log(f"Failed to copy {item}: {e}")
            self.update_progress(idx * step)
        self.log("Installation complete!")
        messagebox.showinfo("Success", "Installation complete!")
        self.install_btn.configure(state="disabled")


def main():
    root = ctk.CTk() if USE_CUSTOM else tk.Tk()
    app = InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
