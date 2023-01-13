"""
Created on Fri Jan 13 12:42:25 2023

@author: A. S. Behr
@affiliation: TU Dortmund University
@comment: Functions and code described in paper "Ontology Extension by NLP-based 
Concept Extraction for Domain Experts in Catalytic Sciences" by A. S. Behr,
M. Völkenrath, N. Kockmann

"""

import glob2
import pickle
import spacy

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO
from gensim.models import Word2Vec


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


