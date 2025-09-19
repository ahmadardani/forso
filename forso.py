#!/usr/bin/env python3
import re
import tkinter as tk
from tkinter import ttk, messagebox

# =========================
# --- TAB 1 FUNCTIONS ---
# =========================
MARKER_ONLY = re.compile(r'^\s*([A-Za-z])\s*$')
OPTION_START = re.compile(r'^\s*[A-Za-z](?:\.|\)|\s)')

def preprocess_merge_markers(lines):
    i, out, n = 0, [], len(lines)
    while i < n:
        line = lines[i]
        m = MARKER_ONLY.match(line)
        if m:
            j = i + 1
            while j < n and lines[j].strip() == '':
                j += 1
            if j < n:
                merged = f"{m.group(1)} {lines[j].strip()}"
                out.append(merged)
                i = j + 1
                continue
            else:
                out.append(line)
                i += 1
        else:
            out.append(line)
            i += 1
    return out

def split_into_paragraphs(lines):
    paragraphs, buf = [], []
    for ln in lines:
        if ln.strip() == '':
            if buf:
                paragraphs.append(buf)
                buf = []
        else:
            buf.append(ln.rstrip())
    if buf:
        paragraphs.append(buf)
    return paragraphs

def process_paragraph(par):
    opt_idx = None
    for idx, ln in enumerate(par):
        if OPTION_START.match(ln):
            opt_idx = idx
            break
    contains_q = any('...' in ln for ln in par)
    if contains_q:
        q_lines = par if opt_idx is None else par[:opt_idx]
        opts = [] if opt_idx is None else par[opt_idx:]
        question = ' '.join(ln.strip() for ln in q_lines).strip()
        out = [question] + [opt.strip() for opt in opts]
        return '\n'.join(out)
    else:
        return ' '.join(ln.strip() for ln in par).strip()

def transform_tab1(text: str) -> str:
    lines = text.splitlines()
    merged = preprocess_merge_markers(lines)
    paras = split_into_paragraphs(merged)
    result_blocks, q_num = [], 1
    for p in paras:
        if any('...' in ln for ln in p):
            formatted = process_paragraph(p)
            parts = formatted.split('\n', 1)
            parts[0] = f"{q_num}. {parts[0]}"
            q_num += 1
            result_blocks.append('\n'.join(parts))
        else:
            result_blocks.append(' '.join(ln.strip() for ln in p))
    return '\n\n'.join(result_blocks)


