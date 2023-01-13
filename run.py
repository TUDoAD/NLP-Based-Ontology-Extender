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


##
# 

Onto_filenames = ["bao_complete_merged", "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"]
min_counts_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]   
use_IUPAC_goldbook = True

extender_modules.ConceptExtractor_methanation_diffMCs(Onto_filenames, use_IUPAC_goldbook, min_counts_list)