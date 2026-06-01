"""微信读书数据分析与可视化"""

import os
import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict

import jieba
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import seaborn as sns
from wordcloud import WordCloud

from config import OUTPUT_DIR

# ── 中文字体 ─────────────────────────────────────────────────────────────────
matplotlib.rcParams["axes.unicode_minus"] = False

def _setup_chinese_font():
    import matplotlib.font_manager as fm
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode MS.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            prop = fm.FontProperties(fname=p)
            matplotlib.rcParams["font.family"] = prop.get_name()
            return p
    # fallback — 英文环境
    matplotlib.rcParams["font.family"] = "DejaVu Sans"
    return None

FONT_PATH = _setup_chinese_font()


def _wc_font():
    """返回 WordCloud 可用的字体路径（优先中文）。"""
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


STOPWORDS = set(
    "的 了 是 在 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 "
    "会 着 没有 看 好 自己 这 那 里 就是 但是 如果 因为 所以 这个 还是 "
    "对于 可以 已经 这些 他们 我们 什么 时候 一种 一些 通过 之后 "
    "以及 还有 比如 而且 以下 之前 只有 其实 其中 能够 应该 ".split()
)


# ─────────────────────────────────────────────────────────────────────────────
#  数据处理
# ─────────────────────────────────────────────────────────────────────────────

class WeReadAnalyzer:
    def __init__(self, data: dict):
        self.books      = data.get("books", [])
        self.bookmarks  = data.get("bookmarks", [])
        self.reviews    = data.get("reviews", [])
        self.history    = data.get("history", [])
        self.notebooks  = data.get("notebooks", [])
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── 书架统计 ──────────────────────────────────────────────────────────
    def book_stats(self) -> dict:
        total = len(self.books)
        finished = sum(1 for b in self.books if b.get("finishReading") == 1)
        categories = Counter(b.get("category", "未知") for b in self.books)
        return {
            "total":      total,
            "finished":   finished,
            "reading":    total - finished,
            "categories": categories,
        }

    # ── 阅读时长处理 ──────────────────────────────────────────────────────
    def reading_time_df(self) -> pd.DataFrame:
        rows = []
        for rec in self.history:
            ts = rec.get("readDate") or rec.get("timestamp")
            dur = rec.get("readTime") or rec.get("duration", 0)  # 秒
            bid = rec.get("bookId", "")
            if ts and dur:
                rows.append({"date": pd.to_datetime(ts, unit="s"), "minutes": dur / 60, "bookId": bid})
        if not rows:
            return pd.DataFrame(columns=["date", "minutes", "bookId"])
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        return df.groupby(["date", "bookId"], as_index=False)["minutes"].sum()

    # ── 划线文本 ──────────────────────────────────────────────────────────
    def all_highlight_text(self) -> str:
        texts = []
        for bm in self.bookmarks:
            t = bm.get("markText") or bm.get("text", "")
            if t:
                texts.append(t)
        return " ".join(texts)

    def all_note_text(self) -> str:
        texts = []
        for rv in self.reviews:
            r = rv.get("review", rv)
            t = r.get("content") or r.get("abstract", "")
            if t:
                texts.append(t)
        return " ".join(texts)

    # ── 词频 ──────────────────────────────────────────────────────────────
    def word_freq(self, text: str, topn: int = 50) -> Counter:
        words = jieba.cut(text)
        return Counter(
            w for w in words
            if len(w) > 1 and w not in STOPWORDS and re.search(r"[一-鿿]", w)
        ).most_common(topn)


# ─────────────────────────────────────────────────────────────────────────────
#  可视化
# ─────────────────────────────────────────────────────────────────────────────

