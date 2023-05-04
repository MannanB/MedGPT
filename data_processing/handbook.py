import fitz
from .dataparser import DataParser
# Handbook of Signs & Symptoms

HANDBOOK_PATH = "././raw_data/HandbookofSignsAndSymptoms.pdf"
HANDBOOK_JSON_PATH = "././processed_data/handbookofsignsandsymptoms.json"

class HandbookDataParser(DataParser):
    def __init__(self):
        super().__init__(HANDBOOK_JSON_PATH)
        self.header2page = {} # for credits
    
    def load_data(self):
        self.data = []
        self.header2page = {}

        headers = []
        connected = False
        displaying_graphic = False

        last_font = ''
        last_bbox = 0
        last_header = None

        page_n = 0

        current_result = {}

        pdf = fitz.open(HANDBOOK_PATH) 
        for page in pdf[11:717]:
            dict = page.get_text("dict")
            blocks = dict["blocks"]
            for block in blocks:
                if "lines" in block.keys():
                    spans = block['lines']
                    for span in spans:
                        data = span['spans']
                        for lines in data:
                            if GraphicFont.match(lines['font']):
                                displaying_graphic = True
                            if displaying_graphic and not RegularFont.match(lines['font']) and round(lines['size']) != 10:
                                continue
                            else:
                                displaying_graphic = False

                            connected = PDFFont.get_cls(last_font).match(lines['font'])
                            indent = (last_bbox !=0 and last_bbox[0]+2 < lines['bbox'][0] and last_bbox[1]+1 < lines['bbox'][1] and RegularFont.match(lines['font']))
                            
                            if lines['font'] == "Minion-SwashDisplayItalic" and lines['size'] < 40:
                                # Big fancy letter.
                                if current_result:
                                    current_result_with_page = {}
                                    for key, value in current_result.items():
                                        current_result_with_page[key] = {'paragraphs': value, 'page': self.header2page[key]}
                                    self.data.append(current_result_with_page)
                                    current_result = {}

                            if HeaderFont.match(lines['font']) and lines['size'] < 40:
                                if not connected:
                                    last_header = lines['text'].lower()
                                    headers.append(last_header)
                                else:
                                    if len(last_header) > 1: last_header += ' '
                                    last_header += lines['text'].lower()
                                    last_header = last_header.replace('.', '').strip()
                                    headers[-1] = last_header

                            elif RegularFont.match(lines['font']):
                                if last_header not in list(current_result.keys()):
                                    current_result[last_header] = []
                                if not connected or len(current_result[last_header]) == 0 or indent:
                                    self.header2page[last_header] = page_n
                                    current_result[last_header].append(lines['text'])
                                elif connected:
                                    if len(current_result[last_header][-1]) < 1 or current_result[last_header][-1][-1] != '-':
                                        current_result[last_header][-1] += ' '
                                    else:
                                        current_result[last_header][-1] = current_result[last_header][-1][:-1]
                                    current_result[last_header][-1] += lines['text']

                            last_font = lines['font']
                            last_bbox = lines['bbox']
            page_n += 1
        pdf.close()

class PDFFont:
    FONTS = []
    @classmethod
    def match(cls, font):
        return font in cls.FONTS
    @classmethod
    def get_cls(cls, text):
        for font in cls.__subclasses__():
            if text in font.FONTS:
                return font
        return PDFFont
        
class HeaderFont(PDFFont): FONTS = ["Minion-SwashDisplayItalic", "AGaramond-SemiboldItalic", "AGaramond-Bold", "AGaramond-BoldItalic"]
class RegularFont(PDFFont): FONTS = ["AGaramond-Regular", "AGaramond-Italic"]
class GraphicFont(PDFFont): FONTS = ["Futura-CondensedBold"]


