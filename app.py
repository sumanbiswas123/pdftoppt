import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from converter import PDFToPPTConverter
from ppt_to_html import PPTToHTMLEmailConverter
from json_extractor import AIDesignPackageExtractor, compile_mjml_to_html

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ePDF to ePPT & HTML Email Template Converter")
        self.geometry("740x780")
        self.resizable(False, False)

        self.pdf_file_path = ""
        self.output_dir = ""

        # Title / Header
        self.title_label = ctk.CTkLabel(
            self, 
            text="ePDF to ePPT & HTML Email Studio", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=(15, 3))

        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Universal PDF -> Editable PPTX, Responsive HTML Email & AI Design Extractor", 
            font=ctk.CTkFont(size=12),
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
        self.options_card.pack(padx=25, pady=8, fill="x")

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
        self.select_pages_switch.grid(row=1, column=0, padx=15, pady=6, sticky="w")

        self.select_pages_entry = ctk.CTkEntry(self.options_card, width=180, placeholder_text="e.g. 1")
        self.select_pages_entry.insert(0, "1")
        self.select_pages_entry.configure(state="disabled")
        self.select_pages_entry.grid(row=1, column=1, padx=10, pady=6, sticky="w")

        self.select_pages_hint = ctk.CTkLabel(self.options_card, text="(e.g. 1 or 1,3-5)", text_color="gray", font=ctk.CTkFont(size=11))
        self.select_pages_hint.grid(row=1, column=2, padx=5, pady=6, sticky="w")

        # 2. Ignore Pages Toggle & Entry
        self.ignore_pages_var = tk.BooleanVar(value=False)
        self.ignore_pages_switch = ctk.CTkSwitch(
            self.options_card, 
            text="Ignore Pages", 
            variable=self.ignore_pages_var,
            command=self.toggle_ignore_pages
        )
        self.ignore_pages_switch.grid(row=2, column=0, padx=15, pady=6, sticky="w")

        self.ignore_pages_entry = ctk.CTkEntry(self.options_card, width=180, placeholder_text="e.g. 3, 5-7")
        self.ignore_pages_entry.configure(state="disabled")
        self.ignore_pages_entry.grid(row=2, column=1, padx=10, pady=6, sticky="w")

        self.ignore_pages_hint = ctk.CTkLabel(self.options_card, text="(e.g. 3, 5-7)", text_color="gray", font=ctk.CTkFont(size=11))
        self.ignore_pages_hint.grid(row=2, column=2, padx=5, pady=6, sticky="w")

        # 3. Custom Height Toggle & Entry
        self.custom_height_var = tk.BooleanVar(value=False)
        self.custom_height_switch = ctk.CTkSwitch(
            self.options_card, 
            text="Custom Height", 
            variable=self.custom_height_var,
            command=self.toggle_custom_height
        )
        self.custom_height_switch.grid(row=3, column=0, padx=15, pady=(6, 10), sticky="w")

        self.custom_height_entry = ctk.CTkEntry(self.options_card, width=180, placeholder_text="auto")
        self.custom_height_entry.insert(0, "auto")
        self.custom_height_entry.configure(state="disabled")
        self.custom_height_entry.grid(row=3, column=1, padx=10, pady=(6, 10), sticky="w")

        self.custom_height_hint = ctk.CTkLabel(self.options_card, text="px (beside auto)", text_color="gray", font=ctk.CTkFont(size=11))
        self.custom_height_hint.grid(row=3, column=2, padx=5, pady=(6, 6), sticky="w")

        # 4. Email Width Switch / Selector (700px, 650px, 600px)
        self.email_width_label = ctk.CTkLabel(
            self.options_card, 
            text="Email Width", 
            font=ctk.CTkFont(weight="bold")
        )
        self.email_width_label.grid(row=4, column=0, padx=15, pady=(6, 12), sticky="w")

        self.email_width_var = tk.StringVar(value="700px")
        self.email_width_seg = ctk.CTkSegmentedButton(
            self.options_card,
            values=["700px", "650px", "600px"],
            variable=self.email_width_var,
            width=220,
            command=self.update_email_width_hint
        )
        self.email_width_seg.grid(row=4, column=1, padx=10, pady=(6, 12), sticky="w")

        self.email_width_hint = ctk.CTkLabel(
            self.options_card, 
            text="(Inner Content: 660px)", 
            text_color="gray", 
            font=ctk.CTkFont(size=11)
        )
        self.email_width_hint.grid(row=4, column=2, padx=5, pady=(6, 12), sticky="w")

        # Log Text Box
        self.log_box = ctk.CTkTextbox(self, height=120, width=670, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.pack(padx=25, pady=5)
        self.log_box.insert("end", "Ready. Select a PDF file and choose your desired conversion.\n")

        # Buttons Frame (Conversion Pipeline Options)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=8)

        # Row 0 - Option A: Convert to PPTX
        self.convert_ppt_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Convert to Editable PPTX", 
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            width=230,
            command=lambda: self.start_conversion(generate_html=False)
        )
        self.convert_ppt_btn.grid(row=0, column=0, padx=6, pady=4)

        # Row 0 - Option B: Convert to HTML Email
        self.convert_html_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Convert to HTML Email Template", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1f7a4d",
            hover_color="#165b38",
            height=38,
            width=270,
            command=lambda: self.start_conversion(generate_html=True)
        )
        self.convert_html_btn.grid(row=0, column=1, padx=6, pady=4)

        # Row 1 - Option C: Export AI Package (JSON + Assets)
        self.export_ai_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Export AI Package (JSON + Assets)", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#205493",
            hover_color="#153d6b",
            height=38,
            width=280,
            command=self.start_ai_package_export
        )
        self.export_ai_btn.grid(row=1, column=0, padx=6, pady=4)

        # Row 1 - Option D: Paste & Compile MJML to HTML
        self.compile_mjml_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Paste & Compile MJML to HTML Email", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#6f42c1",
            hover_color="#59339d",
            height=38,
            width=260,
            command=self.open_mjml_compiler_dialog
        )
        self.compile_mjml_btn.grid(row=1, column=1, padx=6, pady=4)

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

    def update_email_width_hint(self, value):
        try:
            width_num = int(value.replace("px", ""))
            inner_num = width_num - 40
            self.email_width_hint.configure(text=f"(Inner Content: {inner_num}px)")
        except Exception:
            pass

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
            
            # Check PDF page count for smart hint
            try:
                import fitz
                doc = fitz.open(filename)
                num_p = len(doc)
                doc.close()
                if num_p == 1:
                    self.select_pages_hint.configure(text="(1 page total)")
                    self.select_pages_entry.delete(0, "end")
                    self.select_pages_entry.insert(0, "1")
                else:
                    self.select_pages_hint.configure(text=f"(e.g. 1-{num_p})")
            except Exception:
                pass

    def browse_output_dir(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir = folder
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, folder)

    def append_log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def start_conversion(self, generate_html=False):
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

        self.convert_ppt_btn.configure(state="disabled")
        self.convert_html_btn.configure(state="disabled")
        
        if generate_html:
            self.convert_html_btn.configure(text="Generating HTML Email...")
            self.append_log("\n--- Starting PDF -> PPT -> HTML Email Pipeline ---")
        else:
            self.convert_ppt_btn.configure(text="Converting to PPT...")
            self.append_log("\n--- Starting PDF to PPT Conversion ---")

        threading.Thread(
            target=self._run_conversion, 
            args=(pdf_path, ppt_path, select_str, ignore_str, custom_height, generate_html), 
            daemon=True
        ).start()

    def _run_conversion(self, pdf_path, ppt_path, select_str, ignore_str, custom_height, generate_html):
        try:
            # Step 1: Convert PDF to PPTX
            converter = PDFToPPTConverter(progress_callback=self.append_log)
            saved_ppt_files = converter.convert(
                pdf_path, 
                ppt_path, 
                select_pages_str=select_str, 
                ignore_pages_str=ignore_str, 
                custom_height_px=custom_height
            )

            all_results = list(saved_ppt_files)

            # Step 2: Convert PPTX to Responsive HTML Email Template (if selected)
            if generate_html and saved_ppt_files:
                try:
                    width_val = int(self.email_width_var.get().replace("px", ""))
                except Exception:
                    width_val = 700
                self.append_log(f"\n--- Generating Responsive HTML Email Template ({width_val}px) ---")
                html_converter = PPTToHTMLEmailConverter(progress_callback=self.append_log)
                
                for ppt_file in saved_ppt_files:
                    base_no_ext, _ = os.path.splitext(ppt_file)
                    html_file = f"{base_no_ext}_email.html"
                    saved_html, _ = html_converter.convert(ppt_file, html_file, email_width=width_val)
                    all_results.append(saved_html)

            files_formatted = "\n".join(all_results)
            self.append_log(f"\nDone! Created file(s):\n{files_formatted}")
            messagebox.showinfo("Success", f"Conversion completed successfully!\n\nCreated file(s):\n{files_formatted}")
        except Exception as e:
            self.append_log(f"\nError during conversion: {str(e)}")
            messagebox.showerror("Conversion Error", f"An error occurred:\n{str(e)}")
        finally:
            self.convert_ppt_btn.configure(state="normal", text="Convert to Editable PPTX")
            self.convert_html_btn.configure(state="normal", text="Convert to HTML Email Template")

    def start_ai_package_export(self):
        pdf_path = self.pdf_entry.get().strip()
        out_dir = self.out_entry.get().strip()

        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return

        if not out_dir:
            out_dir = os.path.dirname(pdf_path)

        select_str = self.select_pages_entry.get().strip() if self.select_pages_var.get() else ""
        ignore_str = self.ignore_pages_entry.get().strip() if self.ignore_pages_var.get() else ""
        
        try:
            width_val = int(self.email_width_var.get().replace("px", ""))
        except Exception:
            width_val = 700

        self.append_log(f"\n--- Exporting AI Design Package ({width_val}px container) ---")
        try:
            extractor = AIDesignPackageExtractor(progress_callback=self.append_log)
            pkg_dir, json_file = extractor.extract(
                pdf_path, 
                out_dir, 
                select_pages_str=select_str, 
                ignore_pages_str=ignore_str,
                email_width=width_val
            )
            self.append_log(f"\nAI Design Package exported to:\n{pkg_dir}")
            messagebox.showinfo("AI Package Exported", f"AI Package successfully created!\n\nLocation:\n{pkg_dir}\n\nWidth: {width_val}px (Inner: {width_val - 40}px)\n\nIncludes:\n- Design JSON\n- Visual Screenshot (>= {width_val}px)\n- Assets Folder")
        except Exception as e:
            self.append_log(f"\nError exporting AI package: {str(e)}")
            messagebox.showerror("Export Error", f"An error occurred:\n{str(e)}")

    def open_mjml_compiler_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Paste & Compile MJML to HTML Email")
        dialog.geometry("640x540")
        dialog.resizable(True, True)

        # Ensure dialog always opens in front of the main window and grabs focus
        dialog.transient(self)
        dialog.lift()
        dialog.focus_force()
        dialog.attributes("-topmost", True)
        dialog.after(200, lambda: dialog.attributes("-topmost", False))

        lbl = ctk.CTkLabel(dialog, text="Paste the MJML generated by Gemini / AI below:", font=ctk.CTkFont(size=13, weight="bold"))
        lbl.pack(padx=20, pady=(15, 5), anchor="w")

        text_box = ctk.CTkTextbox(dialog, height=360, width=600, font=ctk.CTkFont(family="Consolas", size=11))
        text_box.pack(padx=20, pady=5, fill="both", expand=True)

        btn_box = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_box.pack(pady=12)

        def do_compile():
            mjml_code = text_box.get("1.0", "end").strip()
            if not mjml_code:
                messagebox.showwarning("Warning", "Please paste your MJML code first.", parent=dialog)
                return

            save_file = filedialog.asksaveasfilename(
                title="Save Compiled HTML Email",
                defaultextension=".html",
                filetypes=[("HTML Email Template", "*.html")]
            )
            if save_file:
                try:
                    compile_mjml_to_html(mjml_code, save_file)
                    messagebox.showinfo("Success", f"HTML Email successfully compiled and saved to:\n{save_file}", parent=dialog)
                    dialog.destroy()
                except Exception as err:
                    messagebox.showerror("MJML Compile Error", f"Failed to compile MJML:\n{str(err)}", parent=dialog)

        compile_btn = ctk.CTkButton(
            btn_box, 
            text="Compile to HTML Email (.html)", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#6f42c1",
            hover_color="#59339d",
            height=36,
            width=220,
            command=do_compile
        )
        compile_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(btn_box, text="Close", width=100, height=36, command=dialog.destroy)
        cancel_btn.pack(side="left", padx=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()

