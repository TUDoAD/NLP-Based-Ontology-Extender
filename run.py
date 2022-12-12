import sys

import result
import jparsing
import data_save
import clustering
import pdf_globing
import w2v_training
import xlsx_postprocessing
import data_preprocessing_spacy


def textmining(name, mincount):
    # function which calls every needed script
    # set a higher max recursion limit
    max_rec = sys.getrecursionlimit()
    sys.setrecursionlimit(100000)

    name_raw = name + "_raw"

    # extracting text out of PDF files and save string
    print('Extracting text of PDF...')
    data_raw = pdf_globing.get_globed_content()
    data_save.save_pickle(data_raw, name_raw)
    print('Done!')

    # preprocessing text and save string
    print('Preprocessing text...')
    data_prep = data_preprocessing_spacy.preprocessing(data_raw)
    data_save.save_pickle(data_prep, name)
    print('Done!')

    # training Word2Vec model, clustering and creating first json-file
    print('Training Word2Vec...')
    model = w2v_training.create_model(data_prep, mincount)
    name_model = name + '_mc' + str(mincount)
    model.save('./models/' + name_model)
    print('Done!')

    # clustering data and create a json file
    print('Clustering Data and creating a json-file...')
    clustering.w2v_to_json(model, name_model)
    print('Done!')

    # extract hypernyms
    print('Extracting hypernyms...')
    df = jparsing.parsing(name_model)
    print('Done!')

    # calculate accuracy
    print('Calculate accuracy...')
    result_lists = result.calculate(df, model, name)
    print('Done!')

    # creating xlsx file
    xlsx_postprocessing.postprocessing(df, name)

    # reset recursion limit
    sys.setrecursionlimit(max_rec)
    return result_lists, df


'''

from gensim.models import Word2Vec

model_test = Word2Vec.load("./models/Talha_Mod_mc1")

a = model_test.wv.index_to_key

import pandas as pd

df = pd.DataFrame(a)

df.to_excel('Concept_list_CFI_MOD.xlsx')

'''