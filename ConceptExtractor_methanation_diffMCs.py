# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:19:03 2022

@author: Alexander S. Behr
"""

import owlready2
import json
import LocalOntologies
import OntoClassSearcher
import re 

import pandas as pd
import numpy as np

import pickle
import w2v_training 


#[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["chmo","Allotrope_OWL"])#, "chebi"])
[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["bao_complete_merged", "Allotrope_OWL", "chebi", "chmo", "NCIT", "SBO"])

#####
# TODO: INCLUDE FOR LOOP, that iterates through different w2v models' concept lists

# TODO: ALPHA variieren in w2v models + cluster visualisieren!
#####

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
    model = w2v_training.create_model(content, min_count)
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
    df_concepts.to_excel(output_file_name + '.xlsx') 
    print('Stored common concepts and definitions in {}'.format(output_file_name + '.xlsx'))
    
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
pd.DataFrame(statistics_dict_res).to_excel("concept_statistics_diffMCs.xlsx")


    
    
'''
OntoClassSearcher.onto_class_comparison(desc_dict, 'methanation_mc10_searched', 'methanation_mc10_searched-concepts')

for column_name in df.columns:
    Process_list = [i.strip() for i in list(df[column_name].dropna())] # strings without leading or trailing spaces, no empty cells
    
    df_output = pd.DataFrame(Process_list, columns = ["methanation_mc10_prep"]) 
    
    res_dict = {}
    
    for i in desc_dict: # each ontology key
        def_set1 = desc_dict[i]
        #for word in Process_list:
        candidates = list(set(def_set1).intersection(set(Process_list)))
        res_dict[i] = candidates
        found_classes.extend(candidates)
        
    for i in res_dict: # keys (=Ontology names)
        hit_list = [None] * len(Process_list) 
        for num, line in enumerate(Process_list,0):
            if list(set([line]).intersection(set(res_dict[i]))):
                hit_list[num] = desc_dict[i][line][0]
               
        df_output[i] = hit_list
    df_output.to_excel("./Classes_"+column_name.strip().replace("/","")+".xlsx")
    
found_df = pd.DataFrame(found_classes, columns = ["PrefLabels"])
hit_list = [None] * len(found_df) 
for j in desc_dict: # ontology name
    for num, line in enumerate(found_classes,0): # class name
        if list(set([line]).intersection(set(desc_dict[j]))):
            hit_list[num] = desc_dict[j][line][0]
    
    found_df[j] = hit_list
found_df.drop_duplicates(subset = "PrefLabels").to_excel("./condensed.xlsx")    
'''