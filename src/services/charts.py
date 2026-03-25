from __future__ import annotations

from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.services.analyzer import RezultatAnaliza


def postroit_grafik(result: RezultatAnaliza) -> BytesIO:
    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
    figure.suptitle("Статистика текста", fontsize=14)

    lemma_labels = [lemma for lemma, _ in result.top_lemmas[:5]] or ["нет данных"]
    lemma_values = [count for _, count in result.top_lemmas[:5]] or [0]
    axes[0].bar(lemma_labels, lemma_values, color="#4F81BD")
    axes[0].set_title("Топ лемм")
    axes[0].tick_params(axis="x", rotation=25)

    entity_counts = result.entity_counts
    entity_labels = list(entity_counts.keys()) or ["нет сущностей"]
    entity_values = list(entity_counts.values()) or [0]
    axes[1].bar(entity_labels, entity_values, color="#C0504D")
    axes[1].set_title("Сущности")
    axes[1].tick_params(axis="x", rotation=20)

    figure.tight_layout()

    buffer = BytesIO()
    figure.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    buffer.seek(0)
    plt.close(figure)
    return buffer
