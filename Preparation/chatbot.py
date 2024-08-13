import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.load(open('../model/intents.json'))

words = pickle.load(open('../model/words.pkl', 'rb'))
classes = pickle.load(open('../model/classes.pkl', 'rb'))
model = load_model('../model/chatbot_model.keras')


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for word in sentence_words:
        if word in words:
            bag[words.index(word)] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.2  # Experiment with this value

    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)

    return_list = []

    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    # Handle cases where no intent is confidently predicted
    if len(return_list) == 0:
        return [{'intent': 'no_match', 'probability': '0'}]  # Adjust this based on your needs

    return return_list


def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


while True:
    message = input('You: ')
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(f"Chatty: {res}")
