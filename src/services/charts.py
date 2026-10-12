"""График по результатам анализа."""

import matplotlib
matplotlib.use('Agg')  # режим без окна, чтобы график можно было сохранить на сервере
import matplotlib.pyplot as plt


def make_chart(result: dict, filename: str) -> None:
    """Рисует столбчатую диаграмму самых частотных лемм и сохраняет её в файл"""
    lemmas = []
    counts = []
    for lemma, count in result['top_lemmas']:
        lemmas.append(lemma)
        counts.append(count)

    #  разворачиваем списки, чтобы самая частотная лемма была сверху
    lemmas.reverse()
    counts.reverse()

    plt.figure(figsize=(8, 5))
    plt.barh(lemmas, counts, color='purple')
    plt.title('Самые частотные леммы')
    plt.xlabel('Сколько раз встретилась')
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
