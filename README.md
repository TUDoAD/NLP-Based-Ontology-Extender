# NLP-Based-Ontology-Extender
 Code to extend ontologies automatically based on text data.


run.py -> preprocessing pdf to pickles
pdf_globing.py -> pdf data extraction
data_save.py -> saving raw text data as pickle
data_preprocessing_spacy -> preprocesses extracted data, saves as pickle
w2v_training.py -> trains w2v model

ConceptExtractor_methanation_diffMCs.py -> Loads semantic artifacts, loads text-pickle and trains w2v model with desired min_counts outputs list of token and definitions based on min_count list as excel-file

Ontology_normalizer_w2v_MC1-25.py -> Annotates classes in extended ontology with definitions

Onto_Extender_mc_test.py -> Extends ontology by classes based on selected ontology, similarity threshold and w2vec model 

LocalOntologies.py -> description_dicts used to extract classes as list and definitions as dictionary
OntoClassSearcher.py -> needs LocalOntologies module, contains onto_loader function, that returns description_list_dict and class_dict
