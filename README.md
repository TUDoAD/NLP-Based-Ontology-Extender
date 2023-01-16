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


## todo:
Ontology_normalizer_w2v_MC1-25.py -> Annotates classes in extended ontology with definitions


#####

Supported ontologies and semantic artifacts stored in subdir ./ontologies/ :

Name| stored in ./ontologies/ as:| valid argument name for extender_modules.ConceptExtractor_methanation_diffMCs()| Link to file 
BioAssayOntology |"bao_complete_merged.owl"|"bao_complete_merged"|
, "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"

goldbook_vocab.json

