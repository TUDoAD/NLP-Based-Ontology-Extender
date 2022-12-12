from gensim.models import Word2Vec


def calculate(data, model, name):
    # calculating accuracy:
    # how many hypernyms was found for leaves (words out of model),
    # how many data points (node&leaves) are named,
    # which words got no hypernym
    print('Accuracy for ' + str(name))
    # how many hypernyms was found for W2V model and for which is ny hypernym found
    num_leaves = 0
    list_not_found_1 = []

    for i in model.wv.index_to_key:
        for j in range(len(data)):
            if data[1][j] == i and data['hypernym'][j] != 'No common hypernym found!':
                num_leaves += 1
            elif data[1][j] == i and data['hypernym'][j] == 'No common hypernym found!':
                list_not_found_1.append(i)
    print('A hypernyms was found for ' + str(num_leaves) + ' out of ' + str(len(model.wv.index_to_key))
          + ' words out of Word2Vec model!')

    # counting for how many nodes and leaves an hypernym
    num_not = 0
    for i in range(len(data)):
        if data[1][i] == 'No common hypernym found!':
            num_not += 1
    num_hyp = len(data[0]) - num_not
    print('A value is set for ' + str(num_hyp) + ' out of ' + str(len(data[0])) + ' nodes and leaves!')

    # creating a list with words for which no hypernym was found
    list_not_found_2 = []
    for i in range(len(data)):
        if data['hypernym'][i] == 'No common hypernym found!' and data[1][i] != 'No common hypernym found!':
            list_not_found_2.append(data[1][i])

    list_not_found = [list_not_found_1, list_not_found_2]
    return list_not_found
