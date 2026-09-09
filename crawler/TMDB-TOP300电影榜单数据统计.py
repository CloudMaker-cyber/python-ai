# -*- coding: utf-8 -*-
"""TMDB TOP300 电影榜单数据统计。

读取 csv_data/movie_list.csv，用 2x2 子图绘制四张统计图并保存：
  左上 每年电影数量折线图
  右上 不同语言电影数量柱状图
  左下 不同类型电影数量柱状图（一部电影可能有多个类型）
  右下 不同评分电影数量占比饼状图（占比过小的评分合并为"其他"）
"""

import os

import pandas as pd
import matplotlib.pyplot as plt

# 用 SimHei 显示中文，并正常显示坐标轴负号
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 以本文件所在目录为基准，保证从任何工作目录运行都能找到 csv_data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'csv_data', 'movie_list.csv')
SAVE_PATH = os.path.join(BASE_DIR, 'csv_data', 'TMDB-top300电影榜单数据统计.png')

USECOLS = ['电影名', '年份', '上映时间', '类型', '时长', '评分', '语言']


def load_data(csv_path: str = CSV_PATH) -> pd.DataFrame:
    """读取 CSV 中需要的列；年份可能为空，用支持空值的 Int64 类型。"""
    return pd.read_csv(csv_path, usecols=USECOLS, dtype={'年份': 'Int64'})


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """数据清洗：补全年份缺失，修正语言列的脏数据。"""
    # 1. 年份缺失的行，用上映时间的前 4 位（年份）补全
    df['年份'] = df['年份'].fillna(df['上映时间'].str[:4])

    # 2. 识别语言列的脏数据：金额污染（$开头）、缺失占位符（-）
    money_mask = df['语言'].astype(str).str.startswith('$')
    dash_mask = df['语言'] == '-'

    # 3. 手动修正金额污染的电影语言
    fix_map = {
        '火遮眼': '粤语',
        '哪吒之魔童闹海': '国语',
        'Top Gun: Maverick': '英语',
    }
    for name, lang in fix_map.items():
        df.loc[df['电影名'] == name, '语言'] = lang

    # 4. 缺失占位符归为"未知"，英文名 Cantonese 统一为中文"粤语"
    df.loc[dash_mask, '语言'] = '未知'
    df.loc[df['语言'] == 'Cantonese', '语言'] = '粤语'
    return df


def plot_year_trend(ax, df: pd.DataFrame) -> None:
    """折线图：统计每年上映的电影数量。"""
    year_count = df.groupby('年份')['年份'].count()

    min_year = year_count.index.min()
    max_year = year_count.index.max()
    x = list(range(min_year, max_year + 1))
    y = [year_count.get(i, 0) for i in x]  # 没有电影的年份补 0

    ax.plot(x, y)
    ax.set_xlabel('年份')
    ax.set_ylabel('电影数量')
    ax.set_title('每年电影数量统计')
    ax.set_xticks(x[::8])           # 横轴刻度太密，隔 8 年显示一个
    ax.set_yticks(range(0, 31, 3))
    ax.grid(linestyle='--', alpha=0.3)


def plot_language_bar(ax, df: pd.DataFrame) -> None:
    """柱状图：统计不同语言（清洗后）的电影数量。"""
    language_count = df.groupby('语言')['语言'].count().sort_values(ascending=False)

    ax.bar(language_count.index, language_count.values)
    ax.set_xlabel('语言')
    ax.set_ylabel('电影数量')
    ax.set_title('不同语言电影数量统计')
    ax.tick_params(axis='x', rotation=90)   # 语言标签多，竖排避免重叠
    ax.grid(linestyle='--', alpha=0.3)


def plot_type_bar(ax, df: pd.DataFrame) -> None:
    """柱状图：统计不同类型电影数量（一部电影可能有多个类型）。"""
    type_count = {}
    for types in df['类型'].dropna().str.split(','):
        for movie_type in types:
            type_count[movie_type] = type_count.get(movie_type, 0) + 1
    type_count = dict(sorted(type_count.items(), key=lambda item: item[1], reverse=True))

    ax.bar(type_count.keys(), type_count.values())
    ax.set_xlabel('类型')
    ax.set_ylabel('电影数量')
    ax.set_title('不同类型电影数量统计')
    ax.tick_params(axis='x', rotation=90)
    ax.grid(linestyle='--', alpha=0.3)


def plot_score_pie(ax, df: pd.DataFrame) -> None:
    """饼状图：展示不同评分电影数量占比，占比过小的评分合并为"其他"。"""
    scores_count = df.groupby('评分')['评分'].count()

    # 单个评分占比 <= 2% 时数量太少，合并到"其他"避免饼图标签拥挤
    total = scores_count.sum()
    large_scores: pd.Series = scores_count[scores_count > total * 0.02]
    small_scores: pd.Series = scores_count[scores_count <= total * 0.02]
    large_scores['其他'] = small_scores.sum()

    scores = large_scores.index.tolist()
    counts = large_scores.values.tolist()

    patches, texts, autotexts = ax.pie(counts, labels=scores, autopct='%1.1f%%')
    for autotext in autotexts:      # autotexts 才是百分数文本，单独设颜色、字号
        autotext.set_color('black')
        autotext.set_fontsize(10)

    ax.set_title('不同评分电影数量占比')
    ax.legend(scores, loc='upper center', ncol=5, bbox_to_anchor=(0.5, 0))


def main() -> None:
    df = load_data()
    df = clean_data(df)

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
    fig.suptitle('TMDB-top300电影榜单数据统计', fontsize=16, fontweight='bold')
    fig.subplots_adjust(hspace=0.4, wspace=0.2)

    plot_year_trend(axes[0, 0], df)
    plot_language_bar(axes[0, 1], df)
    plot_type_bar(axes[1, 0], df)
    plot_score_pie(axes[1, 1], df)

    plt.savefig(SAVE_PATH)
    plt.show()


if __name__ == '__main__':
    main()
