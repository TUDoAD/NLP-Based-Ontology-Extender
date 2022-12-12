import json
import rec_hyp_extraction
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
g = []


def recursion(v, prefix=''):
    # goes recursive through the json-data and returns a list with all values (names)
    if isinstance(v, dict):
        for k, v2 in v.items():
            p2 = "{}['{}']".format(prefix, k)
            recursion(v2, p2)  # recursive call
    elif isinstance(v, list):
        for i, v2 in enumerate(v):
            p2 = "{}[{}]".format(prefix, i)
            recursion(v2, p2)  # recursive call
    else:
        g.append(['{}'.format(prefix), v])

    return g


def parsing(name):
    j_file = open('./json-files/' + name + '.json', 'r')
    j_data = json.load(j_file)
    j_file.close()
    # calling recursion and convert its output into dataframe
    rec = recursion(j_data)
    df = pd.DataFrame.from_dict(rec)

    # creating a column for hypernyms and hypernym path and set a name for Root1
    df['hyp_path'] = ""
    for i in range(len(df[0])):
        df['hyp_path'][i] = df[0][i][:-23]
    df['hypernym'] = ""
    df['hypernym'][-2:] = 'First Node'
    df['hypernym'][-1:] = 'Root1'

    # calling get_hypernyms
    rec_hyp_extraction.recursive_hypernyms(df)

    # entering terms of new df into JSON file
    for i in range(len(df[0])):
        j_file = open('./json-files/' + name + '.json', 'w')
        if df[1][i] != 'No common hypernym found!':
            path = df[0][i]
            value = df[1][i]

            exec("j_data" + path + "=" + "value")
            json.dump(j_data, j_file)
        j_file.close()

    return df
