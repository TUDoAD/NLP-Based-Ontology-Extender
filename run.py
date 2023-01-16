"""
Created on Fri Jan 13 13:21:08 2023

@author: A. S. Behr
@affiliation: TU Dortmund University
@comment: Functions and code described in paper "Ontology Extension by NLP-based 
Concept Extraction for Domain Experts in Catalytic Sciences" by A. S. Behr,
M. Völkenrath, N. Kockmann

"""


import w2v_ontology_extender_modules as w2v_ext

# reads in pdf files stored in subdir ./import/
# and stores preprocessed data as pickles in subdir ./pickle/
w2v_ext.textmining("test")


##
# 

Onto_filenames = ["bao_complete_merged", "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"]
min_counts_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]   
use_IUPAC_goldbook = True
pickle_name = "methanation_only_text"
goldbook_mute = False

# train w2v models based on min_count and store in ./models/ 
concept_dictionary, metrics = w2v_ext.concept_extractor(Onto_filenames,
                                                        use_IUPAC_goldbook,
                                                        min_counts_list,
                                                        pickle_name,
                                                        goldbook_mute)
## extend ontology AFO
Onto_filenames_ext = ["bao_complete_merged", "chebi", "chmo", "NCIT", "SBO"]
#use_IUPAC_goldbook = True
extend_ontology = "Allotrope_OWL"
#min_counts_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]   
similarity_threshold_list = [0.8,0.9,0.95,0.99,0.995,0.996,0.997,0.998,0.999]
mute_prints = True

w2v_ext.ontology_class_extender(Onto_filenames_ext,
                                use_IUPAC_goldbook,
                                extend_ontology,
                                min_counts_list,
                                pickle_name,
                                similarity_threshold_list,
                                mute_prints)



w2v_ext.ontology_class_annotator()

#

