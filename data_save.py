import pickle


def save_pickle(pdf_data, pickle_name):
    with open('./pickle/' + pickle_name + '.pickle', 'wb') as handle:
        pickle.dump(pdf_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(pickle_name):
    with open('./pickle/' + pickle_name + '.pickle', 'rb') as handle:
        data_open = pickle.load(handle)
    return data_open
