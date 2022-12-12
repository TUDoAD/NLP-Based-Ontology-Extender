# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 13:43:11 2022

@author: User
"""
"""
from owlready2 import *

onto_name = 'Allotrope_OWL'
Onto_World = owlready2.World()
onto_local = Onto_World.get_ontology('./ontologies/' + onto_name + '.owl').load()


with onto_local:
    class Test('reactor'):
        pass
    
    
onto_local.save(file = './testtest.owl') 
onto_local.search_one(prefLabel = 'vector double datum')

wordlist = ['reactor', model_test.wv.similar_by_word('reactor')[0][0], model_test.wv.similar_by_word('reactor')[0][0]]


'''
PICKLES
'''

## Create Pickle
import pickle
  
# Create a variable
myvar = [{'This': 'is', 'Example': 2}, 'of',
         'serialisation', ['using', 'pickle']]
  
# Open a file and use dump()
with open('file.pkl', 'wb') as file:
      
    # A new file will be created
    pickle.dump(myvar, file)
    
## Load Pickle
    
import pickle
  
# Open the file in binary mode
with open('file.pkl', 'rb') as file:
      
    # Call load method to deserialze
    myvar = pickle.load(file)
  
    print(myvar)
    
"""
"""
import json
with open('FoundClasses.json', 'r') as f:
    data = json.load(f)

for key in data:
    print("{}: {} classes found".format(key,len(data[key])))

unique_dict = {}
for keys in data.keys():
    for i in data[keys]:
        temp = dict.fromkeys(i,"")
        unique_dict.update(temp)    

print("unique keys: ", len(unique_dict.keys()))
"""

"""
import pickle
import w2v_training 

with open('./pickle/methanation_only_text.pickle', 'rb') as pickle_file:
    content = pickle.load(pickle_file)
    
min_count = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
for i in min_count:
    print('Training Word2Vec with mincount = {}...'.format(i))
    model = w2v_training.create_model(content, i)
    name_model = 'methanation_only_text' + '_mc' + str(i)
    model.save('./models/' + name_model)
    print('Done!')

conceptList = model.wv.index_to_key
"""
"""
import plotly
import numpy as np
import plotly.graph_objs as go
from sklearn.decomposition import PCA
import pickle
import w2v_training 
from gensim.models import Word2Vec

def display_pca_scatterplot_3D(model, user_input=None, words=None, label=None, color_map=None, topn=10, sample=250):
## Code adapted from: https://towardsdatascience.com/visualizing-word-embedding-with-pca-and-t-sne-961a692509f5
    if words == None:
        if sample > 0:
            words = np.random.choice(list(model.wv.index_to_key), sample)
        else:
            words = [ word for word in model.wv.index_to_key ]
    
    word_vectors = model.wv.vectors # np.array([model[w] for w in words])
    
    three_dim = PCA(random_state=0).fit_transform(word_vectors)[:,:3]
    # For 2D, change the three_dim variable into something like two_dim like the following:
    # two_dim = PCA(random_state=0).fit_transform(word_vectors)[:,:2]

    data = []
    count = 0
    
    for i in range (len(user_input)):

                trace = go.Scatter3d(
                    x = three_dim[count:count+topn,0], 
                    y = three_dim[count:count+topn,1],  
                    z = three_dim[count:count+topn,2],
                    text = words[count:count+topn],
                    name = user_input[i],
                    textposition = "top center",
                    textfont_size = 20,
                    mode = 'markers+text',
                    marker = {
                        'size': 10,
                        'opacity': 0.8,
                        'color': 2
                    }
       
                )
                
                # For 2D, instead of using go.Scatter3d, we need to use go.Scatter and delete the z variable. Also, instead of using
                # variable three_dim, use the variable that we have declared earlier (e.g two_dim)
            
                data.append(trace)
                count = count+topn

    trace_input = go.Scatter3d(
                    x = three_dim[count:,0], 
                    y = three_dim[count:,1],  
                    z = three_dim[count:,2],
                    text = words[count:],
                    name = 'input words',
                    textposition = "top center",
                    textfont_size = 20,
                    mode = 'markers+text',
                    marker = {
                        'size': 10,
                        'opacity': 1,
                        'color': 'black'
                    }
                    )

    # For 2D, instead of using go.Scatter3d, we need to use go.Scatter and delete the z variable.  Also, instead of using
    # variable three_dim, use the variable that we have declared earlier (e.g two_dim)
            
    data.append(trace_input)
    
# Configure the layout

    layout = go.Layout(
        margin = {'l': 0, 'r': 0, 'b': 0, 't': 0},
        showlegend=True,
        legend=dict(
        x=1,
        y=0.5,
        font=dict(
            family="Courier New",
            size=25,
            color="black"
        )),
        font = dict(
            family = " Courier New ",
            size = 15),
        autosize = False,
        width = 1000,
        height = 1000
        )


    plot_figure = go.Figure(data = data, layout = layout)
    plot_figure.show('browser')
    
model = Word2Vec.load('./models/methanation_only_text_mc10')
#sample = 10 # len(model.wv.index_to_key)

#display_pca_scatterplot_3D(model, user_input = w2v_all_concepts_found)#,user_input = ['reactor','chemical', 'methane'])#, sample = sample)#, words = ['1']) 
display_pca_scatterplot_3D(model, user_input = ['reactor','engineering','methanation'])#, similar_word, labels, color_map)
"""

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
