import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from converter import PDFToPPTConverter

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ePDF to ePPT Converter - Editable PowerPoint Creator")
        self.geometry("720 x 680")
        self.resizable(False, False)

        self.pdf_file_path = ""
        self.output_dir = ""

        self.setup_ui()

    def setup_ui(self):
        # Header Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="ePDF to ePPT Converter", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(15, 2))

        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Convert PDFs to 100% Editable PowerPoint Presentations", 
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 10))

        # Main File Frame
        self.card = ctk.CTkFrame(self, corner_radius=12)
        self.card.pack(padx=25, pady=5, fill="x")

        # Select PDF Section
        self.pdf_label = ctk.CTkLabel(self.card, text="Select PDF File:", font=ctk.CTkFont(size=13, weight="bold"))
        self.pdf_label.grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")

        self.pdf_entry = ctk.CTkEntry(self.card, placeholder_text="No file selected...", width=470)
        self.pdf_entry.grid(row=1, column=0, padx=(15, 10), pady=(0, 10), sticky="w")

        self.browse_pdf_btn = ctk.CTkButton(self.card, text="Browse PDF", width=120, command=self.browse_pdf)
        self.browse_pdf_btn.grid(row=1, column=1, padx=(0, 15), pady=(0, 10))

        # Select Output Dir Section
        self.out_label = ctk.CTkLabel(self.card, text="Output Directory:", font=ctk.CTkFont(size=13, weight="bold"))
        self.out_label.grid(row=2, column=0, padx=15, pady=(2, 2), sticky="w")

        self.out_entry = ctk.CTkEntry(self.card, placeholder_text="Same directory as PDF", width=470)
        self.out_entry.grid(row=3, column=0, padx=(15, 10), pady=(0, 12), sticky="w")

        self.browse_out_btn = ctk.CTkButton(self.card, text="Select Folder", width=120, command=self.browse_output_dir)
        self.browse_out_btn.grid(row=3, column=1, padx=(0, 15), pady=(0, 12))

        # Advanced Settings Frame (Toggles)
        self.options_card = ctk.CTkFrame(self, corner_radius=12)
        self.options_card.pack(padx=25, pady=10, fill="x")

        self.opts_title = ctk.CTkLabel(self.options_card, text="Conversion Options & Page Filters", font=ctk.CTkFont(size=13, weight="bold"))
        self.opts_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")

        # 1. Select Pages Toggle & Entry
        self.select_pages_var = tk.BooleanVar(value=False)
        self.select_pages_switch = ctk.CTkSwitch(
            self.options_card, 
            text="Select Pages", 
            variable=self.select_pages_var,
            command=self.toggle_select_pages
        )
        self.select_pages_switch.grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.select_pages_entry = ctk.CTkEntry(self.options_card, width=180, placeholder_text="e.g. 2")
        self.select_pages_entry.insert(0, "2")
        self.select_pages_entry.configure(state="disabled")
        self.select_pages_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        self.select_pages_hint = ctk.CTkLabel(self.options_card, text="(e.g. 2 or 1,3-5)", text_color="gray", font=ctk.CTkFont(size=11))
        self.select_pages_hint.grid(row=1, column=2, padx=5, pady=8, sticky="w")

        # 2. Ignore Pages Toggle & Entry
        self.ignore_pages_var = tk.BooleanVar(value=False)
        self.ignore_pages_switch = ctk.CTkSwitch(
            self.options_card, 
            text="Ignore Pages", 
            variable=self.ignore_pages_var,
            command=self.toggle_ignore_pages
        )
        self.ignore_pages_switch.grid(row=2, column=0, padx=15, pady=8, sticky="w")

        self.ignore_pages_entry = ctk.CTkEntry(self.options_card, width=180, placeholder_text="e.g. 3, 5-7")
        self.ignore_pages_entry.configure(state="disabled")
        self.ignore_pages_entry.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        self.ignore_pages_hint = ctk.CTkLabel(self.options_card, text="(e.g. 3, 5-7)", text_color="gray", font=ctk.CTkFont(size=11))
        self.ignore_pages_hint.grid(row=2, column=2, padx=5, pady=8, sticky="w")

        # 3. Custom Height Toggle & Entry
        self.custom_height_var = tk.BooleanVar(value=False)
        self.custom_height_switch = ctk.CTkSwitch(
            self.options_card, 
            text="Custom Height", 
            variable=self.custom_height_var,
            command=self.toggle_custom_height
        )
        self.custom_height_switch.grid(row=3, column=0, padx=15, pady=(8, 12), sticky="w")

        self.custom_height_entry = ctk.CTkEntry(self.options_card, width=180, placeholder_text="auto")
        self.custom_height_entry.insert(0, "auto")
        self.custom_height_entry.configure(state="disabled")
        self.custom_height_entry.grid(row=3, column=1, padx=10, pady=(8, 12), sticky="w")

        self.custom_height_hint = ctk.CTkLabel(self.options_card, text="px (beside auto)", text_color="gray", font=ctk.CTkFont(size=11))
        self.custom_height_hint.grid(row=3, column=2, padx=5, pady=(8, 12), sticky="w")

        # Log Text Box
        self.log_box = ctk.CTkTextbox(self, height=120, width=670, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.pack(padx=25, pady=5)
        self.log_box.insert("end", "Ready to convert. Select a PDF file to begin.\n")

        # Convert Action Button
        self.convert_btn = ctk.CTkButton(
            self, 
            text="Convert to Editable PPTX", 
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42,
            width=260,
            command=self.start_conversion
        )
        self.convert_btn.pack(pady=10)

    def toggle_select_pages(self):
        if self.select_pages_var.get():
            self.select_pages_entry.configure(state="normal")
        else:
            self.select_pages_entry.configure(state="disabled")

    def toggle_ignore_pages(self):
        if self.ignore_pages_var.get():
            self.ignore_pages_entry.configure(state="normal")
        else:
            self.ignore_pages_entry.configure(state="disabled")

    def toggle_custom_height(self):
        if self.custom_height_var.get():
            self.custom_height_entry.configure(state="normal")
        else:
            self.custom_height_entry.configure(state="disabled")

    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if filename:
            self.pdf_file_path = filename
            self.pdf_entry.delete(0, "end")
            self.pdf_entry.insert(0, filename)
            if not self.output_dir:
                self.output_dir = os.path.dirname(filename)
                self.out_entry.delete(0, "end")
                self.out_entry.insert(0, self.output_dir)

    def browse_output_dir(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir = folder
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, folder)

    def append_log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def start_conversion(self):
        pdf_path = self.pdf_entry.get().strip()
        out_dir = self.out_entry.get().strip()

        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return

        if not out_dir:
            out_dir = os.path.dirname(pdf_path)

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        ppt_path = os.path.join(out_dir, f"{base_name}_editable.pptx")

        # Parse option values
        select_str = self.select_pages_entry.get().strip() if self.select_pages_var.get() else ""
        ignore_str = self.ignore_pages_entry.get().strip() if self.ignore_pages_var.get() else ""
        
        custom_height = None
        if self.custom_height_var.get():
            h_val = self.custom_height_entry.get().strip().lower()
            if h_val != "auto" and h_val.isdigit():
                custom_height = int(h_val)

        self.convert_btn.configure(state="disabled", text="Converting...")
        self.append_log("\n--- Starting Conversion ---")

        threading.Thread(
            target=self._run_conversion, 
            args=(pdf_path, ppt_path, select_str, ignore_str, custom_height), 
            daemon=True
        ).start()

    def _run_conversion(self, pdf_path, ppt_path, select_str, ignore_str, custom_height):
        try:
            converter = PDFToPPTConverter(progress_callback=self.append_log)
            saved_files = converter.convert(
                pdf_path, 
                ppt_path, 
                select_pages_str=select_str, 
                ignore_pages_str=ignore_str, 
                custom_height_px=custom_height
            )
            files_formatted = "\n".join(saved_files)
            self.append_log(f"\nDone! Created presentation file(s):\n{files_formatted}")
            messagebox.showinfo("Success", f"Conversion completed successfully!\nCreated file(s):\n{files_formatted}")
        except Exception as e:
            self.append_log(f"\nError during conversion: {str(e)}")
            messagebox.showerror("Conversion Error", f"An error occurred:\n{str(e)}")
        finally:
            self.convert_btn.configure(state="normal", text="Convert to Editable PPTX")

if __name__ == "__main__":
    app = App()
    app.mainloop()

