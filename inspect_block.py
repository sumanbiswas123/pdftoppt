import fitz

doc = fitz.open(r"c:\Users\SumanBiswas\Downloads\Pages from PM-MY-SGX-EML-250072.pdf")
page = doc[0]
text_page = page.get_text("dict")
for idx, b in enumerate(text_page["blocks"]):
    if b.get("type") == 0:
        print(f"\n--- Block {idx} bbox={b['bbox']} ---")
        for i, l in enumerate(b["lines"]):
            print(f"Line {i} bbox={l['bbox']}:")
            for s in l["spans"]:
                print("   ", s["bbox"], repr(s["text"]))
