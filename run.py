"""
Created on Fri Jan 13 13:21:08 2023

@author: A. S. Behr
@affiliation: TU Dortmund University
@comment: Functions and code described in paper "Ontology Extension by NLP-based 
Concept Extraction for Domain Experts in Catalytic Sciences" by A. S. Behr,
M. Völkenrath, N. Kockmann

"""


import extender_modules

# reads in pdf files stored in subdir ./import/
# and stores preprocessed data as pickles in subdir ./pickle/
extender_modules.textmining("test")


