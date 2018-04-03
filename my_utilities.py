#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This script contains diverse utility funs
Created on Tue Mar 20 11:21:34 2018

@author: haroonr
"""

#%%
def create_pdf_from_pdf_list(file_list, savefilename):
    ''' combine pdfs '''
    from PyPDF2 import PdfFileMerger, PdfFileReader
    merger = PdfFileMerger()
    for pdf in  file_list:
        fin = PdfFileReader(open(pdf, 'rb')) 
        merger.append(fin)
    merger.write(savefilename)
    
        
        

def create_pdf_from_pdf_list_ver2(file_list, savefilename):
    ''' Alternative of create_pdf_from_pdf_list, it uses different approach as, but results are same  '''
    from PyPDF2 import PdfFileReader, PdfFileWriter
    #merger = PdfFileMerger()
    initial_output = PdfFileWriter()
    for pdf in  file_list:
        infile = PdfFileReader(open(pdf, "rb"))
        initial_output.addPage(infile.getPage(0))
    with open(savefilename, 'wb') as fout:
        initial_output.write(fout)