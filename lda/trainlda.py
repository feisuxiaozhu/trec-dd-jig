import logging
import gensim
from gensim.corpora import BleiCorpus
from gensim import corpora
from pymongo import MongoClient
from settings import *

class Corpus(object):
    def __init__(self, cursor, reviews_dictionary, corpus_path):
        self.cursor = cursor
        self.reviews_dictionary = reviews_dictionary
        self.corpus_path = corpus_path

    def __iter__(self):
        self.cursor.rewind()
        for review in self.cursor:
            yield self.reviews_dictionary.doc2bow(review["words"])

    def serialize(self):
        BleiCorpus.serialize(self.corpus_path, self, id2word=self.reviews_dictionary)

        return self

class Dictionary(object):
    def __init__(self, cursor, dictionary_path):
        self.cursor = cursor
        self.dictionary_path = dictionary_path

    def build(self):
        self.cursor.rewind()
        dictionary = corpora.Dictionary(review["words"] for review in self.cursor)
        dictionary.filter_extremes(keep_n=10000)
        dictionary.compactify()
        corpora.Dictionary.save(dictionary, self.dictionary_path)

        return dictionary

class Train:
    def __init__(self):
        pass

    @staticmethod
    def run(lda_model_path, corpus_path, num_topics, id2word):
        corpus = corpora.BleiCorpus(corpus_path)
        lda = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=id2word)
        lda.save(lda_model_path)

        return lda

def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    dictionary_path = "models/dictionary.dict"
    corpus_path = "models/corpus.lda-c"
    lda_num_topics = 75
    lda_model_path = "models/lda_model_50_topics.loggingda"

    corpus_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][NNS_COLLECTION]
    reviews_cursor = corpus_collection.find()

    dictionary = Dictionary(reviews_cursor, dictionary_path).build() #build dictionary from tag_corpus in data base
    Corpus(reviews_cursor, dictionary, corpus_path).serialize() #build corpus from tag_NNS_corpus and dictionary
    Train.run(lda_model_path, corpus_path, lda_num_topics, dictionary) #run lda model with corpus, dictionary

if __name__ == '__main__':
    main()