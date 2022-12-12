# import sys #
import data_save # 
import pdf_globing # 
import w2v_training #
import data_preprocessing_spacy #


def textmining(name, mincount):
    # function which calls every needed script
    # set a higher max recursion limit
    #    max_rec = sys.getrecursionlimit()
    #    sys.setrecursionlimit(100000)

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
    #print('Training Word2Vec...')
    #model = w2v_training.create_model(data_prep, mincount)
    #name_model = name + '_mc' + str(mincount)
    #model.save('./models/' + name_model)
    #print('Done!')



textmining("methanation_mc1",10)