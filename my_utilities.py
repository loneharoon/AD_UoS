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
    from PyPDF2 import PdfFileMerger
    merger = PdfFileMerger()
    for pdf in  file_list:
        merger.append(open(pdf, 'rb'))
    with open(savefilename, 'wb') as fout:
        merger.write(fout)
