"""
Created on Fri Jan 13 12:42:25 2023

@author: A. S. Behr
@affiliation: TU Dortmund University
@comment: Functions and code described in paper "Ontology Extension by NLP-based 
Concept Extraction for Domain Experts in Catalytic Sciences" by A. S. Behr,
M. Völkenrath, N. Kockmann

"""

# general imports used
from gensim.models import Word2Vec
import pickle

# imports for preprocessing functions:
import glob2
import spacy

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO

# imports for ontology related functions:
import pandas as pd
import numpy as np

import random
import re 
import json
import types

from owlready2 import *
from tqdm import tqdm

####

def textmining(name):
    """
    textmining - used for retrieval of text data from pdfs stored in ./import/ subdir. 
    Preprocessed text containing only noun and propnoun token stored in 
    pickle with name "name" in subdir ./pickle/.
    Raw read-in text stored as pickle "name_raw" in subdir ./pickle/.

    Parameters
    ----------
    name : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    name_raw = name + "_raw"

    # extracting text out of PDF files and save string
    print('Extracting text of PDF...')
    data_raw = get_globed_content()
    save_pickle(data_raw, name_raw)
    print('Done!')

    # preprocessing text and save string
    print('Preprocessing text...')
    data_prep = preprocessing(data_raw)
    save_pickle(data_prep, name)
    print('Done!')
    #eg-use: textmining("methanation_mc1")

def get_pdf_file_content(pdf_file):
    """
    extracts content from pdf file, returns text as string . 

    Parameters
    ----------
    pdf_file : TYPE
        DESCRIPTION.

    Returns
    -------
    text : TYPE
        DESCRIPTION.

    """
    # extract the text of PDF-files
    # used to store resources in the PDF, for example images
    resource_manager = PDFResourceManager(caching=True)
    out_text = StringIO()

    # object from the PDF miner layout parameters
    la_params = LAParams()
    text_converter = TextConverter(resource_manager, out_text, laparams=la_params)
    fp = open(pdf_file, mode='rb')
    interpreter = PDFPageInterpreter(resource_manager, text_converter)

    # Process the content of each page of the PDF file
    for page in PDFPage.get_pages(fp, pagenos=set(), maxpages=0, password='', caching=True, check_extractable=True):
        interpreter.process_page(page)
    text = out_text.getvalue()

    # close resources
    fp.close()
    text_converter.close()
    out_text.close()
    return text

def get_globed_content():
    """
    uses glob2 package to retrieve all .pdf files stored in subdir ./import/

    Returns
    -------
    pdf_text_string : TYPE
        DESCRIPTION.

    """
    # pdf data extraction
    # opens all PDF files stored in directory ./import, 
    # hands it to get_pdf_file_content function and converts it 
    # into string
    pdf_globed = glob2.glob('./import/*.pdf')
    pdf_text = []
    for i in range(len(pdf_globed)):
        pdf_text.append(get_pdf_file_content(pdf_globed[i]))
    pdf_text_string = ''.join(pdf_text)
    return pdf_text_string

def save_pickle(pdf_data, pickle_name):
    """
    stores data as pickle in subdir ./pickle/

    Parameters
    ----------
    pdf_data : TYPE
        DESCRIPTION.
    pickle_name : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    with open('./pickle/' + pickle_name + '.pickle', 'wb') as handle:
        pickle.dump(pdf_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle(pickle_name):
    """
    reads stored pickle data from subdir ./pickle/    
    Parameters
    ----------
    pickle_name : TYPE
        DESCRIPTION.

    Returns
    -------
    data_open : TYPE
        DESCRIPTION.
    """
    with open('./pickle/' + pickle_name + '.pickle', 'rb') as handle:
        data_open = pickle.load(handle)
    return data_open


def create_model(preprocessed_data, minc):
    """
    Trains word2vec model based on preprocessed_data (lists of token)
    and based on minc = min_count parameter, which limits the amount of 
    minimal repetitions a token has to have in the text dataset.
    Outputs respective word2vec model


    Parameters
    ----------
    preprocessed_data : TYPE
        DESCRIPTION.
    minc : TYPE
        DESCRIPTION.

    Returns
    -------
    model : TYPE
        DESCRIPTION.

    """

    model = Word2Vec(preprocessed_data, vector_size=300, alpha=0.025, min_count=minc)

    return model

def is_relevant(token):
    """
    tests if a token is important for POS-tagging 
    here, only NOUN and PROPNOUN tokens are considered.

    Parameters
    ----------
    token : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    # NOUN - nouns; PROPN - proper noun; VERB - verbs; ADJ - adjective; NUM - number; PUNCT - punctuation
    pos_tags = ['NOUN', 'PROPN']
    if token.pos_ in pos_tags:
        return True
    else:
        return False


def is_datawaste(token):
    """
    tests if a token is important by comparison to waste list.

    Parameters
    ----------
    token : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    waste = ['fig', 'figure', 'table', 'tab', 'site', 'min', 'max', 'number', 'vol.%', 'xxx', 'mmo', 'ghsv', 'usy',
             'use', 'article', 'tpr', 'image', 'idh', 'con-', 'scr', 'igm', 'author', 'xps', 'lyst', 'cdpr', 'mpa',
             'ref', 'ppm', 'wt.%', 'cm-1', 'pro-', 'ml-1', 're-', 'rng', 'ptg', 'rsc', 'sbcr', 'sci', 'wiley', 'vch',
             'verlag', 'alyst', 'kgaa', 'h-1', 'w.j', 'xxxx', 'wt-%', 'vol-%', 'rmse', 'adv', 'd.s.a', 'http', 'doi',
             'gao', 'list', 'b.v', 'spr', 's-1', 'mol', 'mol1', 'l-1', 'flh', 'cpst', 'appl', 'ltd', 'tso', 'hydro-',
             'sbe900', 'csl', 'sbp4', 'icp', 'ely', 'tem-', 'dft', 'acs', 'fcc', 'mfr', 'sic', 'kpa', 'igg', 'whsv',
             'cm3', 'bjh', 'tof', 'std.l', 'i', 'ii', 'iii', 'iv', 'v', 'cox', 'pres-', 'sty', 'k.p', '.', 's1a†',
             'technol', 'tion', 'mgo', 'jie', 'liu', 'xrd', 'sng', 'tem', 'tpd', 'nio', 'co.', 'xco2', 'bid', 'ceo2',
             'ldh', 'cnt', 'nimn1al10', 'ce0.5zr0.5o2', 'mcr-2x', 'situ', 'ldhs', 'aubps', 'nial', 'ture', 'gms',
             'h−1', '/kg', 'cm−1', 'alox', 'author', 'sch4', 'ceria', 'ml−1', 'ucr', 'mgal', 'mg2−xal', '-al2o3',
             'mgal2o4', '4.8%ni', '5%pr-12%ni', 'sem', 'mnoy', 'nimn0.5al10', '12%ni', 'perature', 'methana-', 'cepte',
             'la2o3', 'nimnxal10', 'eq', 'nimn2al10', 'cata-', 'ing', 'lee', 'rwgs', 'lyst', 'tcd', 'ftir', 'simakov',
             'com-', 'rh(1%)/', 'gem', 'hrtem', 'cfd', 'mol1', 'aubp', 'l−1', 'g-1', 'sorption', 'usyie', 'ature',
             'kmol', 'ych4', 'conver-', 'kgcat.h', 'ni(co)4', 'emol', '/gj', 'ysz', 'pem', 'dn50', 'liu', 'm-³',
             'go¨rke', 'tive', 'reac-', 'nhs', 'nial2o4', 'aunr', 'ml$g‒1$h‒1', 'sol', 'alyst', 'ccus', 'ence', 'ni/',
             'δh298k', 'ce0.72zr0.28o2', 'ru.tio2', 'rha', 'mcm-41', 'gibb', 'nixmg2−xal', 'ni3fe', 'perfor-', 'gen',
             'tofni', 'edc', 'tivity', '5%sreni', '3m-350', '5%x-12%ni', 'eff', 'gms,0', 'cmol', 'pbs', 'car-', 'cnfs',
             'fax', '+86', 'tel', 'jcpds', 'mg1.6al', '5%baeni', 'c.v', 'mg1.6al', 'pdf', '5%sreni', '5%baeni',
             'perfor-', 'eff', 'cnfs', '2.5%mg', '5%x-12%ni', 'ni-', '5%mgeni', '5%caeni', 'ther-', 'lid', 'hcoo',
             'gcat', 'sreni', 'rhtotal', 'δh0', '3s-350', 'co2]in', 'de-', 'sect', 'r.a', 'nio−mgo', '10b', '15%ni',
             'dagle', 'rh/', '5%gd-12%ni', '5%ce-12%ni', '2p3/2', 'jeol', 'vol%', 'ity', 'calcu-', 'wgs', 'mg0.4al',
             'ni1.6', 'mg1.2al', 'cat-', 'mof', 'zsw', 'mea', 'bulk', '5%la-12%ni', 'ni(15%)/tio2', 'iwi''nix/', 'sor',
             'dis-', 'dh298', 'dh298k', 'ni(no3)2·6h2o', 'ru/', '0.86mn', 'cle', 'centration', 'cal', 'fin', 'fout',
             'oad', 'tsos', 'mol−1', 'eac', 'sro2', 'sbp900_av', '/(mw⁄a', 'wfo', 'sbet', 'vmicro', '3.7%ni', 'ni−mg',
             'mg−ni', 'atm', 'kg(cid:2']
    if token.text in waste:
        return True
    else:
        return False

def preprocessing(pdf_data):
    """
    preprocesses extracted text data, returns tokenized list of words acc. to
    token classes specified in function is_relevant(token).
    
    Parameters
    ----------
    pdf_data : TYPE
        DESCRIPTION.

    Returns
    -------
    sentences_lem : TYPE
        DESCRIPTION.

    """
    # function for preprocessing pdf_data with spacy module
    # import spacy library
    lib = spacy.load('en_core_web_sm')
    #lib = spacy.load('de_core_news_md')
    # fix max length
    lib.max_length = 150000000

    # convert text into lower case
    data = pdf_data.lower()

    # create a doc object
    doc = lib(data)

    # create a list of sentences
    sentences = []
    for sentence in doc.sents:
        temp = [sentence]
        sentences.append(temp)

    # deleting unimportant words by POS
    sentences_imp = []
    for sentence in sentences:
        for token in sentence:
            temp = []
            for i in range(len(token)):
                if is_relevant(token[i]):
                    temp.append(token[i])
            sentences_imp.append(temp)

    # deleting unimportant words by comparison
    sentences_imp_2 = []
    for sentence in sentences_imp:
        temp = []
        for token in sentence:
            if not is_datawaste(token):
                temp.append(token)
        sentences_imp_2.append(temp)

    # deleting single letters
    sentences_delsm = []
    for sentence in sentences_imp_2:
        temp = []
        for token in range(len(sentence)):
            if len(sentence[token]) > 2:
                temp.append(sentence[token])
        sentences_delsm.append(temp)

    # lemmatization
    sentences_lem = []
    for sentence in sentences_delsm:
        temp = []
        for i in sentence:
            temp.append(i.lemma_)
        sentences_lem.append(temp)

    # returning preprocessed data
    return sentences_lem


##### 
# Begin of ontology related functions
#####

def load_ontologies(ontology_name):
    """
    loads an ontology from subfolder ontologies defined by its name 
    outputs list of classes contained in this ontology  

    Parameters
    ----------
    ontology_name : TYPE
        DESCRIPTION.

    Returns
    -------
    onto_class_list : TYPE
        DESCRIPTION.

    """
    new_world = owlready2.World()
    onto = new_world.get_ontology("./ontologies/{}.owl".format(ontology_name)).load()
    onto_class_list = list(new_world.classes())
    print("Loading {} done. Imported {} classes.".format(ontology_name, len(onto_class_list)))
    return onto_class_list 

class definitionError(Exception):
    """ 
    definition error used in function description_dicts to return string,
    when class definition strings could not be extracted properly
    """ 
    pass
    

def description_dicts(class_list, ontology_name):
    """
    extracts class names and descriptions based on class list (as owlready2 object)
    returns dictionary with general structure of 
    desc_dict = {ontology_class_label : Definition string}
    WARNING: Descriptions often have different identifiers (see try:... except loop)
          Implemented IAO_0000115 and .comment for now. 

    example: [class_dict, desc_dict] = onto_loader(["chmo","Allotrope_OWL", "chebi"])
    execute once to load all ontologies from list    

    Parameters
    ----------
    class_list : TYPE
        DESCRIPTION.
    ontology_name : TYPE
        DESCRIPTION.

    Raises
    ------
    print
        DESCRIPTION.
    definitionError
        DESCRIPTION.

    Returns
    -------
    desc_dict : TYPE
        DESCRIPTION.

    """
    print("Extracting class descriptions...")
    desc_dict = {}
    N_cl = len(class_list)
    temp_class_label = []
    
    def_dict = {'Allotrope_OWL':'definition',
                'NCIT':'P97',
                'chmo':'IAO_0000115',
                'chebi':'IAO_0000115',
                'bao_complete_merged':'IAO_0000115',
                'bao_complete':'IAO_0000115',
                'SBO':'comment'}
    try:
        def_id = def_dict[ontology_name]
    except:
        def_id = []
    
    for i in range(N_cl):
        temp_class = class_list[i]
        #check, if label and definition are not empty:
        #Definition: IAO_0000115, comment
        try:
            if temp_class.prefLabel:
                # if preferred label is not empty, use it as class label
                temp_class_label = temp_class.prefLabel[0].lower()
        except:
            try:
                if temp_class.label:
                    # if label is not empty, use it as class label
                    temp_class_label = temp_class.label[0].lower()
            except:
                temp_class_label = []
                print("Label for class {} not determined!".format(str(temp_class)))
                return()
        
        if temp_class_label:
            # if class got a label which is not empty, search for definition                    
            if def_id:
                try:
                    desc_dict[temp_class_label] = getattr(temp_class,def_id)
                except:
                    desc_dict[temp_class_label] = temp_class_label
                if not desc_dict[temp_class_label]: # Desc_dict empty
                    desc_dict[temp_class_label] = temp_class_label
            else:
                try: #NCIT
                    desc_dict[temp_class_label] = temp_class.P97
                except:
                    try: #temp_class.IAO_0000115
                        desc_dict[temp_class_label] = temp_class.IAO_0000115    
                    except:
                        try:
                            desc_dict[temp_class_label] = temp_class.definition
                            if not desc_dict[temp_class_label]: 
                                # .definition is empty    
                                try: #temp_class.comment
                                    desc_dict[temp_class_label] = temp_class.comment
                                except:
                                    raise print("in description_dicts - class definitions were not recognized properly.")
                                    return()
                        except:
                            raise definitionError("in description_dicts - class definitions were not recognized properly.")
                            return()
    print("Done.")
    return desc_dict

def onto_loader(ontology_names):        
    """
    Loading ontologies and storing classes and their descriptions in dictionaries.
    Parameters
    ----------
    ontology_names : TYPE
        DESCRIPTION.

    Returns
    -------
    class_list_dict : TYPE
        DESCRIPTION.
    description_list_dict : TYPE
        DESCRIPTION.

    """
    print("=============================================")
    # Ontologies to load
    # ontology_names = ["chmo","Allotrope_OWL", "chebi", "NCIT", "SBO"]
    class_list_dict = {}
    description_list_dict ={}
        
    for name in ontology_names:
        print("Loading ontology {} ...".format(name))
        class_list_dict[name] = load_ontologies(name)
        description_list_dict[name] = description_dicts(class_list_dict[name],name)
    
    # existing_keys = names of ontologies
    #existing_keys = list(description_list_dict.keys())
        
    print("Ontologies {} loaded. \n PLEASE CHECK if class descriptions are not empty.".format(str(ontology_names)))
    print("=============================================")
    return class_list_dict, description_list_dict

def onto_class_comparison(desc_list_dict, file_name, new_file_name):
    """
    Find same entries of class names in both concept_table and ontologies
    load Excel-File with name file_name and store list with all concepts, 
    and their definitions (if any) as new_file_name Excel-file.

    example: onto_class_comparison(desc_dict, 'test_Concepts', 'test_Concepts_compared')
    execute to compare labels in test_Concepts.xlsx with loaded ontologies, store resulting 
    Dataframe in test_Concepts_compared.xlsx
    
    Parameters
    ----------
    desc_list_dict : dict
        Lists classlabel and definition string of ontology class.
        Obtainable from description_dicts()
    file_name : str
        Excel file name to be read.
    new_file_name : str
        Excel file name to be written.

    Returns
    -------
    df_concepts : DataFrame
        DataFrame listing labels and all definitions for the labels according to the respective ontology.

    """   
    
    # names of ontologies within desc_list_dict
    ontology_names = list(desc_list_dict.keys())
    concept_table = pd.read_excel(file_name + '.xlsx')
    
    set_1 = [iter_string.lower() for iter_string in list(concept_table[0])]

    df_concepts = pd.DataFrame({file_name : set_1})
    
    for i in range(len(ontology_names)):
        df_concepts.insert(len(df_concepts.columns),ontology_names[i],'') # empty column with name of ontology
        set_2 = desc_list_dict[ontology_names[i]] # set (Ontology) to compare concepts to
        candidates = list(set(set_1).intersection(set_2)) # intersection of concept_table-list and ontology
        print("Found {}/{} common concept names for Ontology {} and rawdata".format(len(candidates),len(set_1),ontology_names[i]))      
        # paste description of class into respective row, when no description exist, 
        # use the class name to mark concepts, which also exist in the ontology
        for j in candidates:
            if desc_list_dict[ontology_names[i]][j]: # not empty
                try:    
                    df_concepts.loc[getattr(df_concepts, file_name) == j, ontology_names[i]] =  desc_list_dict[ontology_names[i]][j] # changes entry in ontology column to definition, when in concepts
                except:
                    df_concepts.loc[getattr(df_concepts, file_name) == j, ontology_names[i]] = str(desc_list_dict[ontology_names[i]][j])
            else:
                df_concepts.loc[getattr(df_concepts, file_name) == j, ontology_names[i]] =  j # changes entry in ontology column to definition, when in concepts    
    #save dataframe as excel sheet
    df_concepts.to_excel(new_file_name + '.xlsx') 
    print('Stored common concepts and definitions in {}'.format(new_file_name + '.xlsx'))
    return df_concepts

def definition_sampler(desc_dict):
    """
    searches for a random class in each ontology of desc_dict and 
    outputs its definition. Imports package random.
    """
    onto_list = list(desc_dict.keys())
    for i in onto_list:
        tempDefList = list(desc_dict[i].keys())
        randClass = tempDefList[random.randrange(len(tempDefList))]
        randDef = desc_dict[i][randClass]
        print('{}:\n Random Class: {} \n Definition: {}\n'.format(i, randClass, randDef))

######
# Concept extraction
######

def IUPAC_goldbook_loader(mute = True
                          ):
    """
    Loads the json-file from the IUPAC Goldbook located at ./ontologies/goldbook_vocab.json
    and returns it as dictionary
    Parameters
    ----------
    mute:  if true, no console output is printed, when definition string in Goldbook was empty
        
    Returns
    -------
    temp_dict: containing the entries of the goldbook vocabulary for further processing.

    """
    temp_dict = {}
    with open('./ontologies/goldbook_vocab.json', encoding = "utf8") as json_file:
        dict_data = json.load(json_file)
        for entry in dict_data["entries"].keys(): 
            if dict_data["entries"][entry]["term"] != None:
                if dict_data["entries"][entry]["definition"] != None:
                    temp_dict[dict_data["entries"][entry]["term"].lower()] = dict_data["entries"][entry]["definition"]
                else:
                    if not mute:
                        print("IUPAC Goldbook - empty definition in term: {}".format(dict_data["entries"][entry]["term"]))
                    temp_dict[dict_data["entries"][entry]["term"].lower()] = "[AB] Class with same label also contained in [IUPAC-Goldbook]"
            else:
                print("empty entry: {}".format(dict_data["entries"][entry]))
    return temp_dict  

def concept_extractor(ontology_filenames = ["Allotrope_OWL"],
                      use_IUPAC_goldbook = True, 
                      min_count_list = [1],
                      preprocessed_text_pickle_name = "methanation_only_text",
                      gb_muted = True):
    """
    Loads semantic artifacts, loads text-pickle and trains w2v model with desired
    min_count(s). Outputs list of token and definitions based on min_count list and "statistics"/metrics as excel-files in subdir ./xlsx-files/
    trained word2vec models are pickled in subdir ./models/
    
    Parameters
    ----------
    ontology_filenames : List of Strings containing ["bao_complete_merged", "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"]- listing ontology names. 
    For supported names see also def_dict in function description_dicts().
        
    use_IUPAC_goldbook : BOOL, optional
        When true, the goldbook vocabulary is also considered and should be stored at ./ontologies/goldbook_vocab.json . The default is True.
    min_count_list : List of integers, optional
        Lists min_count parameters to be considered by the function. The default is [1], such that a min_count of 1 is applied.
        Using e.g. [1,5] conducts the experiments first with min_count = 1 and then with min_count = 5
    preprocessed_text_pickle_name : String, optional
        Used to load the pickle containing the preprocessed (tokenized) text, as input for word2vec, the model pickle should be put in the subdir ./pickle/ . The default is "methanation_only_text".
    gb_muted: Bool, optional
        when set true, console output from IUPAC_goldbook_loader() is supressed

    Returns
    -------
    concept_dict: dictionary containing all common labels of text data and ontologies respective to min_counts.
                structure (e.g): {min_count 1:{[{Common labels:{0:'catalyst', 1:'methanation', 2:'temperature'}},{Allotrope_OWL:{0:'', 1:'', 2:'A temperature (datum) is a quantity facet that quantifies some temperature. [Allotrope]'}}]}
    statistics_dict_res: dictionary containing metrics of the runs for all different min_count params set up in input

    """
    #[class_dict, desc_dict] = onto_loader(["bao_complete_merged", "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"])
    [class_dict, desc_dict] = onto_loader(ontology_filenames)
    #min_count_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]   
    
    # LOADING IUPAC GOLDBOOK 
    if use_IUPAC_goldbook:
        desc_dict["IUPAC-Goldbook"] = IUPAC_goldbook_loader(gb_muted)
    
    # used for later output of statistics regarding extension of ontologies
    statistics_dict_res = {}
    
    # used later to return all dataframes found for different min_counts, 
    # containing the pairs of class labels and different definitions found
    concept_dict = {}
    
    # load preprocessed data from pickle
    with open('./pickle/'+preprocessed_text_pickle_name+'.pickle', 'rb') as pickle_file:
        content = pickle.load(pickle_file)

    # executed for each min_count parameter set up in list as input
    for min_count in min_count_list:
        print('Training Word2Vec with min_count = {}...'.format(min_count))
        model = create_model(content, min_count)
        name_model = preprocessed_text_pickle_name + '_mc' + str(min_count)
        model.save('./models/' + name_model)
        print('Done!')
        
        word_list = model.wv.index_to_key        
        output_file_name = "{}_conceptsMC{}_definitions".format(preprocessed_text_pickle_name,min_count)            
        df_concepts = pd.DataFrame({"Common labels" :  word_list})
        
        # allocate statistics_dict that helps to gather some "statistics"/data
        # on each set of ontology + word2vec token for later use
        statistics_dict = {}
        
        # allocate resDict, that later contains the resulting class labels and found definitions to be stored in the dataframe.
        resDict = {}
        
        # search for common entries of class labels between set of token (from word2vec) and set of ontology classes (list of class labels for each ontology)
        for loaded_onto in desc_dict:
            summary = []
            description_set =  list(desc_dict[loaded_onto].keys()) #desc_dict["ontology name"].keys() yields the respective class labels from each ontology
            for i in description_set: # comparison of labels
                try:
                    # Make sure, that no special characters are contained in class-name
                    r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
                    newlist = list(filter(r.match, word_list))
                    if newlist: # entry found
                        summary.append(newlist)
                except:
                    print("Passed due to class-name: '{}', Ontology: {}".format(i,loaded_onto))
            resDict[loaded_onto] = summary
        
        # output number of labels found for each ontology
        print("=============================================")
        print("Min_Count = {}".format(min_count))
        for key in resDict:
            print("{}: Found {} labels".format(key, len(resDict[key])))
            statistics_dict[key] = len(resDict[key])
        print("=============================================")
        
        set_1 = [iter_string.lower() for iter_string in list(word_list)]
        ## store prefLabels and definitions
        for i in resDict:
            df_concepts.insert(len(df_concepts.columns),i,'') # empty column with name of ontology
            set_2 = desc_dict[i] # set (Ontology) to compare concepts to
            candidates = list(set(set_1).intersection(set_2)) # intersection of concept_table-list and ontology
          
            # paste description of class into respective row, when no description exist, 
            # use the class name to mark concepts, which also exist in the ontology
            for j in candidates:
                if desc_dict[i][j]: # not empty
                    try:    
                        df_concepts.loc[getattr(df_concepts, "Common labels") == j, i] =  desc_dict[i][j] # changes entry in ontology column to definition, when in concepts
                    except:
                        df_concepts.loc[getattr(df_concepts, "Common labels") == j, i] = str(desc_dict[i][j])
                else:
                    df_concepts.loc[getattr(df_concepts, "Common labels") == j, i] =  j # changes entry in ontology column to definition, when in concepts
        
        #save dataframe as excel sheet
        df_concepts.to_excel('./xlsx-files/' + output_file_name + '.xlsx') 
        print("=============================================")
        print('Stored common concepts and definitions in ./xlsx-files/{}'.format(output_file_name + '.xlsx'))
        print("=============================================")
        
        # update concept_dict with entries for current min_count
        concept_dict.update({"min_count {}".format(min_count):df_concepts.to_dict()})
        
        # from here: "statistics" to store some metrics on the run such as summing up the
        # number of classes with at least 1 definition found.
        
        # replaces empty strings with NaN entries
        df_conceps_nan = df_concepts.replace(r'^\s*$', np.nan, regex=True)
        
        # count each row seperately if entry != NaN and sum up 
        sum_of_found_defs = df_conceps_nan.iloc[:,1:].count(1).astype(bool).sum(axis = 0)
        statistics_dict["sum_of_found_defs"] = int(sum_of_found_defs)
        
        statistics_dict['keys_total'] = len(word_list)
        
        statistics_dict_res[min_count] = statistics_dict
        
    """
    # if you want json file instead of excel-file - just uncomment this block
    with open("{}_concept_statistics_diffMCs.json".format(preprocessed_text_pickle_name), 'w') as f:
        json.dump(statistics_dict_res, f)
    """
    # store metrics in excel-file
    pd.DataFrame(statistics_dict_res).to_excel("./xlsx-files/{}_concept_statistics_diffMCs.xlsx".format(preprocessed_text_pickle_name))
    print("=============================================")
    print("Stored metrics for all min_count paramters in ./xlsx-files/{}_concept_statistics_diffMCs.xlsx".format(preprocessed_text_pickle_name))
    print("=============================================")
    
    return concept_dict,statistics_dict_res

"""
AB HIER WEITER
"""

def ontology_class_extender(ontology_filenames = ["SBO"], 
                            use_IUPAC_goldbook = True,
                            extend_ontology_name = 'Allotrope_OWL',
                            min_count_list = [1],
                            preprocessed_text_pickle_name = "methanation_only_text",
                            similarity_threshold_list = [0.999],
                            mute_prints = True): 
    """
    Extends "extend_ontology_name" by classes and relations and stores the modified ontologies in subdir "./ontologies_output/".
    Loads semantic artifacts and text-pickle to train w2v model with desired min_counts outputs list of token and definitions based on min_count list. 
    Returns metrics as excel-file and dict.
    WARNING: only works, if ontology to be extended has "prefLabel" annotation for labels!
             some (easy) code changes might be needed in function "ontology_class_extender" 
             to adapt to other ontologies. search for comment "#change here, if prefLabel is not correct for ontology to be extended"
             if other than prefLabel is desired
             
    
    Parameters
    ----------
    ontology_filenames : LIST
        DESCRIPTION. The default is ["SBO"].
    use_IUPAC_goldbook : BOOL
        DESCRIPTION. The default is True.
    extend_ontology_name : STR
        DESCRIPTION. The default is 'Allotrope_OWL'.
    min_count_list : LIST of INT
        DESCRIPTION. The default is [1].
    preprocessed_text_pickle_name : STR
        DESCRIPTION. The default is "methanation_only_text".
    similarity_threshold_list : LIST of FLOAT, optional
        DESCRIPTION. The default is [0.999].
    mute_prints : BOOL, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    metrics_dict : DICT
        DESCRIPTION.

    """
    # WARNING: only works, if ontology to be extended has "prefLabel" annotation for labels!
    #          some (easy) code changes might be needed in function "ontology_class_extender" 
    #          to adapt to other ontologies. search for comment "#change here, if prefLabel is not correct for ontology to be extended"
    #          if other than prefLabel is desired
    # parameters:
    #model_name_list = ['methanation_only_text_mc1','methanation_only_text_mc5',
    #                   'methanation_only_text_mc10','methanation_only_text_mc25']    
    #min_count_list = range(1,26)
    print("=============================================")
    print("WARNING: 'ontology_class_extender' only works, if ontology to be extended has 'prefLabel' annotation for labels! Some (easy) code changes might be needed in function to adapt to other ontologies")
    print("=============================================")
    
    # 
    model_name_list = [preprocessed_text_pickle_name + '_mc' + str(i) for i in min_count_list]
    
    # Allocation of lists used for "statistics"/metrics
    modelname_metrics_list = []
    sim_list = []
    new_classes_list = []
    unique_list = []
    model_token_number = []
    unique_len_all_concepts_found = []
    onto_resulting_filenames = []
    #
    
    # Load Definitions and classlabels from ontologies in ontology_filenames
    [class_dict, desc_dict] = onto_loader(ontology_filenames)
    #
    
    # LOADING IUPAC GOLDBOOK 
    if use_IUPAC_goldbook:
        desc_dict["IUPAC-Goldbook"] = IUPAC_goldbook_loader(mute_prints)
    #
    
    # loop through each model name, provided in the model_name_list and through each similarity threshold
    # to extend the ontology "extend_ontology_name" by classes and relations based on different min_counts, sim_thresholds
    for model_name in model_name_list:
        for similarity_threshold in similarity_threshold_list:
           
            # loading ontology from local file to extend
            Onto_World = owlready2.World()
            onto_local = Onto_World.get_ontology('./ontologies/' + extend_ontology_name + '.owl').load()
            
            # load word2vec model
            model_test = Word2Vec.load('./models/' + model_name)
            conceptList = model_test.wv.index_to_key
            
            # get all the preferred labels of the ontology:
            count = 0
            class_list = []
            for i in list(onto_local.classes()):
                try: 
                    class_list.append(i.prefLabel[0])
                except:
                    #print('class not included:{}'.format(i))
                    count += 1
                    pass
            #print('Not able to include {} classes due to missing label'.format(count))
            
            # allocate resultDictionary (only gets important, when more than 1 ontology is loaded)
            resDict = {}
            
            # for unique classes:
            w2v_all_concepts_found = []
            
            # for loaded_onto in desc_dict:
            summary = []
            #description_set =  list(desc_dict[loaded_onto].keys())
            
            for i in class_list: # comparison of labels
                try:
                    r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
                    newlist = list(filter(r.match, conceptList))
                    if newlist: # entry found
                        summary.append(newlist)
                except:
                    if not mute_prints:
                        print("Passed '{}', Ontology: {}".format(i,extend_ontology_name))
            resDict[extend_ontology_name] = summary
            
            # List of classes in vectorspace and 
            # current selected ontology (onto_local) = resDict[extend_ontology_name]
            # dump found classes in json file for later checkup, metrics, etc.
            with open('./json-files/FoundClasses_'+ extend_ontology_name +'_' + model_name +'_' +str(similarity_threshold) + '.json', 'w') as jsonfile:
                json.dump(resDict, jsonfile)
                
            ## 
            # Extension of ontology with classes
            # start with definining superclass "w2vConcept" that gathers all automatically added classes 
            # and conceptually_related_to as suggested semantic relationship between classes
            ##
            with onto_local:
                class w2vConcept(Thing):
                    prefLabel = 'w2vConcept'#change here, if prefLabel is not correct for ontology to be extended
                    definition = 'A concept generated automatically by [AB] to gather all concepts added by word2vec'
                class conceptually_related_to(ObjectProperty):
                    prefLabel = 'conceptually related to'#change here, if prefLabel is not correct for ontology to be extended
                    definition = 'Created automatically by [AB] to specify relations of concepts to newly introduced concepts by word-vector similarity.'
                    python_name = "conceptRelTo"
                    
            for concept in resDict[extend_ontology_name]:
                # iterates through classes of resDict and temp_class = class of the 
                # ontology_name ontology with same label of concept
            
                ## LABEL OR PREFLABEL ? Important setting, when using different ontologies for extension!
                ## label or prefLabel
                temp_class = onto_local.search_one(prefLabel = concept[0]) #change here, if prefLabel is not correct for ontology to be extended
                tuple_similarities = model_test.wv.most_similar(positive = concept[0], topn = 5)
                new_classes = []
                
                for i in range(len(tuple_similarities)):
                    if tuple_similarities[i][1] > similarity_threshold:
                        new_classes.append(tuple_similarities[i][0])
                
                w2v_all_concepts_found.extend(new_classes)
                
                # create new classes, and pose relation "conceptually related to" 
                with onto_local:
                    for i in new_classes: # create new class 
                        ## check, if class already exists?
                        #existing_class = onto_local.search_one(prefLabel = i)
                        if onto_local.search_one(prefLabel = i):#change here, if prefLabel is not correct for ontology to be extended
                            ## LABEL OR PREFLABEL
                            new_class = onto_local.search_one(prefLabel = i)#change here, if prefLabel is not correct for ontology to be extended
                            #new_class.conceptually_related_to = [temp_class]
                            new_class.is_a.append(conceptually_related_to.some(temp_class))
                        else:
                            # label i not yet included in Ontology:    
                            # assign new class i as subclass of temp_class:    
                            # new_class = types.new_class(i, (temp_class,))
                            new_class = types.new_class(i,(w2vConcept,) )
                            new_class.comment.append('Created automatically by [AB] based on word2vec output of concept name "{}"'.format(concept[0]))
                            #new_class.conceptually_related_to = [temp_class]
                            new_class.is_a.append(conceptually_related_to.some(temp_class))                       

            # count the subclasses of w2vConcept for later metrics, these are all classes newly created and inserted to the ontology
            # i.e. the classes the ontology was extended with
            different_class_count = len(list(onto_local.w2vConcept.subclasses()))
            
            # extend ontologies with definition strings from other ontologies/goldbook
            for w2vConceptClass in list(onto_local.w2vConcept.subclasses()):
                for ontology_names in desc_dict:
                    classlabel = w2vConceptClass.name
                    try:
                        defstring = ''.join(desc_dict[ontology_names][classlabel]) if desc_dict[ontology_names][classlabel] != classlabel else "" 
                    except:
                        defstring = 1
                        pass
                    
                    if defstring == 1:
                        pass
                    else:
                        if defstring:
                            comment_string = defstring + "\nFound by [AB] in [" + ontology_names + "]"
                            if not mute_prints:
                                print("def of {} found in ontology {}".format(classlabel, ontology_names))
                        else:
                            comment_string = "[AB] Class with same label also contained in [{}] unable to obtain definition".format(ontology_names)
                    
                    w2vConceptClass.comment.append(comment_string)

            onto_savestring = './ontologies_output/' + extend_ontology_name + '_ext_' + model_name + '_' + str(similarity_threshold) + '.owl'
            onto_local.save(file = onto_savestring)  
            
            
            print("=============================================")
            print("model_name = {} \n similarity_threshold = {}".format(model_name,similarity_threshold))
            print('Added {} new classes based on word2vec model {}. \nFile saved as {}.'.format(different_class_count,model_name, onto_savestring))
            
            with open('./json-files/FoundClasses_'+ extend_ontology_name +'_' + model_name +'_' +str(similarity_threshold) + '.json', 'r') as f:
                data = json.load(f)
            
            unique_dict = {}
            for keys in data.keys():
                for i in data[keys]:
                    temp = dict.fromkeys(i,"")
                    unique_dict.update(temp)    
            
            print("Unique keys added to ontology:", len(dict.fromkeys(w2v_all_concepts_found)))# len(unique_dict.keys()))
            print("=============================================")  
            modelname_metrics_list.append(model_name) # gives the name of the word2vec Model used to obtain class candidates
            sim_list.append(similarity_threshold) # lists the applied cosine-similarity threshold
            new_classes_list.append(different_class_count) # Amount of new classes added to the ontology as subclass of w2vConcept
            unique_list.append(len(dict.fromkeys(w2v_all_concepts_found))) # amount of unique concepts generated by word2vec (as 2 words might have the same concept in their w2v output, unique concept counts each word only once)
            unique_len_all_concepts_found.append(len(w2v_all_concepts_found)) # amount of classes suggested by w2v. 
            model_token_number.append(len(conceptList)) # overall amount of token contained in the word2vec model
            onto_resulting_filenames.append(onto_savestring) # Lists the path and name of the modified ontology
            
            Onto_World = None
            onto_local = None
            
    metrics_dict = {'filenames':onto_resulting_filenames,'min_count': modelname_metrics_list,'similarity_threshold':sim_list,'new_classes':new_classes_list,'unique_keys':unique_list, 'model_token_number':model_token_number, 'unique_len_all_concepts_found':unique_len_all_concepts_found}
    
    print("=============================================")  
    df = pd.DataFrame(metrics_dict)
    df.to_excel("./xlsx-files/Metrics_Ontology_class_extension_{}.xlsx".format(preprocessed_text_pickle_name))
    print("Stored Metrics of ontology class extension in ./xlsx-files/Metrics_Ontology_class_extension_{}.xlsx".format(preprocessed_text_pickle_name))
    print("=============================================")  
    
    return metrics_dict


##
# Annotates classes in extended ontology with definitions
# 
# AB HIER WEITER
##
    
def ontology_class_annotator(ontology_files_to_extend = ["./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc1_0.999"],
                            ontology_filenames = ["Allotrope_OWL"],
                            use_IUPAC_goldbook = True,
                            provenance_string = "AB",
                            mute_prints = True):
    
    json_filenames = []
    
    for ontology_filename in files_to_extend:
        
        local_world = owlready2.World()
        onto_local = local_world.get_ontology(ontology_filename + ".owl").load()
        
        # list_classes will contain all the subclasses of w2vConcept: these are 
        # the classes automatically introduced by Word2Vec, that were not already 
        # contained in the extended ontology
        list_classes = list(onto_local.get_children_of(onto_local.w2vConcept))
        
        # instert labels
        for i_1, i_2 in enumerate(list_classes):
            if i_2.label:
                print("Something went wrong? Label for '{}' already defined".format(i_2.label[0]))
            else:
                list_classes[i_1].label = i_2.name.replace("_"," ").lower()
        
        onto_local.save(file = ontology_filename + "_output.owl")
        
        label_list = [i.label[0] for i in list_classes]
        labels_to_classes_dict = {i.label[0] : i for i in list_classes}

        [class_dict, desc_dict] = onto_loader(ontology_filenames)
        
        
        # LOADING IUPAC GOLDBOOK 
        if use_IUPAC_goldbook:
           desc_dict["IUPAC-Goldbook"] = IUPAC_goldbook_loader(mute_prints)
        #
        
        resDict = {}
        for loaded_onto in desc_dict:
            summary = []
            description_set =  list(desc_dict[loaded_onto].keys())
            for i in description_set: # comparison of labels
                try:
                    r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
                    newlist = list(filter(r.match, label_list))
                    if newlist: # entry found
                        summary.append(newlist)
                except:
                    if not mute_prints:
                        print("Passed '{}', Ontology: {}".format(i,loaded_onto))
            resDict[loaded_onto] = summary
        
        with open('FoundClasses.json', 'w') as jsonfile:
            json.dump(resDict, jsonfile)
        
        onto_local = local_world.get_ontology(ontology_filename + "_output.owl").load()
        #class_candidates = list(onto_local.get_children_of(onto_local.w2vConcept))
        #class_dict_locOntos = {i.name : i for i in class_candidates}
        with onto_local:
            for loaded_onto in resDict:
                for classlabel in resDict[loaded_onto]: # list of classes        
                    defstring = ''.join(desc_dict[loaded_onto][classlabel[0]]) if desc_dict[loaded_onto][classlabel[0]] != classlabel[0] else "" 
                    if defstring:
                        comment_string = defstring + "\nFound by ["+ provenance_string +"] in [" + loaded_onto + "]"
                        if not mute_prints:
                            print("def of {} found in ontology {}".format(classlabel[0], loaded_onto))
                    else:
                        comment_string = "["+provenance_string+"] Class with same label also contained in [{}] unable to obtain definition string".format(loaded_onto)
                    
                    onto_local.search_one(label = classlabel[0]).comment.append(comment_string)
                    #class_dict_locOntos[classlabel[0]].comment.append(comment_string)    
                    #w2v_class.comment.append(comment_string)
            
            w2vSubclasses = len(set(list(onto_local.w2vConcept.subclasses())))
            onto_local.save(file = ontology_filename + "_output.owl")
        
        # List found concepts and make set of unique ones
        tempVar = []
        for key in resDict:
            for i in resDict[key]: tempVar.append(i[0])    
        found_concepts = set(tempVar)
        resDict["unique_keys"] = len(found_concepts)
        resDict["new_classes"] = w2vSubclasses
        with open("./json-files/"+ ontology_filename + "_new_classes.json", 'w') as f:
                json.dump(resDict, f)
        
        json_filenames.append("./json-files/"+ ontology_filename + "_new_classes.json")
    
    ## Export metrics of extended ontologies
    
    metrics_dict = {}
    
    for filename in json_filenames:
        with open(filename, 'r') as f:
            data = json.load(f)
        tempdict = {}
        for key in data:
            if key == 'unique_keys' or key == 'new_classes':
                tempdict[key] = data[key]
            else:
                tempdict[key] = len(data[key])
        
        metrics_dict[filename] = tempdict
        
    df = pd.DataFrame(metrics_dict)
    print("=============================================")
    
    df.to_excel("./xlsx-files/Metrics_{}_annotation_unique_keys.xlsx".format(provenance_string))
    print("Stored metrics for all min_count paramters in ./xlsx-files/Metrics_{}_annotation_unique_keys.xlsx".format(provenance_string))
    print("=============================================")
    
    return metrics_dict