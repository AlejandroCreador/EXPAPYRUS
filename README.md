# Expapyrus: From physical images to digital text.

The proposed Python program aims to extract text from images within scanned PDF files, translate the extracted text into Spanish, and highlight sections where text extraction was unsuccessful. The program utilizes the following libraries and tools:

1. **PyMuPDF**: A library for accessing and manipulating PDF files, enabling the conversion of PDF pages into images.
2. **Tesseract OCR**: An open-source optical character recognition engine that extracts text from images.
3. **Google Translate API**: A service that translates text into various languages, in this case, Spanish.
4. **Pillow**: A Python Imaging Library (PIL) fork that adds image processing capabilities.
5. **ReportLab**: A library for generating PDFs, used here to create a new PDF with the translated text and highlighted unreadable sections.

The program follows these steps:

1. **Convert PDF pages to images**: Using PyMuPDF, each page of the PDF is rendered as an image.
2. **Extract text using OCR**: Tesseract OCR processes each image to extract text content.
3. **Identify unreadable sections**: The program detects areas where text extraction failed or confidence levels are low, marking these regions as unreadable.
4. **Translate text to Spanish**: The extracted text is translated into Spanish using the Google Translate API.
5. **Generate a new PDF**: Utilizing ReportLab, a new PDF is created containing the translated text, with unreadable sections highlighted for review.

This program is particularly useful for digitizing and translating scanned documents, ensuring that any sections requiring further attention are clearly indicated.
