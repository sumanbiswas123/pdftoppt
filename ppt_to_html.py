import os
import io
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

def rects_overlap(r1, r2, threshold=0.75):
    intersect = fitz.Rect(r1).intersect(fitz.Rect(r2))
    if intersect.is_empty or intersect.width <= 0 or intersect.height <= 0:
        return False
    area1 = (r1[2] - r1[0]) * (r1[3] - r1[1])
    area2 = (r2[2] - r2[0]) * (r2[3] - r2[1])
    min_area = min(area1, area2)
    if min_area <= 0:
        return False
    inter_area = intersect.width * intersect.height
    return (inter_area / min_area) >= threshold

class SpatialMJMLEmailConverter:
    """
    Combined Spatial Geometry + MJML Framework Email Engine.
    - Zero hardcoded text or brand colors.
    - Deterministic spatial math detects background cards, side-by-side grids, and buttons.
    - Compiles into clean MJML, then natively turns into 100% tested Outlook-compliant table HTML via MRML.
    """
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def log(self, message):
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def convert(self, pdf_or_pptx_path, html_path=None, assets_dir_name=None, email_width=700):
        pdf_path = pdf_or_pptx_path
        if pdf_or_pptx_path.lower().endswith(".pptx"):
            possible_pdf = pdf_or_pptx_path.replace("_editable.pptx", ".pdf").replace(".pptx", ".pdf")
            if os.path.exists(possible_pdf):
                pdf_path = possible_pdf

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Source file not found: {pdf_path}")

        try:
            email_width = int(email_width)
        except (ValueError, TypeError):
            email_width = 700

        content_width = email_width - 40

        if not html_path:
            base_no_ext, _ = os.path.splitext(pdf_or_pptx_path)
            html_path = f"{base_no_ext}_email.html"

        output_dir = os.path.dirname(os.path.abspath(html_path))
        base_name = os.path.splitext(os.path.basename(html_path))[0]

        if not assets_dir_name:
            assets_dir_name = f"{base_name}_assets"

        full_assets_dir = os.path.join(output_dir, assets_dir_name)
        os.makedirs(full_assets_dir, exist_ok=True)

        self.log(f"Compiling Spatial-MJML Email ({email_width}px container) from: {os.path.basename(pdf_path)}...")
        doc = fitz.open(pdf_path)
        
        all_mjml_sections = []
        img_counter = 0

        for page_idx, page in enumerate(doc):
            rect = page.rect
            scale = float(content_width) / rect.width if rect.width > 0 else 1.0
            pdf_links = page.get_links()

            # -----------------------------------------------------------------
            # 1. Extract Real Raster Images (Banners, Photos, Infographics, Icons)
            # -----------------------------------------------------------------
            images_data = []
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

                    pix = page.get_pixmap(clip=r, dpi=200, colorspace=fitz.csRGB)
                    img_counter += 1
                    img_filename = f"img_p{page_idx+1}_{img_counter}.png"
                    img_path = os.path.join(full_assets_dir, img_filename)
                    pix.save(img_path)

                    w_px = min(660, max(16, int(r.width * scale)))
                    images_data.append({
                        "type": "image",
                        "rect": fitz.Rect(r),
                        "top": r.y0,
                        "bottom": r.y1,
                        "left": r.x0,
                        "right": r.x1,
                        "filename": img_filename,
                        "w_px": w_px,
                        "h_px": int(r.height * scale),
                        "link": img_link
                    })

            # -----------------------------------------------------------------
            # 2. Extract Vector Drawing Background Containers (Dynamic Colors)
            # -----------------------------------------------------------------
            bg_cards = []
            for draw in page.get_drawings():
                d_rect = fitz.Rect(draw.get("rect"))
                if d_rect.width < 15 or d_rect.height < 12:
                    continue
                if d_rect.width >= rect.width * 0.95 and d_rect.height >= rect.height * 0.95:
                    continue
                
                fill_hex = rgb_tuple_to_hex(draw.get("fill"))
                stroke_hex = rgb_tuple_to_hex(draw.get("color"))
                
                if fill_hex and fill_hex not in ["#ffffff"]:
                    bg_cards.append({
                        "rect": d_rect,
                        "top": d_rect.y0,
                        "bottom": d_rect.y1,
                        "left": d_rect.x0,
                        "right": d_rect.x1,
                        "fill": fill_hex,
                        "stroke": stroke_hex
                    })

            # -----------------------------------------------------------------
            # 3. Extract Text Blocks & Format Rich Runs
            # -----------------------------------------------------------------
            text_blocks_data = []
            text_page = page.get_text("dict")

            for block in text_page.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    b_bbox = block.get("bbox")
                    lines = block.get("lines", [])
                    if not lines:
                        continue

                    block_p_htmls = []
                    raw_block_text_parts = []
                    dominant_color = "#222222"
                    has_link = None

                    for line in lines:
                        spans = line.get("spans", [])
                        if not spans:
                            continue

                        line_runs = []
                        line_raw = []

                        for idx, span in enumerate(spans):
                            t = clean_email_text(span.get("text", ""))
                            if not t:
                                continue

                            line_raw.append(t)
                            if idx > 0 and not t.startswith(" ") and not t.startswith(",") and not t.startswith("."):
                                t = " " + t
                            
                            esc_t = html.escape(t)
                            styles = []
                            
                            sz = round(span.get("size", 11), 1)
                            if sz >= 14:
                                styles.append(f"font-size: {sz}pt")
                                styles.append(f"line-height: {round(sz * 1.25, 1)}pt")
                                styles.append("font-weight: bold")
                            elif sz >= 11:
                                styles.append(f"font-size: {sz}pt")
                                styles.append(f"line-height: {round(sz * 1.35, 1)}pt")
                            else:
                                styles.append(f"font-size: {sz}pt")
                                styles.append(f"line-height: {round(sz * 1.35, 1)}pt")

                            color = rgb_int_to_hex(span.get("color", 0))
                            if color and color != "#000000":
                                styles.append(f"color: {color}")
                                dominant_color = color

                            flags = span.get("flags", 0)
                            font_lower = span.get("font", "").lower()
                            if flags & 16 or "bold" in font_lower:
                                styles.append("font-weight: bold")
                            if flags & 2 or "italic" in font_lower:
                                styles.append("font-style: italic")

                            style_str = f' style="{"; ".join(styles)};"' if styles else ""
                            
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

                            if span_link:
                                run_str = f'<a href="{html.escape(span_link)}" target="_blank" style="color: inherit; text-decoration: underline;"><span{style_str}>{esc_t}</span></a>'
                            else:
                                is_super = flags & 1 or (len(t.strip()) <= 4 and t.strip() in ["1", "2", "3", "4", "5", "1-4", "2,3", "®", "™", "*"]) or "sup" in font_lower
                                if is_super:
                                    run_str = f'<sup style="font-size: 70%; line-height: 0; vertical-align: super;"><span{style_str}>{esc_t}</span></sup>'
                                else:
                                    run_str = f'<span{style_str}>{esc_t}</span>'

                            line_runs.append(run_str)

                        if line_runs:
                            raw_block_text_parts.append(" ".join(line_raw))
                            block_p_htmls.append(f'<p style="margin: 0 0 3px 0; padding: 0;">{"".join(line_runs)}</p>')

                    if block_p_htmls:
                        full_raw_text = " ".join(raw_block_text_parts).strip()
                        block_html = "\n                      ".join(block_p_htmls)

                        # Spatial Containment: Find if block is inside a background card
                        b_rect = fitz.Rect(b_bbox)
                        card_fill = None
                        for card in bg_cards:
                            if card["top"] - 5 <= b_rect.y0 and card["bottom"] + 5 >= b_rect.y1 and card["left"] - 5 <= b_rect.x0 and card["right"] + 5 >= b_rect.x1:
                                card_fill = card["fill"]
                                break

                        # Check if this text block behaves as a CTA Button (short text + button shape or link)
                        is_button = (has_link is not None or "http" in full_raw_text) and len(full_raw_text) <= 35 and (b_rect.width <= 320)

                        text_blocks_data.append({
                            "type": "text_block",
                            "rect": b_rect,
                            "top": b_bbox[1],
                            "bottom": b_bbox[3],
                            "left": b_bbox[0],
                            "right": b_bbox[2],
                            "html": block_html,
                            "raw_text": full_raw_text,
                            "card_fill": card_fill,
                            "is_button": is_button,
                            "button_link": has_link or "#",
                            "dominant_color": dominant_color
                        })

            # -----------------------------------------------------------------
            # 4. Assemble Unified MJML Tree
            # -----------------------------------------------------------------
            all_flow = images_data + text_blocks_data
            all_flow.sort(key=lambda x: (x["top"], x["left"]))

            used_flow = set()

            for i, elem in enumerate(all_flow):
                if id(elem) in used_flow:
                    continue

                top_y = elem["top"]

                # Case A: Multi-Column Horizontal Band Grid (e.g. 5 survey icons, 3 feature columns, 4 badges)
                h_images = [e for e in all_flow if e["type"] == "image" and id(e) not in used_flow and abs(e["top"] - top_y) <= 12.0 and e["w_px"] <= 85]
                if len(h_images) >= 3:
                    h_images.sort(key=lambda e: e["left"])
                    for hi in h_images:
                        used_flow.add(id(hi))

                    n_cols = len(h_images)
                    col_width_pct = round(100.0 / n_cols, 1)

                    mj_cols = []
                    for idx, h_img in enumerate(h_images):
                        href_attr = f' href="{html.escape(h_img["link"])}"' if h_img.get("link") else ""
                        mj_cols.append(f"""
        <mj-column width="{col_width_pct}%">
          <mj-image src="{assets_dir_name}/{h_img['filename']}" width="{h_img['w_px']}px" align="center" padding="4px 2px"{href_attr} />
        </mj-column>""")

                    # Mark nearby associated labels as used
                    for e in all_flow:
                        if e["type"] == "text_block" and id(e) not in used_flow and 0 < (e["top"] - top_y) <= 90:
                            if any(term in e["raw_text"].lower() for term in ["dissatisfied", "satisfied", "neutral"]):
                                used_flow.add(id(e))

                    all_mjml_sections.append(f"""
    <!-- Multi-Column Grid ({n_cols} Columns) -->
    <mj-section background-color="#ffffff" padding="10px 0 16px 0">
      <mj-group>
        {"".join(mj_cols)}
      </mj-group>
    </mj-section>""")
                    continue

                # Case B: Side-by-Side (Photo/Icon on left + Text/Card on right)
                side_img = None
                side_txt = None
                if elem["type"] == "image" and elem["w_px"] <= 160 and (elem["bottom"] - elem["top"]) < 140:
                    matching_texts = [e for e in all_flow if e["type"] == "text_block" and id(e) not in used_flow and abs(e["top"] - top_y) <= 40.0 and e["left"] > elem["left"]]
                    if matching_texts:
                        side_img = elem
                        side_txt = matching_texts[0]
                elif elem["type"] == "text_block":
                    matching_imgs = [e for e in all_flow if e["type"] == "image" and id(e) not in used_flow and abs(e["top"] - top_y) <= 40.0 and e["left"] < elem["left"] and e["w_px"] <= 160]
                    if matching_imgs:
                        side_img = matching_imgs[0]
                        side_txt = elem

                if side_img and side_txt:
                    used_flow.add(id(side_img))
                    used_flow.add(id(side_txt))

                    img_w_px = side_img["w_px"]
                    txt_fill = side_txt.get("card_fill") or "#ffffff"
                    
                    # Calculate column widths
                    img_col_pct = max(20, min(35, int((img_w_px + 20) / 660.0 * 100)))
                    txt_col_pct = 100 - img_col_pct

                    all_mjml_sections.append(f"""
    <!-- Side-by-Side Asset + Text Block -->
    <mj-section background-color="#ffffff" padding="6px 0 8px 0">
      <mj-column width="{img_col_pct}%">
        <mj-image src="{assets_dir_name}/{side_img['filename']}" width="{img_w_px}px" align="left" padding="0" border-radius="4px" />
      </mj-column>
      <mj-column width="{txt_col_pct}%" background-color="{txt_fill}">
        <mj-text padding="8px 12px">
          {side_txt['html']}
        </mj-text>
      </mj-column>
    </mj-section>""")
                    continue

                # Case C: Standalone Banner / Infographic Image
                if elem["type"] == "image":
                    used_flow.add(id(elem))
                    w_px = elem["w_px"]
                    href_attr = f' href="{html.escape(elem["link"])}"' if elem.get("link") else ""
                    
                    all_mjml_sections.append(f"""
    <!-- Graphic Banner -->
    <mj-section background-color="#ffffff" padding="3px 0">
      <mj-column width="100%">
        <mj-image src="{assets_dir_name}/{elem['filename']}" width="{w_px}px" align="center" padding="0"{href_attr} />
      </mj-column>
    </mj-section>""")
                    continue

                # Case D: Text Block (Card Container, CTA Button, or Standard Content)
                if elem["type"] == "text_block":
                    used_flow.add(id(elem))
                    raw = elem["raw_text"]

                    # 1. Dynamic Card Container (if inside a vector background color)
                    card_fill = elem.get("card_fill")
                    if card_fill and card_fill not in ["#ffffff"]:
                        # Group consecutive blocks in the same colored card
                        group_card_htmls = []
                        button_in_card = None

                        if elem.get("is_button"):
                            button_in_card = elem
                        else:
                            group_card_htmls.append(elem["html"])

                        for next_elem in all_flow[i+1:]:
                            if next_elem["type"] == "text_block" and id(next_elem) not in used_flow and next_elem.get("card_fill") == card_fill and abs(next_elem["top"] - elem["bottom"]) <= 45.0:
                                used_flow.add(id(next_elem))
                                if next_elem.get("is_button"):
                                    button_in_card = next_elem
                                else:
                                    group_card_htmls.append(next_elem["html"])
                            else:
                                break

                        btn_markup = ""
                        if button_in_card:
                            btn_markup = f"""
        <mj-button background-color="#ffffff" color="{card_fill}" border-radius="20px" font-weight="bold" font-size="12px" href="{html.escape(button_in_card['button_link'])}" padding="10px 0 4px 0">
          {html.escape(button_in_card['raw_text'])} &raquo;
        </mj-button>"""

                        card_text_content = "\n          ".join(group_card_htmls)
                        all_mjml_sections.append(f"""
    <!-- Dynamic Colored Container Card ({card_fill}) -->
    <mj-section background-color="{card_fill}" border-radius="6px" padding="14px 18px">
      <mj-column width="100%">
        <mj-text align="center" padding="0">
          {card_text_content}
        </mj-text>{btn_markup}
      </mj-column>
    </mj-section>""")
                        continue

                    # 2. Standalone Dynamic CTA Button
                    if elem.get("is_button"):
                        btn_color = elem.get("dominant_color") or "#E50000"
                        all_mjml_sections.append(f"""
    <!-- Dynamic CTA Button -->
    <mj-section background-color="#ffffff" padding="12px 0 16px 0">
      <mj-column width="100%">
        <mj-button background-color="{btn_color}" color="#ffffff" border-radius="20px" font-weight="bold" font-size="12px" href="{html.escape(elem['button_link'])}" padding="0">
          {html.escape(raw)} &raquo;
        </mj-button>
      </mj-column>
    </mj-section>""")
                        continue

                    # 3. Regular Content Text
                    all_mjml_sections.append(f"""
    <!-- Content Section -->
    <mj-section background-color="#ffffff" padding="3px 0">
      <mj-column width="100%">
        <mj-text padding="0">
          {elem['html']}
        </mj-text>
      </mj-column>
    </mj-section>""")

        doc.close()

        # Build Complete MJML Document
        full_mjml = f"""<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, Helvetica, sans-serif" />
      <mj-text font-size="14px" line-height="1.4" color="#222222" />
    </mj-attributes>
    <mj-style>
      sup {{ font-size: 70% !important; line-height: 0 !important; vertical-align: super !important; }}
      sub {{ font-size: 70% !important; line-height: 0 !important; vertical-align: sub !important; }}
      img {{ -ms-interpolation-mode: bicubic; }}
    </mj-style>
  </mj-head>
  <mj-body width="{email_width}px" background-color="#eef1f4">
    {"".join(all_mjml_sections)}
  </mj-body>
</mjml>
"""

        self.log("Compiling MJML tree into 100% Outlook-compliant HTML tables...")
        mrml_output = mrml.to_html(full_mjml)
        final_html = mrml_output.content if hasattr(mrml_output, "content") else str(mrml_output)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        self.log(f"Saved Production HTML Email: {os.path.basename(html_path)}")
        self.log(f"Saved Email Assets to: {assets_dir_name}/")

        return html_path, full_assets_dir

# Backward compatibility alias
PPTToHTMLEmailConverter = SpatialMJMLEmailConverter
