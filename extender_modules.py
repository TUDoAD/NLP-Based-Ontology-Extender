"""
Created on Fri Jan 13 12:42:25 2023

@author: A. S. Behr
@affiliation: TU Dortmund University
@comment: Functions and code described in paper "Ontology Extension by NLP-based 
Concept Extraction for Domain Experts in Catalytic Sciences" by A. S. Behr,
M. Völkenrath, N. Kockmann

"""

# imports for preprocessing functions:
import glob2
import pickle
import spacy

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO
from gensim.models import Word2Vec

# imports for ontology related functions:
import pandas as pd
import random
import re 

from owlready2 import *
from tqdm import tqdm
import numpy as np
import pickle

## 
# textmining - used for retrieval of text data from pdfs stored in ./import/
# subdir. 
# Preprocessed text containing only noun and propnoun token stored in 
# pickle with name "name" in subdir ./pickle/.
# Raw read-in text stored as pickle "name_raw" in subdir ./pickle/.
##
def textmining(name):
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

##
# extract content from pdf file, returns text as string
##
def get_pdf_file_content(pdf_file):
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

##
# uses glob2 package to retrieve all .pdf files stored in subdir ./import/
##
def get_globed_content():
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

##
# used to store data as pickle in subdir ./pickle/
##
def save_pickle(pdf_data, pickle_name):
    with open('./pickle/' + pickle_name + '.pickle', 'wb') as handle:
        pickle.dump(pdf_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

##
# used to read stored pickle data from subdir ./pickle/
##
def load_pickle(pickle_name):
    with open('./pickle/' + pickle_name + '.pickle', 'rb') as handle:
        data_open = pickle.load(handle)
    return data_open

##
# Trains word2vec model based on preprocessed_data (lists of token)
# and based on minc = min_count parameter, which limits the amount of 
# minimal repetitions a token has to have in the text dataset.
# Outputs respective word2vec model
##
def create_model(preprocessed_data, minc):

    model = Word2Vec(preprocessed_data, vector_size=300, alpha=0.025, min_count=minc)

    return model

##
# function that tests if a token is important for POS-tagging 
# here, only NOUN and PROPNOUN tokens are considered.
##
def is_relevant(token):
    # NOUN - nouns; PROPN - proper noun; VERB - verbs; ADJ - adjective; NUM - number; PUNCT - punctuation
    pos_tags = ['NOUN', 'PROPN']
    if token.pos_ in pos_tags:
        return True
    else:
        return False

##
# function that tests if a token is important by comparison to waste list
##
def is_datawaste(token):
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

##
# preprocesses extracted text data, returns tokenized list of words acc. to
# token classes specified in function is_relevant(token).
##
def preprocessing(pdf_data):
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

##
# loads an ontology from subfolder ontologies defined by its name 
# outputs list of classes contained in this ontology  
##
def load_ontologies(onto_name):
    new_world = owlready2.World()
    onto = new_world.get_ontology("./ontologies/{}.owl".format(onto_name)).load()
    onto_class_list = list(new_world.classes())
    print("Loading {} done. Imported {} classes.".format(onto_name, len(onto_class_list)))
    return onto_class_list 


## 
# definition error used in function description_dicts to return string,
# when class definition strings could not be extracted properly
## 
class definitionError(Exception):
    pass
    
##
# extracts class names and descriptions based on class list (as owlready2 object)
# returns dictionary with general structure of 
# desc_dict = {ontology_class_label : Definition string}
# WARNING: Descriptions often have different identifiers (see try:... except loop)
#          Implemented IAO_0000115 and .comment for now. 
##
def description_dicts(class_list, onto_name):
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
        def_id = def_dict[onto_name]
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


##    
# Loading ontologies
# and storing classes and their descriptions in dictionaries
##
def onto_loader(onto_names):        

    # Ontologies to load
    # onto_names = ["chmo","Allotrope_OWL", "chebi", "NCIT", "SBO"]
    class_list_dict = {}
    description_list_dict ={}
        
    for name in onto_names:
        print("Loading ontology {} ...".format(name))
        class_list_dict[name] = load_ontologies(name)
        description_list_dict[name] = description_dicts(class_list_dict[name],name)
    
    # existing_keys = names of ontologies
    existing_keys = list(description_list_dict.keys())
        
    print("Ontologies {} loaded. \n PLEASE CHECK if class descriptions are not empty.".format(str(onto_names)))
    print("=============================================")
    return class_list_dict, description_list_dict

##
# Find same entries of class names in both concept_table and ontologies
# load Excel-File with name file_name and store list with all concepts, 
# and their definitions (if any) as new_file_name Excel-file.
##
def onto_class_comparison(desc_list_dict, file_name, new_file_name):
    # names of ontologies within desc_list_dict
    onto_names = list(desc_list_dict.keys())
    concept_table = pd.read_excel(file_name + '.xlsx')
    
    set_1 = [iter_string.lower() for iter_string in list(concept_table[0])]

    df_concepts = pd.DataFrame({file_name : set_1})
    
    for i in range(len(onto_names)):
        df_concepts.insert(len(df_concepts.columns),onto_names[i],'') # empty column with name of ontology
        set_2 = desc_list_dict[onto_names[i]] # set (Ontology) to compare concepts to
        candidates = list(set(set_1).intersection(set_2)) # intersection of concept_table-list and ontology
        print("Found {}/{} common concept names for Ontology {} and rawdata".format(len(candidates),len(set_1),onto_names[i]))      
        # paste description of class into respective row, when no description exist, 
        # use the class name to mark concepts, which also exist in the ontology
        for j in candidates:
            if desc_list_dict[onto_names[i]][j]: # not empty
                try:    
                    df_concepts.loc[getattr(df_concepts, file_name) == j, onto_names[i]] =  desc_list_dict[onto_names[i]][j] # changes entry in ontology column to definition, when in concepts
                except:
                    df_concepts.loc[getattr(df_concepts, file_name) == j, onto_names[i]] = str(desc_list_dict[onto_names[i]][j])
            else:
                df_concepts.loc[getattr(df_concepts, file_name) == j, onto_names[i]] =  j # changes entry in ontology column to definition, when in concepts    
    #save dataframe as excel sheet
    df_concepts.to_excel(new_file_name + '.xlsx') 
    print('Stored common concepts and definitions in {}'.format(new_file_name + '.xlsx'))
    return df_concepts

##
# searches for a random class in each ontology of desc_dict and 
# outputs its definition. Imports package random.
##
def definition_sampler(desc_dict):
    onto_list = list(desc_dict.keys())
    for i in onto_list:
        tempDefList = list(desc_dict[i].keys())
        randClass = tempDefList[random.randrange(len(tempDefList))]
        randDef = desc_dict[i][randClass]
        print('{}:\n Random Class: {} \n Definition: {}\n'.format(i, randClass, randDef))
#####################################
#              Example              #
#####################################
'''
# execute once to load all ontologies from list 
[class_dict, desc_dict] = onto_loader(["chmo","Allotrope_OWL", "chebi"])

# execute to compare CFI_test.xlsx with loaded ontologies, store resulting 
# Dataframe in CFI_comConcepts.xlsx

onto_class_comparison(desc_dict, 'CFI_test', 'CFI_comConcepts')
# onto_class_comparison(desc_dict, 'CFI_Concepts', 'CFI_Concepts_compared')
'''

######
# Concept extraction
######

##
# ConceptExtractor_methanation_diffMCs
# Loads semantic artifacts, loads text-pickle and trains w2v model with desired
# min_counts outputs list of token and definitions based on min_count list as excel-file
##
def ConceptExtractor_methanation_diffMCs():
    [class_dict, desc_dict] = onto_loader(["bao_complete_merged", "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"])
    
    ## LOADING IUPAC GOLDBOOK 
    temp_dict = {}
    with open('./ontologies/goldbook_vocab.json', encoding = "utf8") as json_file:
        dict_data = json.load(json_file)
        for entry in dict_data["entries"].keys(): 
            if dict_data["entries"][entry]["term"] != None:
                if dict_data["entries"][entry]["definition"] != None:
                    temp_dict[dict_data["entries"][entry]["term"].lower()] = dict_data["entries"][entry]["definition"]
                else:
                    print("IUPAC Goldbook - empty definition in term: {}".format(dict_data["entries"][entry]["term"]))
                    temp_dict[dict_data["entries"][entry]["term"].lower()] = "[AB] Class with same label also contained in [IUPAC-Goldbook]"
            else:
                print("empty entry: {}".format(dict_data["entries"][entry]))
    desc_dict["IUPAC-Goldbook"] = temp_dict
    
    
    statistics_dict_res = {}
    
    
    with open('./pickle/methanation_only_text.pickle', 'rb') as pickle_file:
        content = pickle.load(pickle_file)
        
    min_count_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,50,100]
    #min_count_list = [1,5,10,25,50,100]
    
    
    for min_count in min_count_list:
        print('Training Word2Vec with mincount = {}...'.format(min_count))
        model = create_model(content, min_count)
        name_model = 'methanation_only_text' + '_mc' + str(min_count)
        model.save('./models/' + name_model)
        print('Done!')
    
        word_list = model.wv.index_to_key
    
        #file_name = "methanation_mc10_searched"
        output_file_name = "conceptsMC{}_definitions".format(min_count)
        #df_concepts = pd.read_excel(file_name + '.xlsx')
        #df_concepts.drop(df_concepts.columns.difference([file_name + '.xlsx','methanation_mc10_prep']),1,inplace =True)
        
        df_concepts = pd.DataFrame({"MC {}".format(min_count) :  word_list})
        
        #word_list = list(df_concepts['methanation_mc10_prep'])
        
        statistics_dict = {}
        resDict = {}
        for loaded_onto in desc_dict:
            summary = []
            description_set =  list(desc_dict[loaded_onto].keys())
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
        
        ## output number of labels found for each ontology
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
            # print("Found {}/{} common concept names for Ontology {} and rawdata".format(len(candidates),len(set_1),onto_names[i]))
          
            # paste description of class into respective row, when no description exist, 
            # use the class name to mark concepts, which also exist in the ontology
            for j in candidates:
                if desc_dict[i][j]: # not empty
                    try:    
                        df_concepts.loc[getattr(df_concepts, "MC {}".format(min_count)) == j, i] =  desc_dict[i][j] # changes entry in ontology column to definition, when in concepts
                    except:
                        df_concepts.loc[getattr(df_concepts, "MC {}".format(min_count)) == j, i] = str(desc_dict[i][j])
                else:
                    df_concepts.loc[getattr(df_concepts, "MC {}".format(min_count)) == j, i] =  j # changes entry in ontology column to definition, when in concepts
        
        #save dataframe as excel sheet
        df_concepts.to_excel('./xlsx-files/' + output_file_name + '.xlsx') 
        print('Stored common concepts and definitions in ./xlsx-files/{}'.format(output_file_name + '.xlsx'))
        
        # replaces empty strings with NaN entries
        df_conceps_nan = df_concepts.replace(r'^\s*$', np.nan, regex=True)
        
        # count each row seperately if entry != NaN and sum up 
        sum_of_found_defs = df_conceps_nan.iloc[:,1:].count(1).astype(bool).sum(axis = 0)
        statistics_dict["sum_of_found_defs"] = int(sum_of_found_defs)
        
        statistics_dict['keys_total'] = len(word_list)
        
        statistics_dict_res[min_count] = statistics_dict
        
    """
    with open('concept_statistics_diffMCs.json', 'w') as f:
        json.dump(statistics_dict_res, f)
    """
    pd.DataFrame(statistics_dict_res).to_excel("./xlsx-files/concept_statistics_diffMCs.xlsx")
    print('Stored statistics for each loop in ./xlsx-files/concept_statistics_diffMCs.xlsx')
        