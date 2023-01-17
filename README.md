# NLP-Based-Ontology-Extender
This repository contains the codes for the NLP-Based-Ontology-Extender by Alexander S. Behr, TU Dortmund University, created in context of NFDI4Cat TA1. 
The code can be used to extend ontologies automatically based on text data with help of Word2Vec.

**Needed modules (list may not be complete!):**

`pip install owlready2`

`pip install gensim`

`pip install pdfminer`


## run.py (main program)
Run this file to execute the whole workflow as shown below
![Program Scheme](image/Code_workflow.png?raw=true "scheme of overall workflow executed by running run.py")


## w2v_ontology_extender_modules.py (module with functions)
Contains all functions used in run.py to execute the data extraction, train the word2vec models and extend the ontologies as described.

`textmining(<string>)`:used for retrieval of text data from pdfs stored in ./import/ subdir. Preprocessed text containing only noun and propnoun token stored in pickle with name "name" in subdir ./pickle/.
Raw read-in text stored as pickle "name_raw" in subdir ./pickle/.

`concept_extractor(ontology_filenames = ["Allotrope_OWL"],

                      use_IUPAC_goldbook = True, 

                      min_count_list = [1],

                      preprocessed_text_pickle_name = "methanation_only_text",

                      gb_muted = True):`
Loads semantic artifacts, loads text-pickle and trains w2v model with desired min_count(s). Outputs list of token and definitions based on min_count list and "statistics"/metrics as excel-files in subdir ./xlsx-files/ trained word2vec models are pickled in subdir ./models/

## todo:
Ontology_normalizer_w2v_MC1-25.py -> Annotates classes in extended ontology with definitions


#####

Supported ontologies and semantic artifacts stored in subdir ./ontologies/ :

Name| stored in ./ontologies/ as:| valid argument name for extender_modules.ConceptExtractor_methanation_diffMCs()| Link to file 
BioAssayOntology |"bao_complete_merged.owl"|"bao_complete_merged"|
, "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"

goldbook_vocab.json

