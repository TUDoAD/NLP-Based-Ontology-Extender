# NLP-Based-Ontology-Extender
 Code to extend ontologies automatically based on text data.


#run.py -> preprocessing pdf to pickles
#pdf_globing.py -> pdf data extraction
#data_save.py -> saving raw text data as pickle
#data_preprocessing_spacy -> preprocesses extracted data, saves as pickle
#w2v_training.py -> trains w2v model
#LocalOntologies.py -> description_dicts used to extract classes as list and definitions as dictionary
#OntoClassSearcher.py -> needs LocalOntologies module, contains onto_loader function, that returns description_list_dict and class_dict

#ConceptExtractor_methanation_diffMCs.py -> Loads semantic artifacts, loads text-pickle and trains w2v model with desired min_counts outputs list of token and definitions based on min_count list as excel-file

--Onto_Extender_mc_test.py -> Extends ontology by classes based on selected ontology, similarity threshold and w2vec model 
Ontology_normalizer_w2v_MC1-25.py -> Annotates classes in extended ontology with definitions

## Todos: 

Einmal am Anfang vom run.py !?:
##Load Definitions 
[class_dict, desc_dict] = onto_loader(ontology_filenames)

- Umbenennen von extender_modules.py zu w2v_ontology_extender_modules.py - dann "import w2v_ontology_extender_modules as w2v_ext"

#####

Supported ontologies and semantic artifacts stored in subdir ./ontologies/ :

Name| stored in ./ontologies/ as:| valid argument name for extender_modules.ConceptExtractor_methanation_diffMCs()| Link to file 
BioAssayOntology |"bao_complete_merged.owl"|"bao_complete_merged"|
, "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"

goldbook_vocab.json

