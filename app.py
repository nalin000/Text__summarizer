from flask import Flask, request, jsonify, render_template
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# Summarization function (same as before)
def your_summarization_function(text):
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and token.text != '\n']
    tokens1 = []
    stopwords = list(STOP_WORDS)
    allowed_pos = ['ADJ', 'PROPN', 'VERB', 'NOUN']
    for token in doc:
        if token.text in stopwords or token.text in punctuation:
            continue
        if token.pos_ in allowed_pos:
            tokens1.append(token.text)

    word_freq = Counter(tokens)
    max_freq = max(word_freq.values())

    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq

    sent_token = [sent.text for sent in doc.sents]
    sent_score = {}
    for sent in sent_token:
        for word in sent.split():
            if word.lower() in word_freq.keys():
                if sent not in sent_score.keys():
                    sent_score[sent] = word_freq[word.lower()]
                else:
                    sent_score[sent] += word_freq[word.lower()]

    num_sentences = 4
    n = nlargest(num_sentences, sent_score, key=sent_score.get)
    summary = " ".join(n)
    return summary

# Serve HTML page at the root URL
@app.route('/')
def index():
    return render_template('index.html')

# Route for summarization
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    summary = your_summarization_function(text)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
