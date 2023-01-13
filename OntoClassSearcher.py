# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 18:11:14 2021

@author: Alexander Behr


TODO: 
- globbing auf input-Pfad anwenden, statt onto_names?
- in LocalOntologies.py call auf definition (IAO_0000115) variabel machen. Funktioniert bspw bei SBO.owl nicht
Klassen raussuchen, Word2Vec oder aehnliches auf Klassen anwenden.
-> je 1 Vektor/Klasse in Ontologie.
-> Vgl. der Vektoren zweier unterschiedlicher Ontologien 
-> Mapping?

"""

from owlready2 import *

import LocalOntologies
import pandas as pd
import random

def onto_loader(onto_names):        
    ##    
    # Loading ontologies
    # and storing classes and their descriptions in dictionaries
    ##
    # Ontologies to load
    # onto_names = ["chmo","Allotrope_OWL", "chebi"] # "NCIT", "SBO"]
    class_list_dict = {}
    description_list_dict ={}
        
    for name in onto_names:
        print("Loading ontology {} ...".format(name))
        class_list_dict[name] = LocalOntologies.load_ontologies(name)
        description_list_dict[name] = LocalOntologies.description_dicts(class_list_dict[name],name)
    
    # existing_keys = names of ontologies
    existing_keys = list(description_list_dict.keys())
        
    print("Ontologies {} loaded. \n PLEASE CHECK if class descriptions are not empty.".format(str(onto_names)))
    print("=============================================")
    return class_list_dict, description_list_dict

def onto_class_comparison(desc_list_dict, file_name, new_file_name):
    ##
    # Find same entries of class names in both concept_table and ontologies
    # load Excel-File with name file_name and store list with all concepts, 
    # and their definitions (if any) as new_file_name Excel-file.
    ##

    # names of ontologies within desc_list_dict
    onto_names = list(desc_list_dict.keys())

    # import concept list
    # file_name = 'CFI_test'
    # new_file_name = file_name 
    concept_table = pd.read_excel(file_name + '.xlsx')
    
    ### HERE list of concepts
    set_1 = [iter_string.lower() for iter_string in list(concept_table[0])]
    
    # allocate dataframe with concepts from excel file using file_name 
    # as title of first column
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


def definition_sampler(desc_dict):
    # searches for a random class in each ontology of desc_dict and 
    # outputs its definition. Imports random.
    
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

