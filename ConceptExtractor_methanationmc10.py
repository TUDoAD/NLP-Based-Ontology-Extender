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

#[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["chmo","Allotrope_OWL"])#, "chebi"])
[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["chmo","Allotrope_OWL", "chebi", "NCIT", "bao_complete_merged", "SBO"])

file_name = "methanation_mc10_searched"
new_file_name = "conceptsMC10_test"
df_concepts = pd.read_excel(file_name + '.xlsx')
df_concepts.drop(df_concepts.columns.difference([file_name + '.xlsx','methanation_mc10_prep']),1,inplace =True)
word_list = list(df_concepts['methanation_mc10_prep'])
found_classes = []

## LOADING IUPAC GOLDBOOK 
temp_dict = {}
with open('./ontologies/goldbook_vocab.json', encoding = "utf8") as json_file:
    dict_data = json.load(json_file)
    for entry in dict_data["entries"].keys():
        if dict_data["entries"][entry]["term"] != None:
            if dict_data["entries"][entry]["definition"] != None:
                temp_dict[dict_data["entries"][entry]["term"].lower()] = dict_data["entries"][entry]["definition"]
            else:
                print("empty definition for term: {}".format(dict_data["entries"][entry]["term"]))
                temp_dict[dict_data["entries"][entry]["term"].lower()] = "[AB] Class with same label also contained in [IUPAC-Goldbook]"
        else:
            print("empty entry: {}".format(dict_data["entries"][entry]))
desc_dict["IUPAC-Goldbook"] = temp_dict

resDict = {}
for loaded_onto in desc_dict:
    summary = []
    description_set =  list(desc_dict[loaded_onto].keys())
    for i in description_set: # comparison of labels
        try:
            r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
            newlist = list(filter(r.match, word_list))
            if newlist: # entry found
                summary.append(newlist)
        except:
            print("Passed '{}', Ontology: {}".format(i,loaded_onto))
    resDict[loaded_onto] = summary

## output number of labels found for each ontology
print("=============================================")
for key in resDict:
    print("{}: Found {} labels".format(key, len(resDict[key])))
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
                df_concepts.loc[getattr(df_concepts, "methanation_mc10_prep") == j, i] =  desc_dict[i][j] # changes entry in ontology column to definition, when in concepts
            except:
                df_concepts.loc[getattr(df_concepts, "methanation_mc10_prep") == j, i] = str(desc_dict[i][j])
        else:
            df_concepts.loc[getattr(df_concepts, "methanation_mc10_prep") == j, i] =  j # changes entry in ontology column to definition, when in concepts

#save dataframe as excel sheet
df_concepts.to_excel(new_file_name + '.xlsx') 
print('Stored common concepts and definitions in {}'.format(new_file_name + '.xlsx'))


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