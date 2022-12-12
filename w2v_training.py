from gensim.models import Word2Vec
def create_model(preprocessed_data, minc):

    model = Word2Vec(preprocessed_data, vector_size=300, alpha=0.025, min_count=minc)

    return model
