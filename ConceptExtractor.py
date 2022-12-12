# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:19:03 2022

@author: Alexander S. Behr
"""

import owlready2
import LocalOntologies
import OntoClassSearcher

import pandas as pd

[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["chmo","Allotrope_OWL", "chebi"])

df = pd.read_excel("./Table draft 1.xlsx")
found_classes = []

for column_name in df.columns:
    Process_list = [i.strip() for i in list(df[column_name].dropna())] # strings without leading or trailing spaces, no empty cells
    
    df_output = pd.DataFrame(Process_list, columns = ["PrefLabels"]) 
    
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