# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 09:58:31 2021

@author: Alexander Behr
"""

from owlready2 import *
from tqdm import tqdm

class definitionError(Exception):
    pass
    

def load_ontologies(onto_name):
    # loads an ontology from subfolder ontologies defined by its name 
    # outputs list of classes contained in this ontology
    new_world = owlready2.World()
    onto = new_world.get_ontology("./ontologies/{}.owl".format(onto_name)).load()
    onto_class_list = list(new_world.classes())
    print("Loading {} done. Imported {} classes.".format(onto_name, len(onto_class_list)))
    return onto_class_list 


def description_dicts(class_list, onto_name):
    # extracts class names and descriptions based on class list (as owlready2 object)
    # WARNING: Descriptions often have different identifiers (see try:... except loop)
    #          Implemented IAO_0000115 and .comment for now. 
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