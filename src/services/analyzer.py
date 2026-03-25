from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from natasha import Doc, MorphVocab, NewsEmbedding, NewsNERTagger, Segmenter
from pymorphy3 import MorphAnalyzer

STOPWORDS = {
    "а", "без", "более", "бы", "был", "была", "были", "было", "быть", "в", "вам", "вас", "весь",
    "во", "вот", "все", "всего", "вы", "где", "да", "даже", "для", "до", "его", "ее", "если",
    "есть", "еще", "же", "за", "здесь", "и", "из", "или", "им", "их", "к", "как", "ко", "когда",
    "кто", "ли", "либо", "мне", "может", "мы", "на", "над", "надо", "наш", "не", "него", "нее",
    "нет", "ни", "них", "но", "ну", "о", "об", "однако", "он", "она", "они", "оно", "от", "по",
    "под", "при", "с", "со", "так", "также", "такой", "там", "те", "тем", "то", "того", "тоже",
    "той", "только", "том", "ты", "у", "уж", "уже", "хотя", "чего", "чей", "чем", "что", "чтобы",
    "эта", "эти", "это", "я",
}

TOKEN_RE = re.compile(r"[А-Яа-яЁёA-Za-z-]+")

ENTITY_LABELS = {
    "PER": "люди",
    "LOC": "места",
    "ORG": "организации",
    "DATE": "даты",
}


@dataclass(slots=True)
class Sushchnost:
    label: str
    value: str


@dataclass(slots=True)
class RezultatAnaliza:
    source_text: str
    word_count: int
    sentence_count: int
    top_lemmas: list[tuple[str, int]]
    entities: list[Sushchnost]

    @property
    def entity_counts(self) -> dict[str, int]:
        counts = Counter(entity.label for entity in self.entities)
        return {label: counts.get(label, 0) for label in ENTITY_LABELS.values() if counts.get(label, 0) > 0}


class AnalizatorTeksta:
    def __init__(self) -> None:
        self.morph = MorphAnalyzer()
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.embedding = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.embedding)

    def analiz(self, text: str) -> RezultatAnaliza:
        chistyy_tekst = self._normalize_whitespace(text)
        tokeny = self._tokenize(chistyy_tekst)
        lemmmy = self._lemmatize(tokeny)
        top_lemmy = Counter(lemmmy).most_common(10)
        sushchnosti = self._extract_entities(chistyy_tekst)
        kolvo_predlozheniy = self._count_sentences(chistyy_tekst)

        return RezultatAnaliza(
            source_text=chistyy_tekst,
            word_count=len(tokeny),
            sentence_count=kolvo_predlozheniy,
            top_lemmas=top_lemmy,
            entities=sushchnosti,
        )

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _tokenize(self, text: str) -> list[str]:
        return [token.lower() for token in TOKEN_RE.findall(text)]

    def _lemmatize(self, tokens: Iterable[str]) -> list[str]:
        lemmas: list[str] = []
        for token in tokens:
            if len(token) < 3 or token in STOPWORDS:
                continue
            parsed = self.morph.parse(token)[0]
            lemma = parsed.normal_form
            if lemma not in STOPWORDS and len(lemma) >= 3:
                lemmas.append(lemma)
        return lemmas

    def _extract_entities(self, text: str) -> list[Sushchnost]:
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_ner(self.ner_tagger)

        items: list[Sushchnost] = []
        seen: set[tuple[str, str]] = set()
        for span in doc.spans:
            span.normalize(self.morph_vocab)
            label = ENTITY_LABELS.get(span.type)
            value = (span.normal or span.text).strip()
            key = (label or "", value.lower())
            if not label or not value or key in seen:
                continue
            seen.add(key)
            items.append(Sushchnost(label=label, value=value))
        return items[:12]

    def _count_sentences(self, text: str) -> int:
        parts = [part for part in re.split(r"[.!?]+", text) if part.strip()]
        return len(parts)
