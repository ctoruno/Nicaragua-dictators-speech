#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 16:01:19 2022

@author: carlostorunopaniagua
"""

import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from collections import Counter
from gensim.corpora.dictionary import Dictionary
from gensim import models

# Importing data
master_data = pd.read_csv("Data/master.csv")

# Tokenizing speeches
speeches = list(master_data["speech"]) 
tokenized_sps = [[token for token in tk_speech 
                  # Removing stopwords and punctuation 
                  if token.isalpha() and token not in stopwords.words("spanish")] 
                         # Tokenizing individual speeches
                         for tk_speech in [word_tokenize(speech.lower()) 
                                for speech in speeches]]

# Counter(tokenized_sps).most_common(5)

# Bigrams and Trigrams
bigram_phrases = models.Phrases(tokenized_sps, min_count = 5, threshold = 20)
trigram_phrases = models.Phrases(bigram_phrases[tokenized_sps], threshold = 20)

bigram = models.phrases.Phraser(bigram_phrases)
trigram = models.phrases.Phraser(trigram_phrases)

def make_bigrams(texts):
    return[bigram[doc] for doc in texts]

def make_trigrams(texts):
    return[trigram[bigram[doc]] for doc in texts]

data_bigrams = make_bigrams(tokenized_sps)
data_bigrams_trigrams = make_trigrams(data_bigrams)

print (data_bigrams_trigrams[3][0:25])


# TF-IDF Removal
id2word = Dictionary(data_bigrams_trigrams)
gcorpus = [id2word.doc2bow(tkdoc) for tkdoc in data_bigrams_trigrams]

tfidf = models.TfidfModel(gcorpus, id2word = id2word)

#Filter low value words and also words missing in tfidf models.
low_value = 0.025

for i in range(0, len(gcorpus)):
    bow = gcorpus[i]
    low_value_words = [] #reinitialize to be safe. You can skip this.
    tfidf_ids = [id for id, value in tfidf[bow]]
    bow_ids = [id for id, value in bow]
    low_value_words = [id for id, value in tfidf[bow] if value < low_value]
    words_missing_in_tfidf = [id for id in bow_ids if id not in tfidf_ids] # The words with tf-idf socre 0 will be missing

    new_bow = [b for b in bow if b[0] not in low_value_words and b[0] not in words_missing_in_tfidf]  

#reassign        
gcorpus[i] = new_bow

# Creating a gensim corpus
dictionary = Dictionary(tokenized_sps)
gcorpus = [dictionary.doc2bow(doc) for doc in tokenized_sps]

# LDA model
LDA_model = models.ldamodel.LdaModel(corpus = gcorpus,
                                     id2word = dictionary,
                                     num_topics = 8,
                                     random_state = 100,
                                     update_every = 1,
                                     chunksize = 100,
                                     passes = 10,
                                     alpha = "auto")
