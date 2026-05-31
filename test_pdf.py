import fitz

pdf_path = "airbuw_manual.pdf"

doc = fitz.open(pdf_path)

print(f"Total Pages: {doc.page_count}")

page = doc[0]
text = page.get_text()

print("\nFIRST PAGE TEXT:\n")
print(text[:1000])

doc.close()