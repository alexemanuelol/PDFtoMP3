#!/usr/bin/env python3

"""  """


__author__ = "alexemanuelol"
__dependencies__ = ["pdfminer", "gtts"]

import os
import getopt
import sys

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from gtts import gTTS

class PDFtoMP3():
    """  """

    def __init__(self, path = None):
        """ Init. """
        if path != None:
            self.__is_file_valid(path)
            self.fName = os.path.basename(path).replace(".pdf", "")
        self.path = path
        self.text = ""

        # Input options
        self.password = b''
        self.pagenos = set()
        self.maxpages = 0

        # Output options
        self.rotation = 0
        self.pageno = 1
        self.caching = True
        self.showpageno = True
        self.laparams = LAParams()

        self.create_handlers()


    def create_handlers(self):
        """ Create the pdfminer handlers. """
        self.resourceManager = PDFResourceManager(caching=self.caching)
        self.returnString = StringIO()
        self.device = TextConverter(self.resourceManager, self.returnString, laparams=self.laparams)


    def destroy_handlers(self):
        """ Destroy the pdfminer handlers. """
        self.resourceManager = None
        self.returnString.close()
        self.device.close()


    def set_path(self, path):
        """ Set the path variable to the .pdf file. """
        self.__is_file_valid(path)
        self.fName = os.path.basename(path).replace(".pdf", "")
        self.path = path


    def extract_text_from_pdf(self):
        """ Extract the text from the .pdf file located in self.path and place it in self.text variable. """
        self.__is_file_valid(self.path)
        self.create_handlers()

        interpreter = PDFPageInterpreter(self.resourceManager, self.device)
        with open(self.path, 'rb') as fp:
            for page in PDFPage.get_pages(  fp,
                                            self.pagenos,
                                            maxpages=self.maxpages,
                                            password=self.password,
                                            caching=self.caching,
                                            check_extractable=True):
                page.rotate = (page.rotate + self.rotation) % 360
                interpreter.process_page(page)

        self.text = self.returnString.getvalue()
        self.destroy_handlers()

    def export_to_file(self, path = None):
        """ Write the content of self.text to a file. """
        if path == None:
            path = self.fName + ".txt"
        else:
            if not os.path.exists(os.path.dirname(path)):
                raise Exception("Path does not exist.")

        if self.text == "" or self.text == None:
            raise Exception("self.text is empty.")

        with open(path, "w") as fw:
            fw.write(self.text)


    def export_to_mp3(self, path = None):
        """ Export the text to given path. """
        if path == None:
            path = self.fName + ".mp3"
        else:
            if not os.path.exists(os.path.dirname(path)):
                raise Exception("Path does not exist.")
            if not path.endswith(".mp3"):
                raise Exception("Output path needs to be a .mp3 file.")

        if self.text == "" or self.text == None:
            raise Exception("self.text is empty.")

        oFile = gTTS(text=self.text, lang='en')
        oFile.save(path)

    def __is_file_valid(self, path):
        """ Check to see if the file path is valid. """
        if not os.path.exists(path):
            raise Exception("The path to the given file does not exist:\n" + path)
        if not path.endswith(".pdf"):
            raise Exception("The given file is not a .pdf file:\n" + path)

def usage(name):
    """ Describes the usage of the script. """
    print( f'Usage: {name} [-h --help Help] [-P password] [-O output_dir] [-c encoding] [-R rotation]'
            ' [-p pagenos] [-m maxpages] [-S] [-C] [-n] [-A] [-V] [-M char_margin]'
            ' [-L line_margin] [-W word_margin] [-F boxes_flow] [-d] input.pdf ...')
    return 100


if __name__ == "__main__":
    obj = PDFtoMP3()

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hhelp:P:O:R:p:m:SCnAVM:W:L:F:')
    except getopt.GetoptError:
        usage(sys.argv[0])

    output = None
    for (k, v) in opts:
        if k == '-h' or k == '--help': usage(sys.argv[0]); exit()
        if k == '-P': obj.password = v.encode('ascii')
        elif k == '-O': output = v
        elif k == '-R': obj.rotation = int(v)
        elif k == '-p': obj.pagenos.update( int(x)-1 for x in v.split(',') )
        elif k == '-m': obj.maxpages = int(v)
        elif k == '-C': obj.caching = False
        elif k == '-n': obj.laparams = None
        elif k == '-A': obj.laparams.all_texts = True
        elif k == '-V': obj.laparams.detect_vertical = True
        elif k == '-M': obj.laparams.char_margin = float(v)
        elif k == '-W': obj.laparams.word_margin = float(v)
        elif k == '-L': obj.laparams.line_margin = float(v)
        elif k == '-F': obj.laparams.boxes_flow = float(v)

    if len(args) == 0 or not os.path.exists(args[0]):
        raise Exception("Path is not valid: " + args[0])
    obj.set_path(args[0])

    obj.extract_text_from_pdf()

    obj.export_to_mp3(output)
