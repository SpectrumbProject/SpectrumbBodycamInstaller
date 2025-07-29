#!/usr/bin/env python3
import os
import json
import threading
import shutil
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    try:
        return json.load(open(SETTINGS_FILE, "r", encoding="utf-8"))
    except:
        return {}

def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SpectrumB Installer Tool")
        self.minsize(450, 420)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(10, weight=1)

        self.settings = load_settings()
        self._build_ui()

    def _build_ui(self):
        pad = 8

        # Header
        ttk.Label(self, text="SpectrumB Installer Tool", font=("Segoe UI", 18))\
            .grid(row=0, column=0, pady=(12,6), sticky="n")

        # Win64 folder
        ttk.Label(self, text="Win64 Folder:")\
            .grid(row=1, column=0, sticky="w", padx=pad)
        f1 = ttk.Frame(self); f1.grid(row=2, column=0, sticky="ew", padx=pad)
        f1.columnconfigure(1, weight=1)
        self.win64_var = tk.StringVar(value=self.settings.get("win64_folder",""))
        ttk.Entry(f1, textvariable=self.win64_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(f1, text="Browse…", command=self._browse_win64).grid(row=0, column=2, padx=(6,0))

        # Normal Mods folder
        ttk.Label(self, text="Normal Mods Folder:")\
            .grid(row=3, column=0, sticky="w", padx=pad, pady=(12,0))
        f2 = ttk.Frame(self); f2.grid(row=4, column=0, sticky="ew", padx=pad)
        f2.columnconfigure(1, weight=1)
        self.mods_var = tk.StringVar(value=self.settings.get("normalmods_folder",""))
        ttk.Entry(f2, textvariable=self.mods_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(f2, text="Browse…", command=self._browse_mods).grid(row=0, column=2, padx=(6,0))

        # Temp Backup folder
        ttk.Label(self, text="Temp Backup Folder:")\
            .grid(row=5, column=0, sticky="w", padx=pad, pady=(12,0))
        self.temp_var = tk.StringVar(value=self._compute_temp(self.mods_var.get()))
        ttk.Entry(self, textvariable=self.temp_var, state="readonly")\
            .grid(row=6, column=0, sticky="ew", padx=pad)

        ttk.Separator(self, orient="horizontal")\
            .grid(row=7, column=0, sticky="ew", pady=(18,6), padx=pad)

        # Bodycam install
        ttk.Label(self, text="Install SpectrumB Bodycam from RAR Archive", font=("Segoe UI", 12))\
            .grid(row=8, column=0, sticky="w", padx=pad)
        bf = ttk.Frame(self); bf.grid(row=9, column=0, sticky="ew", padx=pad, pady=(4,12))
        bf.columnconfigure(1, weight=1)
        self.bodycam_var = tk.StringVar(value=self.settings.get("bodycam_archive",""))
        ttk.Label(bf, text="From:").grid(row=0, column=0)
        ttk.Entry(bf, textvariable=self.bodycam_var).grid(row=0, column=1, sticky="ew", padx=(4,4))
        ttk.Button(bf, text="Browse…", command=self._browse_bodycam).grid(row=0, column=2)
        self.btn_bodycam = ttk.Button(bf, text="Install", command=self._install_bodycam)
        self.btn_bodycam.grid(row=1, column=1, sticky="w", pady=(8,0))
        self.bodycam_progress = ttk.Progressbar(bf, mode="indeterminate")

        # Event Prepare Settings
        grp = ttk.Labelframe(self, text="Event Prepare Settings", padding=pad)
        grp.grid(row=10, column=0, sticky="nsew", padx=pad, pady=(0,12))
        grp.columnconfigure(0, weight=1)

        self.event_mode = tk.StringVar(value="backup")
        ttk.Radiobutton(grp, text="Backup all Mods to Temp",
                        variable=self.event_mode, value="backup")\
            .grid(row=0, column=0, sticky="w", pady=2)
        ttk.Radiobutton(grp, text="Restore all Mods from Temp to Mods",
                        variable=self.event_mode, value="restore")\
            .grid(row=1, column=0, sticky="w", pady=2)

        self.btn_event = ttk.Button(grp, text="Run Selection", command=self._run_event_prepare)
        self.btn_event.grid(row=2, column=0, sticky="w", pady=(8,0))
        self.event_progress = ttk.Progressbar(grp, mode="determinate")

        # Save settings checkbox
        self.save_var = tk.BooleanVar(value=self.settings.get("save_all", True))
        ttk.Checkbutton(self, text="Save settings for next time", variable=self.save_var)\
            .grid(row=11, column=0, sticky="e", padx=pad, pady=(0,12))

        # Status bar
        self.status = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status.grid(row=12, column=0, sticky="ew", padx=pad)

        # Watermark
        ttk.Label(self, text="v0.1.4", font=("Segoe UI", 8), foreground="gray50")\
            .grid(row=13, column=0, sticky="e", padx=pad, pady=(0,4))

    def _compute_temp(self, mods_folder):
        if mods_folder:
            tmp = os.path.join(mods_folder, "temp_backup")
            os.makedirs(tmp, exist_ok=True)
            return tmp
        return ""

    def _browse_win64(self):
        d = filedialog.askdirectory(title="Select Win64 Folder")
        if d:
            self.win64_var.set(d)
            if self.save_var.get():
                self.settings["win64_folder"] = d
                save_settings(self.settings)

    def _browse_mods(self):
        d = filedialog.askdirectory(title="Select Normal Mods Folder")
        if d:
            self.mods_var.set(d)
            tmp = os.path.join(d, "temp_backup")
            os.makedirs(tmp, exist_ok=True)
            self.temp_var.set(tmp)
            if self.save_var.get():
                self.settings["normalmods_folder"] = d
                save_settings(self.settings)

    def _browse_bodycam(self):
        f = filedialog.askopenfilename(title="Select Bodycam RAR",
                                        filetypes=[("RAR","*.rar")])
        if f:
            self.bodycam_var.set(f)
            if self.save_var.get():
                self.settings["bodycam_archive"] = f
                save_settings(self.settings)

    def _install_bodycam(self):
        arc, dst = self.bodycam_var.get(), self.win64_var.get()
        if not os.path.isfile(arc):
            return messagebox.showwarning("Missing","Select a valid archive.")
        if not os.path.isdir(dst):
            return messagebox.showwarning("Missing","Select a valid Win64 folder.")

        self.btn_bodycam.grid_forget()
        self.bodycam_progress.grid(row=1, column=1, sticky="ew", pady=(8,0))
        self.bodycam_progress.start(50)
        self.status.config(text="Installing Bodycam...")
        threading.Thread(target=self._do_install_bodycam, daemon=True).start()

    def _do_install_bodycam(self):
        try:
            ex = self._find_extractor()
            ext = os.path.splitext(self.bodycam_var.get())[1].lower()
            if ext == ".zip":
                with zipfile.ZipFile(self.bodycam_var.get(), "r") as z:
                    members = z.infolist()
                    total = len(members)
                    self.bodycam_progress.config(mode="determinate",
                                                 maximum=total, value=0)
                    for i, m in enumerate(members, 1):
                        z.extract(m, self.win64_var.get())
                        self.bodycam_progress["value"] = i
            else:
                self._extract(self.bodycam_var.get(), self.win64_var.get(), ex)
            self.status.config(text="Bodycam installed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Error.")
        finally:
            self.bodycam_progress.stop()
            self.bodycam_progress.grid_forget()
            self.bodycam_progress.config(mode="indeterminate")
            self.btn_bodycam.grid(row=1, column=1, sticky="w", pady=(8,0))

    def _run_event_prepare(self):
        mode = self.event_mode.get()
        src, dst = self.mods_var.get(), self.temp_var.get()
        if self.save_var.get():
            self.settings["backup_src"]  = src
            self.settings["backup_dst"]  = dst
            self.settings["restore_src"] = dst
            self.settings["restore_dst"] = src
            save_settings(self.settings)

        if not os.path.isdir(src) or not os.path.isdir(dst):
            return messagebox.showwarning("Missing","Select valid Mods & Temp folders.")

        self.btn_event.grid_forget()
        self.event_progress.grid(row=2, column=0, sticky="ew", pady=(8,0))
        if mode == "backup":
            items = [e for e in os.listdir(src)
                     if os.path.abspath(os.path.join(src, e)) != os.path.abspath(dst)]
        else:
            items = os.listdir(dst)
        total = len(items)
        self.event_progress.config(mode="determinate",
                                   maximum=total, value=0)
        self.status.config(text=f"{mode.title()} in progress...")
        threading.Thread(target=self._do_event,
                         args=(mode, src, dst, items), daemon=True).start()

    def _do_event(self, mode, src, dst, items):
        try:
            for i, name in enumerate(items, 1):
                if mode == "backup":
                    msrc = os.path.join(src, name)
                    out  = os.path.join(dst, name)
                else:
                    msrc = os.path.join(dst, name)
                    out  = os.path.join(src, name)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.move(msrc, out)
                self.event_progress["value"] = i
                self.status.config(text=f"{mode.title()} {i}/{len(items)}")
            self.status.config(text=f"{mode.title()} complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Error.")
        finally:
            self.event_progress.grid_forget()
            self.btn_event.grid(row=2, column=0, sticky="w", pady=(8,0))

    def _find_extractor(self):
        here = os.path.dirname(__file__)
        bund = os.path.join(here, "UnRAR.exe")
        if os.path.isfile(bund):
            return bund
        for pf in (os.environ.get("ProgramFiles"),
                   os.environ.get("ProgramFiles(x86)")):
            if pf:
                p = os.path.join(pf, "WinRAR", "UnRAR.exe")
                if os.path.isfile(p):
                    return p
        for exe in ("7z","7za","7zr"):
            p = shutil.which(exe)
            if p:
                return p
        raise RuntimeError("No extractor found! Install UnRAR.exe or 7-Zip/WinRAR.")

    def _extract(self, src, dst, ex):
        ext = os.path.splitext(src)[1].lower()
        if ext == ".zip":
            with zipfile.ZipFile(src, "r") as z:
                for m in z.infolist():
                    z.extract(m, dst)
            return
        name = os.path.basename(ex).lower()
        cmd = ([ex, "x", "-o+", src, dst]
               if name.startswith("unrar")
               else [ex, "x", src, f"-o{dst}", "-y"])
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    App().mainloop()
