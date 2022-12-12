# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 13:35:02 2022

@author: Alexander Behr 
"""

#TODO:
"""
IUPAC GOLDBOOK NOCH IMPLEMENTIEREN!
-> Dazu json zu desc_dict umbauen?

REGULAR EXPRESSIONS anschauen
https://docs.python.org/3/library/re.html#regular-expression-syntax

"""


from owlready2 import *
import LocalOntologies
import OntoClassSearcher
import re
import json


local_world = owlready2.World()
onto_local = local_world.get_ontology("./Allotrope_OWL_ext_methanation_only_text_mc10.owl").load()
list_classes = list(onto_local.get_children_of(onto_local.w2vConcept))

# Labels einfügen
for i_1, i_2 in enumerate(list_classes):
    if i_2.label:
        print("Label zu '{}' bereits definiert".format(i_2.label[0]))
    else:
        list_classes[i_1].label = i_2.name.replace("_"," ").lower()

onto_local.save(file = "./Allotrope_OWL_ext_methanation_only_text_mc10_output.owl")



######

label_list = [i.label[0] for i in list_classes]

labels_to_classes_dict = {i.label[0] : i for i in list_classes}

[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["chmo","Allotrope_OWL", "chebi", "NCIT", "bao_complete_merged", "SBO"])


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
            newlist = list(filter(r.match, label_list))
            if newlist: # entry found
                summary.append(newlist)
        except:
            print("Passed '{}', Ontology: {}".format(i,loaded_onto))
    resDict[loaded_onto] = summary
## in rdfs:seeAlso oder so schreiben, dass mapping zu Ontologie XX und Klasse YY möglich ist, tagging mit [AB] oder so?
with open('FoundClasses.json', 'w') as jsonfile:
    json.dump(resDict, jsonfile)

onto_local = local_world.get_ontology("./Allotrope_OWL_ext_methanation_only_text_mc10_output.owl").load()
#class_candidates = list(onto_local.get_children_of(onto_local.w2vConcept))
#class_dict_locOntos = {i.name : i for i in class_candidates}
with onto_local:
    for loaded_onto in resDict:
        for classlabel in resDict[loaded_onto]: # list of classes        
            defstring = ''.join(desc_dict[loaded_onto][classlabel[0]]) if desc_dict[loaded_onto][classlabel[0]] != classlabel[0] else "" 
            if defstring:
                comment_string = defstring + "\nFound by [AB] in [" + loaded_onto + "]"
                print("def of {} found in ontology {}".format(classlabel[0], loaded_onto))
            else:
                comment_string = "[AB] Class with same label also contained in [{}] unable to obtain definition".format(loaded_onto)
            
            onto_local.search_one(label = classlabel[0]).comment.append(comment_string)
            #class_dict_locOntos[classlabel[0]].comment.append(comment_string)    
            #w2v_class.comment.append(comment_string)
'''
## storing definitions in ontology
for loaded_onto in resDict:
    for concept in resDict[loaded_onto]:
        temp_class = labels_to_classes_dict[concept[0]]
        # defstring should contain definition contained in desc_dict but only 
        # IF the definition is not equal to the label
        # if the definition is equal to the label -> no definition was contained in ontology
        if loaded_onto == "IUPAC-Goldbook":
            defstring = ''.join(desc_dict[loaded_onto][concept[0]]) if desc_dict[loaded_onto][concept[0]] != concept[0] else "" 
        else:            
            defstring = ''.join(desc_dict[loaded_onto][concept[0]]) if desc_dict[loaded_onto][concept[0]] != concept[0] else "" 
        
        if defstring:
            comment_string =  defstring + "\nFound by [AB] in [" + loaded_onto + "]"
        else:
            comment_string = "[AB] Class with same label also contained in [{}]".format(loaded_onto)
       #print("{}: {}\n".format(concept[0],comment_string))
        temp_class.comment.append(comment_string)
'''

onto_local.save(file = "./Allotrope_OWL_ext_methanation_only_text_mc10_output_.owl")


# Found concepts (unique)
tempVar = []
for key in resDict:
    for i in resDict[key]: tempVar.append(i[0])    
found_concepts = set(tempVar)
#andereVariableTest = list_classes[5]
# andereVariableTest.name
# .title()