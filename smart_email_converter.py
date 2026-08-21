import os
import io
import html
import re
import fitz  # PyMuPDF

def rgb_to_hex(color_int):
    if isinstance(color_int, int):
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#222222"

def clean_email_text(text):
    if not text:
        return ""
    # Fix common encoding artifacts in PDF
    text = text.replace('\xa0', ' ')
    text = text.replace('', '©')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

class SmartPDFToHTMLEmailConverter:
    """
    Direct High-Fidelity & GSK-Pharma Compliant HTML Email Generator.
    - 700px outer container, 20px left/right padding, 660px inner content.
    - Eliminates duplicate vector slices and spacious clutter.
    - Groups inline icons with text (2-column side-by-side).
    - Groups rating smilies into a responsive 5-column table.
    - Formats CTA buttons into bulletproof email buttons.
    - Preserves <sup> and <sub> tags with line-height resets.
    - Formats legal/safety disclaimers cleanly in compact footer tables.
    """
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def log(self, message):
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def convert(self, pdf_path, html_path=None, assets_dir_name=None):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not html_path:
            base_no_ext, _ = os.path.splitext(pdf_path)
            html_path = f"{base_no_ext}_email.html"

        output_dir = os.path.dirname(os.path.abspath(html_path))
        base_name = os.path.splitext(os.path.basename(html_path))[0]

        if not assets_dir_name:
            assets_dir_name = f"{base_name}_assets"

        full_assets_dir = os.path.join(output_dir, assets_dir_name)
        os.makedirs(full_assets_dir, exist_ok=True)

        self.log(f"Analyzing PDF layout for Email Template: {os.path.basename(pdf_path)}...")
        doc = fitz.open(pdf_path)
        
        all_sections_html = []
        img_counter = 0

        for page_idx, page in enumerate(doc):
            rect = page.rect
            scale = 660.0 / rect.width if rect.width > 0 else 1.0

            # 1. Extract Real Raster Images (Filter out 1px lines or background covers)
            images_data = []
            for img in page.get_images():
                xref = img[0]
                img_rects = page.get_image_rects(xref)
                for r in img_rects:
                    # Ignore tiny 1px separator lines or page-size backgrounds
                    if r.height <= 2.0 or r.width <= 2.0:
                        continue
                    if r.width >= rect.width * 0.98 and r.height >= rect.height * 0.98:
                        continue

                    pix = page.get_pixmap(clip=r, dpi=200, colorspace=fitz.csRGB)
                    img_counter += 1
                    img_filename = f"img_p{page_idx+1}_{img_counter}.png"
                    img_path = os.path.join(full_assets_dir, img_filename)
                    pix.save(img_path)

                    images_data.append({
                        "type": "image",
                        "rect": r,
                        "top": r.y0,
                        "left": r.x0,
                        "width": r.width,
                        "height": r.height,
                        "filename": img_filename,
                        "w_px": min(660, max(16, int(r.width * scale))),
                        "h_px": int(r.height * scale)
                    })

            # 2. Extract Text Blocks & Spans
            text_blocks = []
            text_page = page.get_text("dict")
            links = page.get_links()

            for block in text_page.get("blocks", []):
                if block.get("type") == 0:  # Text
                    b_rect = fitz.Rect(block.get("bbox"))
                    b_text = "".join(s.get("text", "") for l in block.get("lines", []) for s in l.get("spans", []))
                    if not b_text.strip():
                        continue

                    # Group spans by lines
                    lines_data = []
                    for line in block.get("lines", []):
                        spans_data = []
                        for span in line.get("spans", []):
                            stext = clean_email_text(span.get("text", ""))
                            if not stext:
                                continue
                            spans_data.append({
                                "text": stext,
                                "size": span.get("size", 11),
                                "font": span.get("font", "Arial"),
                                "color": rgb_to_hex(span.get("color", 0)),
                                "flags": span.get("flags", 0),
                                "bbox": span.get("bbox")
                            })
                        if spans_data:
                            lines_data.append(spans_data)

                    if lines_data:
                        text_blocks.append({
                            "type": "text",
                            "rect": b_rect,
                            "top": b_rect.y0,
                            "left": b_rect.x0,
                            "width": b_rect.width,
                            "height": b_rect.height,
                            "lines": lines_data,
                            "raw_text": b_text.strip()
                        })

            # 3. Detect and Cluster Layout Elements (Side-by-side, 5-col ratings, banners, headers)
            # Combine all visual elements and sort by Y coordinate
            all_elements = images_data + text_blocks
            all_elements.sort(key=lambda x: (x["top"], x["left"]))

            # Process elements with smart clustering
            used_elements = set()
            page_rows = []

            for i, elem in enumerate(all_elements):
                if id(elem) in used_elements:
                    continue

                top_y = elem["top"]

                # Case A: Check for Horizontal Rating / Survey Row (e.g. 5 smiley icons with labels)
                # Find all images at nearly the same Y
                h_images = [e for e in all_elements if e["type"] == "image" and id(e) not in used_elements and abs(e["top"] - top_y) <= 10.0 and e["w_px"] <= 70]
                if len(h_images) >= 4:
                    # Found rating smilies! Sort left to right
                    h_images.sort(key=lambda e: e["left"])
                    for hi in h_images:
                        used_elements.add(id(hi))

                    # Find matching label text block just below them
                    h_labels = [e for e in all_elements if e["type"] == "text" and id(e) not in used_elements and 0 < (e["top"] - top_y) <= 80]
                    
                    rating_cols = []
                    rating_labels_text = ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]
                    
                    for idx, h_img in enumerate(h_images):
                        lbl = rating_labels_text[idx] if idx < len(rating_labels_text) else ""
                        col_html = f"""
                        <td align="center" valign="top" width="20%" style="width: 20%; padding: 4px 2px;">
                          <a href="#" target="_blank" style="text-decoration: none;">
                            <img src="{assets_dir_name}/{h_img['filename']}" width="{h_img['w_px']}" alt="{lbl}" border="0" style="display: block; width: {h_img['w_px']}px; height: auto; margin: 0 auto 6px auto; border: 0;" />
                            <span style="font-family: Arial, Helvetica, sans-serif; font-size: 8.5pt; color: #444444; line-height: 1.1; display: block;">{lbl}</span>
                          </a>
                        </td>"""
                        rating_cols.append(col_html)

                    # Mark nearby label block as used if present
                    for hl in h_labels:
                        if any(term in hl["raw_text"] for term in ["dissatisfied", "Satisfied", "Neutral"]):
                            used_elements.add(id(hl))

                    rating_table = f"""
                <!-- Survey / Rating 5-Column Grid -->
                <tr>
                  <td align="center" valign="top" style="padding: 12px 0 16px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width: 100%;">
                      <tr>
                        {"".join(rating_cols)}
                      </tr>
                    </table>
                  </td>
                </tr>"""
                    page_rows.append(rating_table)
                    continue

                # Case B: Side-by-Side (Inline Icon + Text, or Logo + Header Text)
                # Check if there is an image on the left and text on the right at roughly the same Y
                side_img = None
                side_txt = None
                if elem["type"] == "image" and elem["w_px"] <= 120 and elem["height"] < 60:
                    matching_texts = [e for e in all_elements if e["type"] == "text" and id(e) not in used_elements and abs(e["top"] - top_y) <= 25.0 and e["left"] > elem["left"]]
                    if matching_texts:
                        side_img = elem
                        side_txt = matching_texts[0]
                elif elem["type"] == "text":
                    matching_imgs = [e for e in all_elements if e["type"] == "image" and id(e) not in used_elements and abs(e["top"] - top_y) <= 25.0 and e["left"] < elem["left"] and e["w_px"] <= 120]
                    if matching_imgs:
                        side_img = matching_imgs[0]
                        side_txt = elem

                if side_img and side_txt:
                    used_elements.add(id(side_img))
                    used_elements.add(id(side_txt))

                    img_w = side_img["w_px"]
                    txt_html = self._format_text_block(side_txt)

                    side_by_side_html = f"""
                <!-- Side-by-Side (Icon/Logo + Text) -->
                <tr>
                  <td align="left" valign="top" style="padding: 6px 0 8px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width: 100%;">
                      <tr>
                        <td align="left" valign="middle" width="{img_w + 10}" style="width: {img_w + 10}px; padding-right: 10px;">
                          <img src="{assets_dir_name}/{side_img['filename']}" width="{img_w}" alt="" border="0" style="display: block; width: {img_w}px; height: auto; border: 0;" />
                        </td>
                        <td align="left" valign="middle" style="font-family: Arial, Helvetica, sans-serif;">
                          {txt_html}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>"""
                    page_rows.append(side_by_side_html)
                    continue

                # Case C: Standalone Banner Image
                if elem["type"] == "image":
                    used_elements.add(id(elem))
                    w_px = elem["w_px"]
                    
                    # Check if it's a full-width hero banner (e.g. > 500px)
                    is_full_width = w_px >= 540
                    pad_v = "0" if is_full_width else "8px"

                    img_block = f"""
                <!-- Banner Image -->
                <tr>
                  <td align="center" valign="top" style="padding: {pad_v} 0; font-size: 0px; line-height: 0px;">
                    <img src="{assets_dir_name}/{elem['filename']}" width="{w_px}" alt="" border="0" style="display: block; width: 100%; max-width: {w_px}px; height: auto; outline: none; border: 0;" />
                  </td>
                </tr>"""
                    page_rows.append(img_block)
                    continue

                # Case D: Text Block (Check if CTA Button, Heading, Body, or Legal Footer)
                if elem["type"] == "text":
                    used_elements.add(id(elem))
                    raw = elem["raw_text"].strip()

                    # CTA Button detection (e.g., "Get full access here", "Click here")
                    if ("Get full access" in raw or "Click here" in raw or "Register now" in raw) and len(raw) < 35:
                        btn_html = f"""
                <!-- Bulletproof CTA Button -->
                <tr>
                  <td align="center" valign="top" style="padding: 14px 0 16px 0;">
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 0 auto;">
                      <tr>
                        <td align="center" bgcolor="#E50000" style="background-color: #E50000; border-radius: 4px; padding: 10px 24px;">
                          <a href="#" target="_blank" style="font-family: Arial, Helvetica, sans-serif; font-size: 11pt; font-weight: bold; color: #ffffff; text-decoration: none; display: inline-block;">{html.escape(raw)} &raquo;</a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>"""
                        page_rows.append(btn_html)
                        continue

                    # Footer / References / Legal disclaimers (e.g. References, Adverse events, Disclaimer)
                    is_legal_footer = any(kw in raw for kw in ["References:", "Adverse events", "Trade marks", "Before prescribing", "About this email", "About your privacy", "GlaxoSmithKline", "PM-MY-"])
                    
                    txt_html = self._format_text_block(elem, is_legal=is_legal_footer)
                    
                    pad_val = "2px 0" if is_legal_footer else "6px 0"
                    
                    row_html = f"""
                <!-- Content Text Block -->
                <tr>
                  <td align="left" valign="top" style="padding: {pad_val};">
                    {txt_html}
                  </td>
                </tr>"""
                    page_rows.append(row_html)

            all_sections_html.append("\n".join(page_rows))

        doc.close()

        body_content = "\n".join(all_sections_html)

        # Assemble Full HTML Email Template
        full_email_html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="x-apple-disable-message-reformatting" />
  <meta name="format-detection" content="telephone=no, date=no, address=no, email=no" />
  <title>GSK Approved Email Template</title>
  <!--[if mso]>
  <noscript>
    <xml>
      <o:OfficeDocumentSettings>
        <o:AllowPNG/>
        <o:PixelsPerInch>96</o:PixelsPerInch>
      </o:OfficeDocumentSettings>
    </xml>
  </noscript>
  <![endif]-->
  <style type="text/css">
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
    table {{ border-collapse: collapse !important; }}
    body {{ height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #eef1f4; }}
    a[x-apple-data-detectors] {{ color: inherit !important; text-decoration: none !important; font-size: inherit !important; font-family: inherit !important; font-weight: inherit !important; line-height: inherit !important; }}
    sup {{ font-size: 70% !important; line-height: 0 !important; vertical-align: super !important; }}
    sub {{ font-size: 70% !important; line-height: 0 !important; vertical-align: sub !important; }}
    @media screen and (max-width: 720px) {{
      .email-container {{ width: 100% !important; max-width: 100% !important; }}
      .content-cell {{ padding-left: 15px !important; padding-right: 15px !important; }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 0; width: 100% !important; background-color: #eef1f4; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">
  
  <!-- Outer Centering Table -->
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#eef1f4" style="background-color: #eef1f4; width: 100%;">
    <tr>
      <td align="center" valign="top" style="padding: 25px 0;">
        
        <!--[if (gte mso 9)|(IE)]>
        <table role="presentation" width="700" align="center" cellpadding="0" cellspacing="0" border="0" style="width: 700px;">
        <tr>
        <td valign="top">
        <![endif]-->

        <!-- 700px Container Table -->
        <table role="presentation" class="email-container" width="700" cellpadding="0" cellspacing="0" border="0" align="center" style="width: 100%; max-width: 700px; margin: 0 auto; background-color: #ffffff; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
          <tr>
            <!-- 20px Left and Right Padding (Inner Area = 660px) -->
            <td class="content-cell" align="left" valign="top" style="padding: 24px 20px 24px 20px; background-color: #ffffff;">
              
              <!-- 660px Main Content Flow Table -->
              <table role="presentation" width="660" cellpadding="0" cellspacing="0" border="0" style="width: 100%; max-width: 660px; border-collapse: collapse;">
{body_content}
              </table>
              <!-- End 660px Main Content Flow Table -->

            </td>
          </tr>
        </table>
        <!-- End 700px Container Table -->

        <!--[if (gte mso 9)|(IE)]>
        </td>
        </tr>
        </table>
        <![endif]-->

      </td>
    </tr>
  </table>
</body>
</html>
"""

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_email_html)

        self.log(f"Saved Smart HTML Email Template: {os.path.basename(html_path)}")
        self.log(f"Extracted clean assets to: {assets_dir_name}/")

        return html_path, full_assets_dir

    def _format_text_block(self, elem, is_legal=False):
        lines_html = []
        for line in elem["lines"]:
            spans_html = []
            for span in line:
                text = html.escape(span["text"])
                if not text:
                    continue

                styles = []
                styles.append("font-family: Arial, Helvetica, sans-serif")
                
                # Font size
                if is_legal:
                    styles.append("font-size: 8pt")
                    styles.append("line-height: 11pt")
                    styles.append("color: #666666")
                else:
                    sz = round(span["size"], 1)
                    if sz > 14:
                        styles.append(f"font-size: {min(22, round(sz * 1.05, 1))}pt")
                        styles.append(f"line-height: {min(26, round(sz * 1.25, 1))}pt")
                        styles.append("font-weight: bold")
                    elif sz > 11:
                        styles.append(f"font-size: {sz}pt")
                        styles.append(f"line-height: {round(sz * 1.3, 1)}pt")
                        styles.append("font-weight: bold")
                    else:
                        styles.append("font-size: 10pt")
                        styles.append("line-height: 14pt")
                    
                    color = span.get("color")
                    if color and color != "#000000":
                        styles.append(f"color: {color}")
                    else:
                        styles.append("color: #222222")

                flags = span.get("flags", 0)
                font_lower = span.get("font", "").lower()
                if flags & 16 or "bold" in font_lower:
                    styles.append("font-weight: bold")
                if flags & 2 or "italic" in font_lower:
                    styles.append("font-style: italic")

                style_str = f' style="{"; ".join(styles)};"' if styles else ""
                
                # Check for superscript citations (e.g. 1-4, ®, TM)
                if getattr(span, 'is_super', False) or (len(text) <= 4 and text in ["1", "2", "3", "4", "5", "1-4", "®", "™", "*"]):
                    if text in ["®", "™"] or (len(text) <= 3 and text.isdigit()):
                        span_out = f'<sup style="font-size: 70%; line-height: 0; vertical-align: super;"><span{style_str}>{text}</span></sup>'
                    else:
                        span_out = f'<span{style_str}>{text}</span>'
                else:
                    span_out = f'<span{style_str}>{text}</span>'

                spans_html.append(span_out)

            if spans_html:
                m_bottom = "3px" if is_legal else "5px"
                lines_html.append(f'<p style="margin: 0 0 {m_bottom} 0; padding: 0;">{" ".join(spans_html)}</p>')

        return "\n                    ".join(lines_html)
