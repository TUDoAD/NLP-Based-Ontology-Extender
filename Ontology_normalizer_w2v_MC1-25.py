# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 13:35:02 2022

@author: Alexander Behr 
"""

##
# Annotates classes in extended ontology with definitions
##


from owlready2 import *
import LocalOntologies
import OntoClassSearcher
import re
import json



ontology_filename_list = ["./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc1_0.999","./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc2_0.999","./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc5_0.999","./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc10_0.999","./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc25_0.999",
                          "./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc10_0.99","./ontologies_output/Allotrope_OWL_ext_methanation_only_text_mc10_0.995"]

for ontology_filename in ontology_filename_list:
    
    local_world = owlready2.World()
    onto_local = local_world.get_ontology(ontology_filename + ".owl").load()
    list_classes = list(onto_local.get_children_of(onto_local.w2vConcept))
    
    # Labels einfügen
    for i_1, i_2 in enumerate(list_classes):
        if i_2.label:
            print("Label zu '{}' bereits definiert".format(i_2.label[0]))
        else:
            list_classes[i_1].label = i_2.name.replace("_"," ").lower()
    
    onto_local.save(file = ontology_filename + "_output.owl")
    
    
    
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
    
    onto_local = local_world.get_ontology(ontology_filename + "_output.owl").load()
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
        
        w2vSubclasses = len(set(list(onto_local.w2vConcept.subclasses())))
        onto_local.save(file = ontology_filename + "_output.owl")
        
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
    
    # Found concepts (unique)
    tempVar = []
    for key in resDict:
        for i in resDict[key]: tempVar.append(i[0])    
    found_concepts = set(tempVar)
    resDict["unique_keys"] = len(found_concepts)
    resDict["new_classes"] = w2vSubclasses
    with open(ontology_filename + "_new_classes.json", 'w') as f:
            json.dump(resDict, f)
    #andereVariableTest = list_classes[5]
    # andereVariableTest.name
    # .title()
    
import json
import pandas as pd

json_filenames = ["mc1_0.999_new_classes.json",
"mc10_0.995_new_classes.json",
"mc10_0.99_new_classes.json",
"mc25_0.999_new_classes.json",
"mc10_0.999_new_classes.json",
"mc5_0.999_new_classes.json",
"mc2_0.999_new_classes.json"]

df_dict = {}

for filename in json_filenames:
    with open('./ontologies_output/Allotrope_OWL_ext_methanation_only_text_'+filename, 'r') as f:
        data = json.load(f)
    tempdict = {}
    for key in data:
        if key == 'unique_keys' or key == 'new_classes':
            tempdict[key] = data[key]
        else:
            tempdict[key] = len(data[key])
    
    df_dict[filename] = tempdict
    
df = pd.DataFrame(df_dict)
df.to_excel('Auswertung_Onto_extension_defCounts.xlsx')
