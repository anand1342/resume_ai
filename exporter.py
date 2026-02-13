from docx import Document

def export_to_word(text, filename):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(filename)
