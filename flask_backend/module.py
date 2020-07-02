import json 
from CocCocTokenizer import PyTokenizer
import re

with open('template.json') as file:
    data = json.load(file)
    questions = data['questions']
    answers = data['answers']


def clean_data(text):
    text = text.lower()
    text = re.sub('[^a-zA-Zàáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹýđ]+', ' ', text)
    return text

def tokenzie(text):
    text = clean_data(text)
    T = PyTokenizer(load_nontone_data=True)
    token_array = T.word_tokenize(text, tokenize_option=0)
    return token_array

def remove_stopword(text):
    stop_words = [line.rstrip('\n') for line in open('./stop_word.txt')]
    text_removed = []
    for i in range(len(text)):
        if text[i] not in stop_words:
            text_removed.append(text[i])
    return text_removed

def get_key_word(token_array):
    words = remove_stopword(token_array)
    for i in range(len(words)):
        words[i] = words[i].replace('_', ' ')
    return words

def get_answer(text):
    token_array = tokenzie(text)

    key_words = get_key_word(token_array)

    score_similar = {}
    for question in questions:
        score_similar[question['id']] = 0

    for question in questions:
        for key_word in key_words: 
            if key_word in question['question']:
                score_similar[question['id']] += 1

    max_key = max(score_similar, key=score_similar.get)
    

    if score_similar[max_key] < 1:
        return None

    for question in questions:
        if question['id'] == max_key:
            answer_id = question['answer_id']
    
    for answer in answers:
        if answer['id'] == answer_id:
            return answer['answer']
    
    return None