# =========================
# --- TAB 2 FUNCTIONS ---
# =========================
def is_marker(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if len(s) <= 4 and ' ' not in s:
        return True
    return False

def transform_tab2(text: str) -> str:
    lines = text.splitlines()
    out_lines, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if is_marker(line):
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and not is_marker(lines[j]):
                marker = line.strip().rstrip('. )')
                desc = lines[j].strip()
                out_lines.append(f"{marker} {desc}")
                i = j + 1
                continue
            else:
                out_lines.append(line.strip())
                i += 1
                continue
        else:
            if line.strip() == "":
                if out_lines and out_lines[-1] != "":
                    out_lines.append("")
            else:
                out_lines.append(line.rstrip())
            i += 1
    while out_lines and out_lines[0] == "":
        out_lines.pop(0)
    while out_lines and out_lines[-1] == "":
        out_lines.pop()
    return "\n".join(out_lines)


# =========================
# --- TAB 3 FUNCTIONS ---
# =========================
def number_questions_paragraphs(text: str) -> str:
    if not text.strip():
        return text
    paragraphs = re.split(r"\n\s*\n", text)
    out_pars, q_num = [], 1
    for p in paragraphs:
        if '...' in p:
            p_no_leading_num = re.sub(r'^\s*(?:\d+\.\s*|\d+\)\s*|\(\d+\)\s*)', '', p)
            p_no_leading_num = p_no_leading_num.lstrip()
            new_p = f"{q_num}. {p_no_leading_num}"
            out_pars.append(new_p)
            q_num += 1
        else:
            out_pars.append(p)
    return "\n\n".join(out_pars)


# =========================
# --- MAIN APP WITH TABS ---
# =========================
class TabFrame(ttk.Frame):
    def __init__(self, master, transform_func, sample=""):
        super().__init__(master, padding=10)
        lbl_in = ttk.Label(self, text="Input text")
        lbl_in.grid(row=0, column=0, sticky=tk.W)
        lbl_out = ttk.Label(self, text="Output text")
        lbl_out.grid(row=0, column=1, sticky=tk.W)

        self.txt_in = tk.Text(self, wrap=tk.WORD)
        self.txt_out = tk.Text(self, wrap=tk.WORD)

        self.txt_in.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.txt_out.grid(row=1, column=1, sticky="nsew")

        # Frame tombol (isi 2 subframe: kiri & kanan)
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        left_frame = ttk.Frame(btn_frame)
        right_frame = ttk.Frame(btn_frame)
        left_frame.pack(side=tk.LEFT, anchor="w")
        right_frame.pack(side=tk.RIGHT, anchor="e")

        self.transform_func = transform_func
        btn_transform = ttk.Button(left_frame, text="Transform", command=self.on_transform)
        btn_clear = ttk.Button(right_frame, text="Clear All", command=self.on_clear)
        btn_copy = ttk.Button(right_frame, text="Copy Output", command=self.on_copy)

        btn_transform.pack(side=tk.LEFT)
        btn_copy.pack(side=tk.RIGHT, padx=(0, 8))
        btn_clear.pack(side=tk.RIGHT)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        if sample:
            self.txt_in.insert("1.0", sample)

    def on_transform(self):
        src = self.txt_in.get("1.0", tk.END)
        if not src.strip():
            messagebox.showinfo("Info", "Masukkan teks terlebih dahulu.")
            return
        try:
            result = self.transform_func(src)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memproses teks: {e}")
            return
        self.txt_out.delete("1.0", tk.END)
        self.txt_out.insert("1.0", result)

    def on_clear(self):
        self.txt_in.delete("1.0", tk.END)
        self.txt_out.delete("1.0", tk.END)

    def on_copy(self):
        out = self.txt_out.get("1.0", tk.END).strip()
        if not out:
            return
        self.clipboard_clear()
        self.clipboard_append(out)
        messagebox.showinfo("Copied", "Output copied to clipboard.")


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forso")
        self.geometry("960x600")

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1
        sample1 = (
            "Komponen model simulasi yang digunakan oleh entitas untuk menyelesaikan\n"
            "tugasnya adalah...\n"
            "a\n\nAtribut\n\nb\n\nKeadaan\n\nc\n\nEntitas\n\n"
            "d\n\nSumber Daya\n\ne\n\nAktivitas"
        )
        tab1 = TabFrame(notebook, transform_tab1, sample1)
        notebook.add(tab1, text="Perbaiki Soal dan Jawaban")

        # Tab 2
        sample2 = (
            "a\n\nAtribut\n\nb\n\nKeadaan\n\nc\n\nEntitas\n\nd\n\nSumber Daya\n\ne\n\nAktivitas"
        )
        tab2 = TabFrame(notebook, transform_tab2, sample2)
        notebook.add(tab2, text="Perbaiki Pilihan Jawaban")

        # Tab 3
        sample3 = (
            "Komponen model simulasi yang digunakan oleh entitas untuk menyelesaikan\n"
            "tugasnya adalah...\n\n"
            "a Atribut\n\nb Keadaan\n\nc Entitas\n\nd Sumber Daya\n\ne Aktivitas\n\n"
            "Tujuan utama dari tahap Analisis Hasil dan Dokumentasi adalah...\n\n"
            "a Mengumpulkan data input\n\nb Memastikan model dibangun dengan benar"
        )
        tab3 = TabFrame(notebook, number_questions_paragraphs, sample3)
        notebook.add(tab3, text="Mengisi Nomor Soal")

        # Tab 4 (Tentang)
        tab4 = ttk.Frame(notebook, padding=20)
        lbl_about = ttk.Label(
            tab4,
            text=(
                "FAQ\n\n"
                "Mengapa formatnya tidak berhasil dengan baik?\n"
		"Kemungkinan soal yang kamu cantumkan tidak ada tanda baca ... di akhir soal jadinya mungkin terlihat sedikit berantakan.\n"
                "\n\n"
                "Apakah ada rencana untuk update software ini? Untuk beberapa soal yang gagal di format?\n"
		"Untuk sekarang masih tidak kepikiran untuk memperbaruinya atau memperbaikinya. Tapi dilain waktu saya akan update\n"
            ),
            justify="center"
        )
        lbl_about.pack(expand=True, anchor="center")
        notebook.add(tab4, text="FAQ")

        # Tab 5 (Tentang)
        tab5 = ttk.Frame(notebook, padding=20)
        lbl_about = ttk.Label(
            tab5,
            text=(
                "Forso v1.0\n\n"
                "Software untuk memperbaiki format soal.\n"
                "\n"
                "© 2025 - Copyright."
            ),
            justify="center"
        )
        lbl_about.pack(expand=True, anchor="center")
        notebook.add(tab5, text="Tentang")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
