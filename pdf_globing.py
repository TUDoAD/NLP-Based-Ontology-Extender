import glob2

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO


def get_pdf_file_content(pdf_file):
    # extract the text of PDF-files
    # used to store resources in the PDF, for example images
    resource_manager = PDFResourceManager(caching=True)
    out_text = StringIO()

    # object from the PDF miner layout parameters
    la_params = LAParams()
    text_converter = TextConverter(resource_manager, out_text, laparams=la_params)
    fp = open(pdf_file, mode='rb')
    interpreter = PDFPageInterpreter(resource_manager, text_converter)

    # Process the content of each page of the PDF file
    for page in PDFPage.get_pages(fp, pagenos=set(), maxpages=0, password='', caching=True, check_extractable=True):
        interpreter.process_page(page)
    text = out_text.getvalue()

    # close resources
    fp.close()
    text_converter.close()
    out_text.close()
    return text


def get_globed_content():
    # opens all PDF file, hands it to get_pdf_file_content function and converts it into string
    pdf_globed = glob2.glob('./import/*.pdf')
    pdf_text = []
    for i in range(len(pdf_globed)):
        pdf_text.append(get_pdf_file_content(pdf_globed[i]))
    pdf_text_string = ''.join(pdf_text)
    return pdf_text_string
