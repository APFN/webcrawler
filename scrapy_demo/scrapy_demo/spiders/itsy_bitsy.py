#Turorial source: https://www.imagescape.com/blog/2018/08/20/scraping-pdf-doc-and-docx-scrapy/
import re
import textract
from itertools import chain
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from tempfile import NamedTemporaryFile

control_chars = ''.join(map(chr, chain(range(0, 9), range(11, 32), range(127, 160))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(control_chars))
TEXTRACT_EXTENSIONS = [".pdf"] 

class CustomLinkExtractor(LinkExtractor):
    def __init__(self, *args, **kwargs):
        super(CustomLinkExtractor, self).__init__(*args, **kwargs)
        # Keep the default values in "deny_extensions" *except* for those types we want.
        #self.restrict_xpaths= ['//*[@id="Form1"]/section[2]/div/div[2]/div[3]/center[2]/center[1]/h1/p/strong/a']
        self.restrict_xpaths= ['//*[@id="Form1"]']
        self.deny_extensions = [ext for ext in self.deny_extensions if ext not in TEXTRACT_EXTENSIONS]


class ItsyBitsySpider(CrawlSpider):
    name = "itsy_bitsy"
    start_urls = [
        'http://diariooficial.rn.gov.br/dei/dorn3/'
    ]

    def __init__(self, *args, **kwargs):
       # Selector(response=response).xpath('//*[@id="Form1"]/section[2]/div/div[2]/div[3]/center[2]/center[1]/h1/p/strong/a').get()
        self.rules = (Rule(CustomLinkExtractor(), follow=True, callback="parse_item"),)
        super(ItsyBitsySpider, self).__init__(*args, **kwargs)

        

    def parse_item(self, response):
        print(">>>>>>>>>>>>>>>Entrou no parse")
        if hasattr(response, "text"):
            print("Entrou no texto")
            # The response is text - we assume html. Normally we'd do something                                                                                                                    
            # with this, but this demo is just about binary content, so...                                                                                                                         
            pass
        else:
            print("Entrou no binario")
            # We assume the response is binary data                                                                                                                                                
            # One-liner for testing if "response.url" ends with any of TEXTRACT_EXTENSIONS                                                                                                         
            extension = list(filter(lambda x: response.url.lower().endswith(x), TEXTRACT_EXTENSIONS))[0]
            if extension:
                print("Entoru no if do binario")
                # This is a pdf or something else that Textract can process                                                                                                                        
                # Create a temporary file with the correct extension.                                                                                                     
                tempfile = NamedTemporaryFile(suffix=extension)
                tempfile.write(response.body)
                tempfile.flush()
                extracted_data = textract.process(tempfile.name)
                extracted_data = extracted_data.decode('utf-8')
                extracted_data = CONTROL_CHAR_RE.sub('', extracted_data)
                tempfile.close()         
                patterns = ['Raimundo', 'Executivo']  
                term = "Raimundo"

                for line in extracted_data:
                    line = line.strip().split(',')  # <--- 
                    if term == line:             # <--- You can also stay with "if term in line:" if you doesn't care which field the "model" is. 
                        print(">>>>>>>>>>>>>Achou>>>>>>>>>>>>")

                # if re.search(patterns, extracted_data):
                #     print(">>>>>>>>>>>>>Achou>>>>>>>>>>>>")
                
                with open("scraped_content.txt", "a") as f:
                    f.write(response.url.upper())
                    f.write("\n")                    
                    f.write(extracted_data)
                    f.write("\n\n")