def plot_overview(az: WeReadAnalyzer) -> str:
    stats = az.book_stats()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("微信读书 · 总览", fontsize=18, fontweight="bold", y=1.02)

    # 1. 完读 vs 在读
    sizes  = [stats["finished"], stats["reading"]]
    labels = [f"已读完\n{stats['finished']} 本", f"阅读中\n{stats['reading']} 本"]
    colors = ["#4CAF50", "#2196F3"]
    wedges, texts, autotexts = axes[0].pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(11)
    axes[0].set_title(f"书架共 {stats['total']} 本", fontsize=13)

    # 2. 分类分布（Top 8）
    cats = stats["categories"].most_common(8)
    if cats:
        cat_names, cat_vals = zip(*cats)
        axes[1].barh(
            list(cat_names)[::-1], list(cat_vals)[::-1],
            color=sns.color_palette("Blues_d", len(cats)),
        )
        axes[1].set_xlabel("书籍数量")
        axes[1].set_title("书籍分类分布", fontsize=13)
        axes[1].tick_params(axis="y", labelsize=9)
    else:
        axes[1].text(0.5, 0.5, "暂无分类数据", ha="center", va="center", transform=axes[1].transAxes)
        axes[1].set_title("书籍分类分布", fontsize=13)

    # 3. 划线 / 笔记数量
    bm_per_book = Counter(bm.get("bookId") for bm in az.bookmarks)
    rv_per_book = Counter(
        (rv.get("review") or rv).get("bookId") for rv in az.reviews
    )
    top_books = [b for b, _ in bm_per_book.most_common(10)]
    book_titles = {}
    for b in az.books:
        book_titles[b.get("bookId", "")] = b.get("title", b.get("bookId", ""))

    labels3 = [book_titles.get(bid, bid)[:8] for bid in top_books]
    bm_vals  = [bm_per_book[bid] for bid in top_books]
    rv_vals  = [rv_per_book.get(bid, 0) for bid in top_books]

    x = range(len(labels3))
    w = 0.4
    axes[2].bar([i - w/2 for i in x], bm_vals, width=w, label="划线", color="#FF9800")
    axes[2].bar([i + w/2 for i in x], rv_vals, width=w, label="笔记", color="#9C27B0")
    axes[2].set_xticks(list(x))
    axes[2].set_xticklabels(labels3, rotation=30, ha="right", fontsize=8)
    axes[2].set_ylabel("数量")
    axes[2].set_title("划线 & 笔记最多的书（Top 10）", fontsize=13)
    axes[2].legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "1_overview.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_reading_heatmap(az: WeReadAnalyzer) -> str:
    df = az.reading_time_df()
    if df.empty:
        return _no_data_plot("阅读时间热力图", "2_heatmap.png", "暂无阅读时长数据")

    daily = df.groupby("date")["minutes"].sum().reset_index()
    daily.columns = ["date", "minutes"]
    daily["date"] = pd.to_datetime(daily["date"])

    # 构造日历矩阵（最近 52 周）
    end   = daily["date"].max()
    start = end - timedelta(weeks=52)
    idx   = pd.date_range(start, end, freq="D")
    s = daily.set_index("date").reindex(idx, fill_value=0)["minutes"]

    weeks = (s.index - s.index[0]).days // 7
    dows  = s.index.dayofweek  # Mon=0

    matrix = pd.DataFrame({"week": weeks, "dow": dows, "val": s.values})
    pivot  = matrix.pivot(index="dow", columns="week", values="val").fillna(0)

    fig, ax = plt.subplots(figsize=(20, 4))
    sns.heatmap(
        pivot, ax=ax, cmap="YlOrRd",
        linewidths=0.3, linecolor="white",
        cbar_kws={"label": "分钟"},
        xticklabels=False,
    )
    ax.set_yticks(range(7))
    ax.set_yticklabels(["周一","周二","周三","周四","周五","周六","周日"], rotation=0)
    ax.set_title("阅读时间热力图（近一年每日分钟数）", fontsize=14)
    ax.set_xlabel("")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "2_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_monthly_trend(az: WeReadAnalyzer) -> str:
    df = az.reading_time_df()
    if df.empty:
        return _no_data_plot("月度阅读趋势", "3_monthly.png", "暂无阅读时长数据")

    df["month"] = df["date"].dt.to_period("M")
    monthly = df.groupby("month")["minutes"].sum()
    monthly.index = monthly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(monthly.index, monthly.values / 60, alpha=0.3, color="#2196F3")
    ax.plot(monthly.index, monthly.values / 60, marker="o", color="#2196F3", linewidth=2)

    for x, y in zip(monthly.index, monthly.values / 60):
        if y > 0:
            ax.annotate(f"{y:.1f}h", (x, y), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=8, color="#1565C0")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha="right")
    ax.set_ylabel("阅读时长（小时）")
    ax.set_title("月度阅读时长趋势", fontsize=14)
    ax.grid(axis="y", alpha=0.3)

    total_h = df["minutes"].sum() / 60
    avg_h   = total_h / max(len(monthly), 1)
    ax.axhline(avg_h, linestyle="--", color="gray", alpha=0.6, label=f"月均 {avg_h:.1f}h")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "3_monthly.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_wordcloud(az: WeReadAnalyzer) -> str:
    text = az.all_highlight_text() + " " + az.all_note_text()
    if not text.strip():
        return _no_data_plot("划线词云", "4_wordcloud.png", "暂无划线/笔记数据")

    words = " ".join(
        w for w in jieba.cut(text)
        if len(w) > 1 and w not in STOPWORDS and re.search(r"[一-鿿]", w)
    )

    wc_kwargs = dict(
        width=1200, height=600,
        background_color="white",
        colormap="viridis",
        max_words=200,
        collocations=False,
    )
    if font := _wc_font():
        wc_kwargs["font_path"] = font

    wc = WordCloud(**wc_kwargs).generate(words)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("划线与笔记高频词云", fontsize=16)

    path = os.path.join(OUTPUT_DIR, "4_wordcloud.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_top_highlights(az: WeReadAnalyzer) -> str:
    """展示被划线最多的书 Top 10，以及总划线数走势。"""
    if not az.bookmarks:
        return _no_data_plot("划线分析", "5_highlights.png", "暂无划线数据")

    book_titles = {b.get("bookId", ""): b.get("title", b.get("bookId", "")) for b in az.books}
    counter = Counter(bm.get("bookId") for bm in az.bookmarks)
    top10   = counter.most_common(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    labels  = [book_titles.get(bid, bid)[:12] for bid, _ in top10]
    vals    = [cnt for _, cnt in top10]
    colors  = sns.color_palette("Oranges_r", len(top10))

    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1])
    for bar, v in zip(bars, vals[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", fontsize=9)

    ax.set_xlabel("划线数量")
    ax.set_title(f"划线最多的书 Top 10（共 {len(az.bookmarks)} 条划线）", fontsize=14)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "5_highlights.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def generate_text_report(az: WeReadAnalyzer) -> str:
    stats    = az.book_stats()
    df       = az.reading_time_df()
    total_h  = df["minutes"].sum() / 60 if not df.empty else 0
    bm_count = len(az.bookmarks)
    rv_count = len(az.reviews)

    book_titles = {b.get("bookId", ""): b.get("title", b.get("bookId", "")) for b in az.books}

    # 划线最多的书
    top_bm = Counter(bm.get("bookId") for bm in az.bookmarks).most_common(5)
    # 笔记最多的书
    top_rv = Counter(
        (rv.get("review") or rv).get("bookId") for rv in az.reviews
    ).most_common(5)

    # 阅读连续天数
    if not df.empty:
        dates  = sorted(df["date"].dt.date.unique())
        streak = _calc_streak(dates)
    else:
        streak = 0

    lines = [
        "=" * 50,
        "      微信读书年度阅读报告",
        "=" * 50,
        "",
        "【总览】",
        f"  书架总数  : {stats['total']} 本",
        f"  已读完    : {stats['finished']} 本",
        f"  完读率    : {stats['finished']/max(stats['total'],1)*100:.1f}%",
        f"  总阅读时长: {total_h:.1f} 小时",
        f"  最长连读  : {streak} 天",
        f"  划线总数  : {bm_count} 条",
        f"  笔记总数  : {rv_count} 条",
        "",
        "【分类偏好 Top 5】",
    ]
    for cat, n in stats["categories"].most_common(5):
        lines.append(f"  {cat:<12}: {n} 本")

    lines += ["", "【划线最多 Top 5】"]
    for bid, cnt in top_bm:
        lines.append(f"  《{book_titles.get(bid, bid)[:15]}》  {cnt} 条")

    lines += ["", "【笔记最多 Top 5】"]
    for bid, cnt in top_rv:
        lines.append(f"  《{book_titles.get(bid, bid)[:15]}》  {cnt} 条")

    if not df.empty:
        monthly = (
            df.assign(month=df["date"].dt.to_period("M"))
            .groupby("month")["minutes"].sum()
        )
        best_m  = monthly.idxmax()
        lines  += [
            "",
            "【月度之最】",
            f"  阅读最多月份: {best_m}  ({monthly[best_m]/60:.1f} 小时)",
        ]

    lines += ["", "=" * 50]
    report = "\n".join(lines)

    path = os.path.join(OUTPUT_DIR, "report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path


def _calc_streak(dates) -> int:
    if not dates:
        return 0
    max_s = cur_s = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            cur_s += 1
            max_s = max(max_s, cur_s)
        else:
            cur_s = 1
    return max_s


def _no_data_plot(title: str, filename: str, msg: str) -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, msg, ha="center", va="center",
            transform=ax.transAxes, fontsize=14, color="gray")
    ax.set_title(title, fontsize=14)
    ax.axis("off")
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path


# ─────────────────────────────────────────────────────────────────────────────
#  一键生成全部报告
# ─────────────────────────────────────────────────────────────────────────────

def run_analysis(data: dict) -> list[str]:
    az = WeReadAnalyzer(data)

    print("\n📊 生成总览图...")
    paths = [plot_overview(az)]

    print("🗓  生成阅读热力图...")
    paths.append(plot_reading_heatmap(az))

    print("📈 生成月度趋势图...")
    paths.append(plot_monthly_trend(az))

    print("☁️  生成词云...")
    paths.append(plot_wordcloud(az))

    print("🔖 生成划线分析...")
    paths.append(plot_top_highlights(az))

    print("📝 生成文字报告...")
    paths.append(generate_text_report(az))

    print(f"\n✅ 所有图表已保存到 {OUTPUT_DIR}/")
    return paths
