# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 09:23:25 2022

@author: Alexander Behr
"""
##
# Gets all words from a trained Word2Vec model and searches them in an existing
# ontology. Existing classes in the ontologies then get -based on the Word2Vec
# model the top X words assigned as children of the existing class.
##

## ToDo: Danach vllt. noch ein Check, wie viele der ursprünglichen Keys jetzt 
#        in der Ontologie gelandet sind?

## ToDo: neu erzeugte Klassen prüfen auf 4 Ontologien und Definition-Strings 
#        erzeugen 


from owlready2 import *
import LocalOntologies
import OntoClassSearcher
import re
import json
import types
import pandas as pd

from gensim.models import Word2Vec


# parameters:
#model_name_list = ['methanation_only_text_mc1','methanation_only_text_mc5',
#                   'methanation_only_text_mc10','methanation_only_text_mc25']    
mc_list = range(1,26)
#mc_list = range(5,11)
model_name_list = ['methanation_only_text_mc'+str(i) for i in mc_list]

#similarity_threshold_list = [0.8,0.9,0.95,0.99,0.995,0.996,0.997,0.998,0.999]
similarity_threshold_list = [0.999]#,0.9995,1]

#model_name = 'methanation_only_text_mc1'
#model_name = 'methanation_only_text_mc10'
#model_name = 'methanation_only_text_mc5'
#model_name = 'methanation_only_text_mc25'
#onto_name = 'ManalsHierarchyOutput_withDefinitions'
onto_name = 'Allotrope_OWL'
# similarity_threshold = 0.99


## Allocation of lists used for statistics
modelname_list = []
sim_list = []
new_classes_list = []
unique_list = []
model_token_number = []
unique_len_all_concepts_found = []
##

## Load Definitions
[class_dict, desc_dict] = OntoClassSearcher.onto_loader(["chmo", "chebi", "NCIT", "bao_complete_merged", "SBO"])


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




##
for model_name in model_name_list:
    for similarity_threshold in similarity_threshold_list:
       
        # loading ontology from local file 
        #[class_dict, desc_dict] = OntoClassSearcher.onto_loader([onto_name])
        Onto_World = owlready2.World()
        onto_local = Onto_World.get_ontology('./ontologies/' + onto_name + '.owl').load()
        
        # load word2vec model
        model_test = Word2Vec.load('./models/' + model_name)
        conceptList = model_test.wv.index_to_key
        
        # get all the preferred labels of the ontology:
        count = 0
        
        class_list = []
        for i in list(onto_local.classes()):
            try: 
                class_list.append(i.prefLabel[0])
            except:
                #print('class not included:{}'.format(i))
                count += 1
                pass
        #print('Not able to include {} classes due to missing label'.format(count))
        ##
        #   conceptList = Liste mit Konzepten aus MC = 10, die auch in AFO drin sind?
        ##
        
        # allocate resultDictionary (only gets important, when more than 1 ontology is loaded)
        resDict = {}
        
        # for unique classes:
        w2v_all_concepts_found = []
        
        # for loaded_onto in desc_dict:
        summary = []
        #description_set =  list(desc_dict[loaded_onto].keys())
        
        for i in class_list: # comparison of labels
            try:
                r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
                newlist = list(filter(r.match, conceptList))
                if newlist: # entry found
                    summary.append(newlist)
            except:
                print("Passed '{}', Ontology: {}".format(i,onto_name))
        resDict[onto_name] = summary
        
        with open('./json-files/FoundClasses' + model_name + str(similarity_threshold) + '.json', 'w') as jsonfile:
            json.dump(resDict, jsonfile)
            
        # List of classes in Vectorspace and 
        # current selected ontology (onto_local) = resDict[onto_name]
        
        with onto_local:
            class w2vConcept(Thing):
                prefLabel = 'w2vConcept'
                definition = 'A concept generated automatically by [AB] to gather all concepts added by word2vec'
            class conceptually_related_to(ObjectProperty):
                prefLabel = 'conceptually related to'
                definition = 'Created automatically by [AB] to specify relations of concepts to newly introduced concepts by word-vector similarity.'
                python_name = "conceptRelTo"
                
        for concept in resDict[onto_name]:
            # iterates through classes of resDict and temp_class = class of the 
            # onto_name ontology with same label of concept
        
            ## LABEL OR PREFLABEL
            ## label or prefLabel
            temp_class = onto_local.search_one(prefLabel = concept[0]) 
            tuple_similarities = model_test.wv.most_similar(positive = concept[0], topn = 5)
            # new_classes = [tuple_similarities[i][0] for i in range(len(tuple_similarities))]
            new_classes = []
            
            for i in range(len(tuple_similarities)):
                if tuple_similarities[i][1] > similarity_threshold:
                    new_classes.append(tuple_similarities[i][0])
            
            w2v_all_concepts_found.extend(new_classes)
            
            with onto_local:
                for i in new_classes: # create new class 
                    ## check, if class already exists?
                    #existing_class = onto_local.search_one(prefLabel = i)
                    if onto_local.search_one(prefLabel = i):
                        ## LABEL OR PREFLABEL
                        new_class = onto_local.search_one(prefLabel = i)
                        #new_class.conceptually_related_to = [temp_class]
                        new_class.is_a.append(conceptually_related_to.some(temp_class))
                    else:
                        # label i not yet included in Ontology:    
                        # assign new class i as subclass of temp_class:    
                        # new_class = types.new_class(i, (temp_class,))
                        new_class = types.new_class(i,(w2vConcept,) )
                        new_class.comment.append('Created automatically by [AB] based on word2vec output of concept name "{}"'.format(concept[0]))
                        #new_class.conceptually_related_to = [temp_class]
                        new_class.is_a.append(conceptually_related_to.some(temp_class))                       
                        
                        
        different_class_count = len(list(onto_local.w2vConcept.subclasses()))
        
        for w2vConceptClass in list(onto_local.w2vConcept.subclasses()):
            for onto_names in desc_dict:
                classlabel = w2vConceptClass.name
                try:
                    defstring = ''.join(desc_dict[onto_names][classlabel]) if desc_dict[onto_names][classlabel] != classlabel else "" 
                except:
                    defstring = 1
                    pass
                
                if defstring == 1:
                    pass
                else:
                    if defstring:
                        comment_string = defstring + "\nFound by [AB] in [" + onto_names + "]"
                        print("def of {} found in ontology {}".format(classlabel, onto_names))
                    else:
                        comment_string = "[AB] Class with same label also contained in [{}] unable to obtain definition".format(onto_names)
                
                w2vConceptClass.comment.append(comment_string)
        
        
        
        onto_savestring = './ontologies_output/' + onto_name + '_ext_' + model_name + '_' + str(similarity_threshold) + '.owl'
        onto_local.save(file = onto_savestring)  
        
        print("=============================================")
        print("model_name = {} \n similarity_threshold = {}".format(model_name,similarity_threshold))
        print('Added {} new classes based on word2vec model {}. \nFile saved as {}.'.format(different_class_count,model_name, onto_savestring))
        
        with open('./json-files/FoundClasses' + model_name + str(similarity_threshold) + '.json', 'r') as f:
            data = json.load(f)
        
        unique_dict = {}
        for keys in data.keys():
            for i in data[keys]:
                temp = dict.fromkeys(i,"")
                unique_dict.update(temp)    
        
        print("Unique keys added to ontology:", len(dict.fromkeys(w2v_all_concepts_found)))# len(unique_dict.keys()))
        print("=============================================")  
        modelname_list.append(model_name) # gives the name of the word2vec Model used to obtain class candidates
        sim_list.append(similarity_threshold) # lists the applied cosine-similarity threshold
        new_classes_list.append(different_class_count) # Amount of new classes added to the ontology as subclass of w2vConcept
        unique_list.append(len(dict.fromkeys(w2v_all_concepts_found))) # amount of unique concepts generated by word2vec (as 2 words might have the same concept in their w2v output, unique concept counts each word only once)
        unique_len_all_concepts_found.append(len(w2v_all_concepts_found)) # amount of classes suggested by w2v. 
        model_token_number.append(len(conceptList)) # overall amount of token contained in the word2vec model
        
        Onto_World = None
        onto_local = None
        
output_dict = {'min_count': modelname_list,'similarity_threshold':sim_list,'new_classes':new_classes_list,'unique_keys':unique_list, 'model_token_number':model_token_number, 'unique_len_all_concepts_found':unique_len_all_concepts_found}

df = pd.DataFrame(output_dict)
df.to_excel('Auswertung_versch_MC_und_Thresholds.xlsx')


'''
model_test.wv.similar_by_word('reactor')
Out[78]: 
[('bed', 0.9994844198226929),
 ('outlet', 0.9993471503257751),
 ('tube', 0.999320924282074),
 ('inlet', 0.9993012547492981),
 ('heat', 0.9992453455924988),
 ('temperature', 0.999235987663269),
 ('salt', 0.9992288947105408),
 ('ﬂow', 0.9992184638977051),
 ('pressure', 0.9992129802703857),
 ('feed', 0.9991992712020874)]

model_test.wv.similar_by_word('bed')
Out[79]: 
[('reactor', 0.9994844794273376),
 ('salt', 0.9994573593139648),
 ('parameter', 0.9994072318077087),
 ('tube', 0.999401330947876),
 ('time', 0.9993911385536194),
 ('temperature', 0.9993727803230286),
 ('coolant', 0.9993698000907898),
 ('drop', 0.999361515045166),
 ('mass', 0.9993523955345154),
 ('pressure', 0.9993463754653931)]

model_test.wv.similar_by_word('outlet')
Out[80]: 
[('inlet', 0.9996315836906433),
 ('feed', 0.9995215535163879),
 ('pressure', 0.9994890689849854),
 ('temperature', 0.999485194683075),
 ('gas', 0.9994626045227051),
 ('rate', 0.9994502663612366),
 ('composition', 0.999421238899231),
 ('flow', 0.9994135499000549),
 ('concentration', 0.9993895292282104),
 ('ﬂow', 0.9993889331817627)]
'''
  
