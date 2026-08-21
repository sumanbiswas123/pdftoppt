import fitz

doc = fitz.open(r"c:\Users\SumanBiswas\Downloads\Pages from PM-MY-SGX-EML-250072.pdf")
page = doc[0]
print(f"Page rect: {page.rect}")
print(f"Images count: {len(page.get_images())}")
for img in page.get_images():
    rects = page.get_image_rects(img[0])
    print(f"  Img xref={img[0]}, rects={rects}")

print(f"\nText blocks count: {len(page.get_text('blocks'))}")
for b in page.get_text('blocks'):
    print(f"  Block bbox={b[:4]}, text={repr(b[4][:50])}")
