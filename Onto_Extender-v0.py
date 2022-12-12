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

from owlready2 import *
import LocalOntologies
import OntoClassSearcher
import re
import json
import types

from gensim.models import Word2Vec


# parameters:
model_name = 'methanation_only_text_mc10'
onto_name = 'Allotrope_OWL'
similarity_threshold = 0.999
##

# loading ontology from local file 
[class_dict, desc_dict] = OntoClassSearcher.onto_loader([onto_name])
Onto_World = owlready2.World()
onto_local = Onto_World.get_ontology('./ontologies/' + onto_name + '.owl').load()
class_list = (onto_local.classes())


##
#   conceptList = Liste mit Konzepten aus MC = 10, die auch in AFO drin sind?
##

model_test = Word2Vec.load('./models/' + model_name)

conceptList = model_test.wv.index_to_key

resDict = {}
for loaded_onto in desc_dict:
    summary = []
    description_set =  list(desc_dict[loaded_onto].keys())
    for i in description_set: # comparison of labels
        try:
            r = re.compile(str("[a-zA-Z0-9]*^" + i + "$"),re.IGNORECASE)
            newlist = list(filter(r.match, conceptList))
            if newlist: # entry found
                summary.append(newlist)
        except:
            print("Passed '{}', Ontology: {}".format(i,loaded_onto))
    resDict[loaded_onto] = summary

with open('FoundClasses' + model_name + '.json', 'w') as jsonfile:
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

    temp_class = onto_local.search_one(prefLabel = concept[0])
    tuple_similarities = model_test.wv.most_similar(positive = concept[0], topn = 5)
    # new_classes = [tuple_similarities[i][0] for i in range(len(tuple_similarities))]
    new_classes = []
    
    for i in range(len(tuple_similarities)):
        if tuple_similarities[i][1] > similarity_threshold:
            new_classes.append(tuple_similarities[i][0])
    
    with onto_local:
        for i in new_classes: # create new class 
            ## check, if class already exists?
            #existing_class = onto_local.search_one(prefLabel = i)
            if onto_local.search_one(prefLabel = i):
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
                
onto_savestring = './' + onto_name + '_ext_' + model_name + '.owl'
onto_local.save(file = onto_savestring)  

print("=============================================")
print('Added {} new classes based on word2vec model {}. \nFile saved as {}.'.format(different_class_count,model_name, onto_savestring))

  
    
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
  
