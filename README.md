# NLP-Based-Ontology-Extender
This repository contains the codes for the NLP-Based-Ontology-Extender by Alexander S. Behr, TU Dortmund University, created in context of NFDI4Cat TA1. 
The code can be used to extend ontologies automatically based on text data with help of Word2Vec.

**Needed modules (list may not be complete!):**

```
pip install owlready2
pip install gensim
pip install pdfminer
```

## run.py (main program)
Run this file to execute the whole workflow as shown below
![Program Scheme](image/Code_workflow.png?raw=true "scheme of overall workflow executed by running run.py")


## w2v_ontology_extender_modules.py (module with functions)
Contains all functions used in run.py to execute the data extraction, train the word2vec models and extend the ontologies as described.

```
textmining(<string>)
```
used for retrieval of text data from pdfs stored in `./import/` subdir. Preprocessed text containing only noun and propnoun token stored in pickle with name "name" in subdir `./pickle/`.
Raw read-in text stored as pickle "name_raw" in subdir `./pickle/`.

```
concept_dictionary, metrics = w2v_ext.concept_extractor(Onto_filenames,
                                                        use_IUPAC_goldbook,
                                                        min_counts_list,
                                                        pickle_name,
                                                        goldbook_mute)
```
Loads semantic artifacts, loads text-pickle and trains w2v model with desired min_count(s). Outputs list of token and definitions based on min_count list and "statistics"/metrics as excel-files in subdir `./xlsx-files/` trained word2vec models are pickled in subdir `./models/`.
Also outputs concept_dictionary, a dictionary containing all common labels of text data and ontologies respective to `min_count`s.

```
metrics_onto_extension = w2v_ext.ontology_class_extender(Onto_filenames_ext,
                                                         use_IUPAC_goldbook,
                                                         extend_ontology,
                                                         min_counts_list,
                                                         pickle_name,
                                                         similarity_threshold_list,
                                                         mute_prints)
```
Extends `extend_ontology` (name of ontology provided as string) by classes and relations and stores the modified ontologies in subdir `./ontologies_output/`. 
Loads semantic artifacts and text-pickle to train w2v model with desired min_counts outputs list of token and definitions based on min_count list. 
Returns metrics as dict and stores it as excel-file in subdir `./xlsx-files/`.


## todo:
Ontology_normalizer_w2v_MC1-25.py -> Annotates classes in extended ontology with definitions


#####

Supported ontologies and semantic artifacts, when stored in subdir `./ontologies/`:

| Ontology / Semantic Artifact | Stored in `./ontologies/` as: |
| ---------------------------- | ----------------------------- |
| BioAssayOntology             | bao_complete_merged.owl       |
| Content Cell  | Content Cell  |

Name| stored in ./ontologies/ as:| valid argument name for extender_modules.ConceptExtractor_methanation_diffMCs()| Link to file 
BioAssayOntology |"bao_complete_merged.owl"|"bao_complete_merged"|
, "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"

goldbook_vocab.json

