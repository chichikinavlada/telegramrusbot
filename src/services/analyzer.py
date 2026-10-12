"""Анализ русского учебного текста: слова, предложения, леммы и именованные сущности."""

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, wordpunct_tokenize
from natasha import Doc, MorphVocab, NewsEmbedding, NewsNERTagger, Segmenter
from pymorphy3 import MorphAnalyzer

# данные для nltk 
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

# модели загружаем при запуске бота
morph = MorphAnalyzer()
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)

# стоп-слова

stops = set(stopwords.words('russian') + ['это', 'весь', 'который', 'мочь', 'свой', 'являться'])

# уже разобранные слова, чтобы не вызывать pymorphy много раз для одного слова
known_words = {}

# типы сущностей в natasha и их названия для пользователя
ENTITY_NAMES = {'PER': 'люди', 'LOC': 'места', 'ORG': 'организации'}


def get_words(text: str) -> list:
    """Делит текст на слова: оставляет только токены из букв и приводит их к нижнему регистру."""
    words = []
    for token in wordpunct_tokenize(text):
        if token.isalpha():
            words.append(token.lower())
    return words


def get_lemmas(words: list) -> list:
    """Лемматизирует слова через pymorphy3 и убирает стоп-слова и очень короткие леммы."""
    lemmas = []
    for word in words:
        if word in known_words:
            lemma = known_words[word]
        else:
            lemma = morph.parse(word)[0].normal_form
            known_words[word] = lemma
        if lemma not in stops and len(lemma) > 2:
            lemmas.append(lemma)
    return lemmas


def count_sentences(text: str) -> int:
    """Считает предложения с помощью sent_tokenize из nltk."""
    return len(sent_tokenize(text, language='russian'))


def find_entities(text: str) -> dict:
    """Ищет людей, места и организации через natasha. Возвращает словарь {тип: [сущности]}."""
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    entities = {}
    for span in doc.spans:
        if span.type not in ENTITY_NAMES:
            continue
        span.normalize(morph_vocab)
        name = ENTITY_NAMES[span.type]
        value = span.normal or span.text
        if name not in entities:
            entities[name] = []
        if value not in entities[name]:
            entities[name].append(value)
    return entities


def analyze_text(text: str) -> dict:
    """Главная функция: принимает текст и возвращает словарь с результатами анализа."""
    text = text.strip()
    words = get_words(text)
    lemmas = get_lemmas(words)

    # таблица частотности лемм
    freq = pd.Series(lemmas, dtype='object').value_counts()
    top_lemmas = []
    for lemma, count in freq.head(10).items():
        top_lemmas.append((lemma, int(count)))

    return {
        'word_count': len(words),
        'sentence_count': count_sentences(text),
        'top_lemmas': top_lemmas,
        'entities': find_entities(text),
    }
