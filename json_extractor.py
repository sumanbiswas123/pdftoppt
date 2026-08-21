import os
import io
import json
import html
import re
import fitz  # PyMuPDF
import mrml

def rgb_tuple_to_hex(rgb):
    if not rgb:
        return None
    try:
        r = int(round(rgb[0] * 255))
        g = int(round(rgb[1] * 255))
        b = int(round(rgb[2] * 255))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return None

def rgb_int_to_hex(color_int):
    if isinstance(color_int, int):
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#222222"

def clean_email_text(text):
    if not text:
        return ""
    text = text.replace('\xa0', ' ')
    text = text.replace('\ufffd', '')
    text = text.replace('\x00', '')
    return text

def parse_page_spec(spec_str, total_pages):
    pages = set()
    if not spec_str:
        return set(range(total_pages))
    parts = [p.strip() for p in spec_str.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            subparts = part.split("-")
            if len(subparts) == 2 and subparts[0].isdigit() and subparts[1].isdigit():
                start, end = int(subparts[0]), int(subparts[1])
                for p in range(start, end + 1):
                    if 1 <= p <= total_pages:
                        pages.add(p - 1)
        elif part.isdigit():
            p = int(part)
            if 1 <= p <= total_pages:
                pages.add(p - 1)
    return pages

class AIDesignPackageExtractor:
    """
    Extracts high-fidelity design assets, page screenshots (minimum 700px width),
    and a complete structured JSON for selected pages only.
    """
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def log(self, message):
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def extract(self, pdf_path, output_dir=None, select_pages_str="", ignore_pages_str=""):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        if not output_dir:
            output_dir = os.path.dirname(os.path.abspath(pdf_path))

        package_dir = os.path.join(output_dir, f"{base_name}_ai_package")
        assets_dir = os.path.join(package_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        self.log(f"Opening PDF: {os.path.basename(pdf_path)}...")
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        if total_pages == 0:
            raise ValueError("PDF file contains no pages.")

        # Determine target pages
        if select_pages_str and select_pages_str.strip():
            selected_set = parse_page_spec(select_pages_str, total_pages)
            if not selected_set:
                if total_pages == 1:
                    self.log(f"Notice: Selection '{select_pages_str}' out of range for 1-page PDF. Defaulting to Page 1.")
                    selected_set = {0}
                else:
                    raise ValueError(f"Selected pages '{select_pages_str}' are out of range (PDF has {total_pages} page(s)).")
        else:
            selected_set = set(range(total_pages))

        if ignore_pages_str and ignore_pages_str.strip():
            ignored_set = parse_page_spec(ignore_pages_str, total_pages)
        else:
            ignored_set = set()

        final_pages = [p for p in range(total_pages) if p in selected_set and p not in ignored_set]
        if not final_pages:
            raise ValueError(f"No pages left to convert after applying filters. Selected: {selected_set}, Ignored: {ignored_set}.")

        self.log(f"Extracting AI Design Package for {len(final_pages)} page(s): {[p+1 for p in final_pages]}...")

        package_data = {
            "document_name": os.path.basename(pdf_path),
            "total_pages": len(final_pages),
            "target_email_specs": {
                "container_width": "700px",
                "padding_left_right": "20px",
                "content_width": "660px",
                "framework": "MJML"
            },
            "pages": []
        }

        img_counter = 0

        for page_idx in final_pages:
            page = doc[page_idx]
            rect = page.rect
            scale = 660.0 / rect.width if rect.width > 0 else 1.0
            pdf_links = page.get_links()

            # 1. Render Full High-Resolution Page Preview (Minimum 700px width guaranteed)
            page_preview_filename = f"page_{page_idx+1}_preview.png"
            page_preview_path = os.path.join(package_dir, page_preview_filename)
            
            # Guarantee minimum 700px pixel width for screenshot
            min_width_px = max(700.0, rect.width)
            zoom_w = max(1.0, 700.0 / rect.width if rect.width > 0 else 1.0)
            render_matrix = fitz.Matrix(zoom_w * 1.5, zoom_w * 1.5)
            page_pix = page.get_pixmap(matrix=render_matrix, alpha=False)
            page_pix.save(page_preview_path)

            page_dict = {
                "page_number": page_idx + 1,
                "canvas_width_pt": rect.width,
                "canvas_height_pt": rect.height,
                "page_preview_image": page_preview_filename,
                "preview_pixel_width": page_pix.width,
                "preview_pixel_height": page_pix.height,
                "elements": []
            }

            # 2. Extract Vector Background Cards (Fills & Coordinates)
            bg_cards = []
            for draw in page.get_drawings():
                d_rect = fitz.Rect(draw.get("rect"))
                if d_rect.width < 12 or d_rect.height < 10:
                    continue
                if d_rect.width >= rect.width * 0.95 and d_rect.height >= rect.height * 0.95:
                    continue
                
                fill_hex = rgb_tuple_to_hex(draw.get("fill"))
                stroke_hex = rgb_tuple_to_hex(draw.get("color"))
                if fill_hex and fill_hex not in ["#ffffff"]:
                    bg_cards.append({
                        "rect": d_rect,
                        "bbox": [round(d_rect.x0, 1), round(d_rect.y0, 1), round(d_rect.x1, 1), round(d_rect.y1, 1)],
                        "fill_color": fill_hex,
                        "stroke_color": stroke_hex
                    })

            # 3. Extract Raster Images & Crop Crisp High-Quality Assets
            images_data = []
            asset_dpi = max(200, int(72.0 * zoom_w * 2.0))
            for img in page.get_images(full=True):
                xref = img[0]
                for r in page.get_image_rects(xref):
                    if r.height <= 3.0 or r.width <= 3.0:
                        continue
                    if r.width >= rect.width * 0.95 and r.height >= rect.height * 0.95:
                        continue

                    img_link = None
                    for lk in pdf_links:
                        l_rect = lk.get("from")
                        if l_rect and r.intersects(l_rect):
                            img_link = lk.get("uri")
                            break

                    pix = page.get_pixmap(clip=r, dpi=asset_dpi, colorspace=fitz.csRGB)
                    img_counter += 1
                    img_filename = f"asset_p{page_idx+1}_{img_counter}.png"
                    img_path = os.path.join(assets_dir, img_filename)
                    pix.save(img_path)

                    w_px = min(660, max(16, int(r.width * scale)))
                    h_px = int(r.height * scale)

                    images_data.append({
                        "type": "image",
                        "bbox": [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)],
                        "top": r.y0,
                        "left": r.x0,
                        "asset_path": f"assets/{img_filename}",
                        "width_px": w_px,
                        "height_px": h_px,
                        "hyperlink": img_link
                    })

            # 4. Extract Text Blocks with Exact Typography & Superscript Hierarchy
            text_blocks_data = []
            text_page = page.get_text("dict")

            for block in text_page.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    b_bbox = block.get("bbox")
                    lines = block.get("lines", [])
                    if not lines:
                        continue

                    block_lines_data = []
                    full_text_parts = []
                    dominant_color = "#222222"
                    has_link = None

                    for line in lines:
                        spans = line.get("spans", [])
                        if not spans:
                            continue

                        line_spans_data = []
                        line_text_parts = []

                        for idx, span in enumerate(spans):
                            t = clean_email_text(span.get("text", ""))
                            if not t:
                                continue

                            line_text_parts.append(t)
                            sz = round(span.get("size", 11), 1)
                            color = rgb_int_to_hex(span.get("color", 0))
                            if color and color != "#000000":
                                dominant_color = color

                            flags = span.get("flags", 0)
                            font_lower = span.get("font", "").lower()
                            is_bold = bool(flags & 16 or "bold" in font_lower or sz >= 14)
                            is_italic = bool(flags & 2 or "italic" in font_lower)

                            # Hyperlink check
                            s_bbox = span.get("bbox")
                            s_rect = fitz.Rect(s_bbox) if s_bbox else None
                            span_link = None
                            if s_rect:
                                for lk in pdf_links:
                                    l_rect = lk.get("from")
                                    if l_rect and s_rect.intersects(l_rect):
                                        span_link = lk.get("uri")
                                        has_link = span_link
                                        break

                            is_super = bool(flags & 1 or (len(t.strip()) <= 4 and t.strip() in ["1", "2", "3", "4", "5", "1-4", "2,3", "®", "™", "*"]) or "sup" in font_lower)

                            line_spans_data.append({
                                "text": t,
                                "font_size_pt": sz,
                                "color": color,
                                "bold": is_bold,
                                "italic": is_italic,
                                "superscript": is_super,
                                "hyperlink": span_link
                            })

                        if line_spans_data:
                            full_text_parts.append(" ".join(line_text_parts))
                            block_lines_data.append({
                                "bbox": [round(line["bbox"][0], 1), round(line["bbox"][1], 1), round(line["bbox"][2], 1), round(line["bbox"][3], 1)],
                                "spans": line_spans_data
                            })

                    if block_lines_data:
                        full_raw_text = " ".join(full_text_parts).strip()
                        b_rect = fitz.Rect(b_bbox)

                        # Container Card Containment Check
                        parent_card_color = None
                        for card in bg_cards:
                            if card["rect"].y0 - 5 <= b_rect.y0 and card["rect"].y1 + 5 >= b_rect.y1 and card["rect"].x0 - 5 <= b_rect.x0 and card["rect"].x1 + 5 >= b_rect.x1:
                                parent_card_color = card["fill_color"]
                                break

                        is_button = bool((has_link is not None or "http" in full_raw_text) and len(full_raw_text) <= 35 and b_rect.width <= 320)

                        text_blocks_data.append({
                            "type": "text_block",
                            "bbox": [round(b_bbox[0], 1), round(b_bbox[1], 1), round(b_bbox[2], 1), round(b_bbox[3], 1)],
                            "top": b_bbox[1],
                            "left": b_bbox[0],
                            "raw_text": full_raw_text,
                            "lines": block_lines_data,
                            "parent_container_color": parent_card_color,
                            "is_cta_button": is_button,
                            "cta_button_link": has_link,
                            "dominant_color": dominant_color
                        })

            # Combine and sort all visual elements by reading order (Top to Bottom, Left to Right)
            all_elements = images_data + text_blocks_data
            all_elements.sort(key=lambda e: (e["top"], e["left"]))

            page_dict["elements"] = all_elements
            page_dict["background_cards"] = [{
                "bbox": c["bbox"],
                "fill_color": c["fill_color"],
                "stroke_color": c["stroke_color"]
            } for c in bg_cards]

            package_data["pages"].append(page_dict)

        doc.close()

        # Save JSON File
        json_filename = f"{base_name}_design.json"
        json_path = os.path.join(package_dir, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(package_data, f, indent=2)

        # Generate Ready-to-Paste Gemini Prompt
        prompt_filename = "PROMPT_FOR_GEMINI.txt"
        prompt_path = os.path.join(package_dir, prompt_filename)
        prompt_content = f"""You are an expert Email Template & MJML Developer.
I have uploaded the design screenshot '{page_preview_filename}' and the structured '{json_filename}'.

TASK:
Convert this email design into clean, pixel-perfect, mobile-responsive MJML code.

CRITICAL REQUIREMENTS:
1. Container Specs:
   - Outer width: 700px (<mj-body width="700px" background-color="#eef1f4">)
   - Left & Right Padding: 20px (Inner content area = 660px)
2. Assets:
   - Use the exact asset paths listed in the JSON (e.g. 'assets/asset_p1_1.png', 'assets/asset_p1_2.png', etc.).
3. Styling & Hierarchy:
   - Match all font sizes, bold weights, line heights, and exact hex colors from the JSON.
   - For citations & numbers, keep superscripts inline: <sup>2,3</sup>, <sup>4</sup>.
   - For colored cards (e.g. red #{package_data['pages'][0]['background_cards'][0]['fill_color'] if package_data['pages'][0]['background_cards'] else '9e0b0f'} or grey cards), use <mj-section background-color="..."> with matching border-radius.
   - For side-by-side elements (e.g. header logo + text, or photo + card), use <mj-section> with 2 <mj-column> tags.
   - For rating grids (e.g. 5 satisfaction smilies), use <mj-group> with 5 <mj-column width="20%"> tags.
   - For CTA buttons, use <mj-button> with proper background-color and link.
4. Output ONLY the raw <mjml>...</mjml> code without markdown formatting so it is ready to compile directly into production table HTML.
"""
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_content)

        self.log(f"AI Design Package ready in: {os.path.basename(package_dir)}/")
        self.log(f"  - Structured Data: {json_filename}")
        self.log(f"  - Visual Screenshot: {page_preview_filename}")
        self.log(f"  - Assets Folder: assets/ ({img_counter} images)")
        self.log(f"  - AI Prompt: {prompt_filename}")

        return package_dir, json_path, prompt_path

# Standalone MJML to HTML helper
def compile_mjml_to_html(mjml_code, output_html_path):
    # Auto-clean common AI Markdown formatting quirks (e.g. href="[url](url)")
    mjml_code = re.sub(r'href="\[([^\]]+)\]\([^\)]+\)"', r'href="\1"', mjml_code)
    mjml_code = re.sub(r'href="\[([^\]]+)\]"', r'href="\1"', mjml_code)
    
    # Wrap in <mjml> tags if user only pasted inner body
    if "<mjml>" not in mjml_code:
        mjml_code = f"""<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, Helvetica, sans-serif" />
      <mj-text font-size="14px" line-height="1.4" color="#222222" />
    </mj-attributes>
    <mj-style>
      sup {{ font-size: 70% !important; line-height: 0 !important; vertical-align: super !important; }}
      sub {{ font-size: 70% !important; line-height: 0 !important; vertical-align: sub !important; }}
      img {{ -ms-interpolation-mode: bicubic; }}
      a {{ color: inherit; }}
      .link-text {{ color: #d71920 !important; text-decoration: underline; }}
      .link-plain {{ text-decoration: none; color: #151515 !important; }}
    </mj-style>
  </mj-head>
  <mj-body width="700px" background-color="#eef1f4">
    {mjml_code}
  </mj-body>
</mjml>"""

    mrml_output = mrml.to_html(mjml_code)
    final_html = mrml_output.content if hasattr(mrml_output, "content") else str(mrml_output)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    return output_html_path
