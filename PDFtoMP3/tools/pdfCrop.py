#!/usr/bin/env python3

""" PDFCrop

    Description:    Enables cropping of a PDF file, choosing which pages to be removed.

    parameters:     -p, input path,     Path to the input PDF file.
                    -f, pageFilter,     A list of numbers indication which pages to be removed (first index = 1).
                                        Format:     1-3 (Pages 1 to 3)
                                                    5 (Page 5)
                    -o, output path,    Path to the output PDF file.

"""

__author__ = 'alexemanuelol'
__dependencies__ = ['PyPDF2']

import sys
import os
from PyPDF2 import PdfFileWriter, PdfFileReader

class PDFCrop():

    def __init__(self, path = None, pageFilter = [-1]):
        """ Init. """
        self.__cropped = False

        self.__infile = None
        self.__outfile = None
        self.__path = None

        if path != None:
            self.__is_file_valid(path)
            self.read_pdf(path)
            self.__path = path

        self.__is_filter_valid(pageFilter)
        self.__pageFilter = pageFilter

    def set_path(self, path):
        """ Set the path to the .pdf file. """
        self.__is_file_valid(path)
        self.__path = path

    def set_page_filter(self, pageFilter):
        """ Set which pages that shouldn't be included in the end file. """
        self.__is_filter_valid(pageFilter)
        self.__pageFilter = pageFilter
        self.__cropped = False

    def read_pdf(self, path = None):
        """ Read the .pdf file. """
        if path != None:
            self.__is_file_valid(path)
            self.__path = path
        elif self.__path == None:
            raise Exception('Not path set in path or self.__path.')

        self.__infile = PdfFileReader(self.__path, 'rb')
        self.__outfile = PdfFileWriter()
        self.__cropped = False

    def crop_pdf(self):
        """ Remove the pages in self.__pageFilter. """
        if self.__infile == None:
            raise Exception('.pdf file is not read.')

        if self.__pageFilter == [-1]:
            raise Exception('self.__pageFiler is empty, please select pages to be removed.')

        self.__cropped = True

        for i in range(1, self.__infile.getNumPages() + 1):
            if i not in self.__pageFilter:
                self.__outfile.addPage(self.__infile.getPage(i - 1))

    def write_pdf(self, path = None):
        """ Writes the cropped file. """
        if self.__outfile == None:
            raise Exception('.pdf file is not read.')

        if path == None:
            path = self.__path.replace('.pdf', '_cropped.pdf')

        directory = os.path.dirname(path)
        if directory == '':
            directory = '.'

        if not os.path.exists(directory):
            raise Exception('Path does not exist:\n' + str(directory))

        if not self.__cropped:
            raise Exception('.pdf file have not yet been cropped.')

        with open(path, 'wb') as f:
            self.__outfile.write(f)

    def __is_file_valid(self, path):
        """ Check if the file is valid. """
        if not os.path.exists(path):
            raise Exception('Path does not exist:\n' + str(path))
        elif not path.endswith('.pdf'):
            raise Exception('File is not a .pdf file:\n' + str(path))
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
    print(  f'Usage: py {name} [-h --help Help]\n'
            f'       -p path\n'
            f'       -f [1-n pages, format: interval of pages 1-5, or single page 4]\n'
            f'       [-o output path]\n\n'
            f'Example: py {name} -p "sample.pdf" -f 1-4 6 10 12-15')
    return 100

if __name__ == '__main__':
    obj = PDFCrop()
    inputPath = ''
    outputPath = ''
    filt = []

    args = sys.argv

    if len(args) < 5 or not '-p' in args or not '-f' in args or '-h' in args or '--help' in args:
        usage(args[0])
        exit()

    currentFlag = ''
    for item in args:
        if item == '-p' or item == '-f' or item == '-o':
            currentFlag = item
            continue

        if currentFlag == '-p':
            inputPath += item
        elif currentFlag == '-f':
            if '-' in item:
                temp = item.split('-')
                if len(temp) != 2:
                    usage(args[0])
                    exit()
                for page in range(int(temp[0]), int(temp[1]) + 1):
                    filt.append(int(page))
            else:
                filt.append(int(item))
        elif currentFlag == '-o':
            outputPath += item

    obj.read_pdf(inputPath)
    obj.set_page_filter(filt)
    obj.crop_pdf()
    obj.write_pdf(outputPath if outputPath != '' else None)
