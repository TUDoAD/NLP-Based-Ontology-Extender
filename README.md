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

## Main Program Functions
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
							 provenance_string,
                                                         mute_prints)
```
Extends `extend_ontology` (name of ontology provided as string) by classes and relations and stores the modified ontologies in subdir `./ontologies_output/`. 
Loads semantic artifacts and text-pickle to train w2v model with desired min_counts outputs list of token and definitions based on min_count list. 
Returns metrics as dict and stores them as excel-file in subdir `./xlsx-files/`.
Automatically added classes and texts are denoted by a string "[provenance_string]" within the resulting ontology. 
This later allows for more easy search of automatically created content.

```
metrics_onto_annotation =  w2v_ext.ontology_class_annotator(list_of_ontologies_to_annotate,
                                                            Onto_filenames,
                                                            use_IUPAC_goldbook,
                                                            provenance_string,
                                                            mute_prints)
```
Annotates classes in extended ontology with definitions from other semantic artifacts (string values) and stores the annotated input ontology in `./ontologies_output/` with name ending "_output.owl".
Stores number of unique keys and classes added as json-files in subdir `./json-files/`for metrics as files ending with "_new_classes.json". 
Returns metrics as dict and stores them as excel-file in subdir `./xlsx-files/`.
Automatically added classes and texts are denoted by a string "[provenance_string]" within the resulting ontology. 
This later allows for more easy search of automatically created content.

## Supported Semantic Artifacts

Supported ontologies and semantic artifacts, when stored in subdir `./ontologies/`:

| Ontology / Semantic Artifact | Stored in `./ontologies/` as: | Valid argument string in `w2v_ontology_extender_modules.py`|
| ---------------------------- | ----------------------------- |----------------------------------------------------------------------|
| Allotrope Foundation Ontology| Allotrope_OWL.owl             | "Allotrope_OWL"|
| BioAssayOntology             | bao_complete_merged.owl       | "bao_complete_merged" |
| Chemical Entities of Biological interest | chebi.owl | "chebi" |
| Chemical Methods Ontology | chmo.owl | "chmo" |
| System Biology Ontology | SBO.owl | "SBO" |
| National Cancer Institute Thesaurus| NCIT.owl | "NCIT"|
| IUPAC-Goldbook| goldbook_vocab.json | via bool: `use_IUPAC_goldbook = True` as argument|
