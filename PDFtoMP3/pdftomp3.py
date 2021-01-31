#!/usr/bin/env python3

""" PDFtoMP3

    Description:    Converts a PDF file to a MP3 file.

    Parameters:     -h, --help, help,       Print's usage of the script.
                    -P, password            The password for the PDF file.
                    -O, output path,        The output path of the MP3 file.
                    -R, rotation,           Rotation of the pages.
                    -p, page numbers,       Pages to be extracted, default it extract text from all pages.
                    -m, max pages,          Max pages to be read.
                    -C, caching,            Suppress object caching.
                    -n, layout,             Suppress layout analysis.
                    -A, all text,           Force layout analysis for all the text strings, including text in figures.
                    -V, Vertical read,      Allow vertical read.
                    -M, char margin,        Character margin.
                    -W, word margin,        Word margin.
                    -L, line margin,        Line margin.
                    -F, boxes flow,         x and y position of a text matters when determining a text order.
                    -r, voice rate,         The speed in which the voice is talking.
                    -v, volume,             The volumne of the voice.
                    -f, page filter,        Pages to be ignored (first index = 1)
                                            Format:     1-3 (Pages 1 to 3)
                                                        5 (Page 5)

"""

__author__ = "alexemanuelol"
__dependencies__ = ["pdfminer", "pyttsx3"]

import os
import getopt
import pyttsx3
import re
import sys

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


class PDFtoMP3():

    def __init__(self, path = None):
        """ Init. """
        if path != None:
            self.__is_file_valid(path)
            self.fName = os.path.basename(path).replace(".pdf", "")

        self.path = path
        self.text = ""
        self.__pageFilter = [-1]

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

        # TTS options
        self.rate = 150
        self.volume = 1.0

        self.create_handlers()


    def create_handlers(self):
        """ Create the pdfminer/tts handlers. """
        # pdfminer handlers
        self.resourceManager = PDFResourceManager(caching=self.caching)
        self.returnString = StringIO()
        self.device = TextConverter(self.resourceManager, self.returnString, laparams=self.laparams)

        # TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)


    def destroy_handlers(self):
        """ Destroy the pdfminer handlers. """
        self.resourceManager = None
        self.returnString.close()
        self.device.close()


    def set_path(self, path):
        """ Set the path variable to the PDF file. """
        self.__is_file_valid(path)
        self.fName = os.path.basename(path).replace(".pdf", "")
        self.path = path

    def set_page_filter(self, pageFilter):
        """ Set which pages that shouldn't be included in the end file. """
        self.__is_filter_valid(pageFilter)
        self.__pageFilter = pageFilter

    def extract_text_from_pdf(self):
        """ Extract the text from the PDF file located in self.path and place it in self.text variable. """
        self.__is_file_valid(self.path)
        self.create_handlers()

        interpreter = PDFPageInterpreter(self.resourceManager, self.device)
        with open(self.path, 'rb') as fp:
            for i, page in enumerate(PDFPage.get_pages(  fp,
                                            self.pagenos,
                                            maxpages=self.maxpages,
                                            password=self.password,
                                            caching=self.caching,
                                            check_extractable=True)):
                if (i + 1) not in self.__pageFilter:
                    page.rotate = (page.rotate + self.rotation) % 360
                    interpreter.process_page(page)

        self.text = self.returnString.getvalue()

        self.text = re.sub(r"(?<!\n)\n{1}(?!\n)", " ", self.text)
        self.text = self.text.replace("\n\n", "\n")

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

        self.engine.save_to_file(self.text, path)
        self.engine.runAndWait()
        self.engine.stop()

    def __is_file_valid(self, path):
        """ Check to see if the file path is valid. """
        if not os.path.exists(path):
            raise Exception("The path to the given file does not exist:\n" + path)
        if not path.endswith(".pdf"):
            raise Exception("The given file is not a .pdf file:\n" + path)
        return True

    def __is_filter_valid(self, pageFilter):
        """ Check if the filter is valid. """
        if not isinstance(pageFilter, list):
            raise Exception('pageFilter is not a list:\n' + str(pageFilter))
        elif not all(isinstance(x, int) for x in pageFilter):
            raise Exception('Not all elements in the list is intergers:\n' + str(pageFilter))
        return True

def usage(name):
    """ Describes the usage of the script. """
    print( f'Usage: {name} [-h --help Help] [-P password] [-O output_dir] [-c encoding] [-R rotation]'
            ' [-p pagenos] [-m maxpages] [-r rate] [-v volume] [-S] [-C] [-n] [-A] [-V] [-M char_margin]'
            ' [-L line_margin] [-W word_margin] [-F boxes_flow] [-d] input.pdf ...')
    return 100


if __name__ == "__main__":
    obj = PDFtoMP3()

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hhelp:P:O:R:p:m:SCnAVM:W:L:F:r:v')
    except getopt.GetoptError:
        usage(sys.argv[0])

    filt = []
    arguments = sys.argv
    inFilter = False
    for item in arguments:
        if item == '-f':
            inFilter = True
            continue

        if inFilter and item in [   '-h', '--help', '-P', '-O', '-R',
                                    '-p', '-m', '-C', '-n', '-A', '-V',
                                    '-M', '-W', '-L', '-F', '-r', '-v']:
            break

        if inFilter:
            if '-' in item:
                temp = item.split('-')
                if len(temp) != 2:
                    usage(arguments[0])
                    exit()
                for page in range(int(temp[0]), int(temp[1]) + 1):
                    filt.append(int(page))
            else:
                filt.append(int(item))

    output = None
    for (k, v) in opts:
        if k == '-h' or k == '--help': usage(sys.argv[0]); exit()
        elif k == '-P': obj.password = v.encode('ascii')
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
        elif k == '-r': obj.rate = int(v)
        elif k == '-v': obj.volume = float(v)

    if len(args) == 0 or not os.path.exists(args[0]):
        raise Exception("Path is not valid: " + args[0])

    obj.set_path(args[0])

    if filt:
        obj.set_page_filter(filt)

    obj.extract_text_from_pdf()

    obj.export_to_mp3(output)
