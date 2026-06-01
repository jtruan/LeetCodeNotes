"""微信读书数据分析与可视化"""

import os
import re
from datetime import datetime, timezone

import jieba
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from collections import Counter
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
    ]
    for p in candidates:
        if os.path.exists(p):
            prop = fm.FontProperties(fname=p)
            matplotlib.rcParams["font.family"] = prop.get_name()
            return p
    matplotlib.rcParams["font.family"] = "DejaVu Sans"
    return None

_setup_chinese_font()

STOPWORDS = set(
    "的 了 是 在 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 "
    "会 着 没有 看 好 自己 这 那 里 就是 但是 如果 因为 所以 这个 还是 "
    "对于 可以 已经 这些 他们 我们 什么 时候 一种 一些 通过 之后 "
    "以及 还有 比如 而且 以下 之前 只有 其实 其中 能够 应该 ".split()
)

def _wc_font():
    for p in [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]:
        if os.path.exists(p):
            return p
    return None

def _ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else ""

def _sec_fmt(seconds: int) -> str:
    h, m = divmod(int(seconds) // 60, 60)
    return f"{h}小时{m}分钟" if h else f"{m}分钟"


# ─────────────────────────────────────────────────────────────────────────────
class WeReadAnalyzer:
    def __init__(self, data: dict):
        self.books     = data.get("books", [])
        self.albums    = data.get("albums", [])
        self.bookmarks = data.get("bookmarks", [])
        self.reviews   = data.get("reviews", [])
        self.notebooks = data.get("notebooks", [])
        self.rd_overall = data.get("readdata_overall", {})
        self.rd_annual  = data.get("readdata_annually", {})
        self.rd_monthly = data.get("readdata_monthly", {})
        self._book_map  = {b["bookId"]: b for b in self.books if b.get("bookId")}
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def title(self, book_id: str) -> str:
        b = self._book_map.get(book_id, {})
        return b.get("title", book_id)[:15]

    def all_highlight_text(self) -> str:
        return " ".join(bm.get("markText", "") for bm in self.bookmarks if bm.get("markText"))

    def all_note_text(self) -> str:
        texts = []
        for rv in self.reviews:
            r = rv.get("review", rv)
            texts.append(r.get("content") or r.get("abstract", ""))
        return " ".join(t for t in texts if t)

    def word_freq(self, text: str, topn: int = 50):
        words = jieba.cut(text)
        return Counter(
            w for w in words
            if len(w) > 1 and w not in STOPWORDS and re.search(r"[一-鿿]", w)
        ).most_common(topn)

    # ── 从 readdata 提取月度时长序列 ────────────────────────────────────
    def monthly_hours(self) -> pd.Series:
        """从 readdata_annually 的 readTimes 提取按月阅读时长（小时）。"""
        rt = self.rd_annual.get("readTimes", {})
        if not rt:
            rt = self.rd_overall.get("readTimes", {})
        if not rt:
            return pd.Series(dtype=float)
        s = pd.Series({
            pd.Timestamp(int(k), unit="s"): v / 3600
            for k, v in rt.items()
        }).sort_index()
        s.index = s.index.to_period("M").to_timestamp()
        return s.groupby(level=0).sum()

    # ── 偏好时段（preferTime 从 6 点起的 24 段，单位秒）────────────────
    def prefer_time(self) -> list[int]:
        return self.rd_overall.get("preferTime") or self.rd_annual.get("preferTime", [])

    # ── 偏好分类 ──────────────────────────────────────────────────────────
    def prefer_category(self) -> list[dict]:
        return (
            self.rd_overall.get("preferCategory")
            or self.rd_annual.get("preferCategory", [])
        )


# ─────────────────────────────────────────────────────────────────────────────
#  图表
# ─────────────────────────────────────────────────────────────────────────────

def plot_overview(az: WeReadAnalyzer) -> str:
    books    = az.books
    total    = len(books) + len(az.albums)
    finished = sum(1 for b in books if b.get("finishReading") == 1)
    reading  = total - finished

    # 分类来自 readdata preferCategory
    cats = az.prefer_category()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("微信读书 · 总览", fontsize=18, fontweight="bold")

    # 完读饼图
    sizes  = [finished, reading]
    labels = [f"已读完\n{finished} 本", f"阅读中\n{reading} 本"]
    axes[0].pie(
        sizes, labels=labels,
        colors=["#4CAF50", "#2196F3"],
        autopct="%1.1f%%", startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    axes[0].set_title(f"书架共 {total} 本", fontsize=13)

    # 偏好分类（来自官方数据）
    if cats:
        top8  = sorted(cats, key=lambda x: x.get("readingTime", 0), reverse=True)[:8]
        names = [c.get("categoryTitle", "") for c in top8][::-1]
        times = [c.get("readingTime", 0) / 3600 for c in top8][::-1]
        axes[1].barh(names, times, color=sns.color_palette("Blues_d", len(top8)))
        axes[1].set_xlabel("阅读时长（小时）")
        axes[1].set_title("偏好分类（阅读时长）", fontsize=13)
    else:
        axes[1].text(0.5, 0.5, "暂无分类数据", ha="center", va="center",
                     transform=axes[1].transAxes, color="gray")
        axes[1].set_title("偏好分类", fontsize=13)

    # 划线/笔记排行
    bm_cnt = Counter(bm.get("bookId") for bm in az.bookmarks)
    rv_cnt = Counter((rv.get("review") or rv).get("bookId") for rv in az.reviews)
    top10  = [bid for bid, _ in bm_cnt.most_common(10)]

    labels3 = [az.title(bid) for bid in top10]
    x = range(len(labels3))
    w = 0.4
    axes[2].bar([i - w/2 for i in x], [bm_cnt[bid] for bid in top10],
                width=w, label="划线", color="#FF9800")
    axes[2].bar([i + w/2 for i in x], [rv_cnt.get(bid, 0) for bid in top10],
                width=w, label="笔记", color="#9C27B0")
    axes[2].set_xticks(list(x))
    axes[2].set_xticklabels(labels3, rotation=30, ha="right", fontsize=8)
    axes[2].set_ylabel("数量")
    axes[2].set_title("划线 & 笔记 Top 10", fontsize=13)
    axes[2].legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "1_overview.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_monthly_trend(az: WeReadAnalyzer) -> str:
    s = az.monthly_hours()
    if s.empty:
        return _no_data_plot("月度阅读趋势", "2_monthly.png", "暂无阅读时长数据")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(s.index, s.values, alpha=0.3, color="#2196F3")
    ax.plot(s.index, s.values, marker="o", color="#2196F3", linewidth=2)
    for x, y in zip(s.index, s.values):
        if y > 0:
            ax.annotate(f"{y:.1f}h", (x, y), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=8, color="#1565C0")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha="right")
    ax.set_ylabel("阅读时长（小时）")
    ax.set_title("月度阅读时长趋势", fontsize=14)
    ax.grid(axis="y", alpha=0.3)
    if len(s) > 0:
        avg = s.mean()
        ax.axhline(avg, linestyle="--", color="gray", alpha=0.6, label=f"月均 {avg:.1f}h")
        ax.legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "2_monthly.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_prefer_time(az: WeReadAnalyzer) -> str:
    pt = az.prefer_time()
    if not pt or len(pt) < 24:
        return _no_data_plot("阅读偏好时段", "3_prefer_time.png", "暂无时段数据")

    # preferTime 从 6 点起排列
    hours  = [(i + 6) % 24 for i in range(24)]
    values = [pt[i] / 60 for i in range(24)]  # 秒 → 分钟

    fig, ax = plt.subplots(figsize=(12, 5), subplot_kw={"polar": False})
    bars = ax.bar(range(24), values, color=sns.color_palette("YlOrRd", 24))
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}:00" for h in hours], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("阅读时长（分钟）")
    ax.set_title("24 小时阅读偏好时段", fontsize=14)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "3_prefer_time.png")
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
    wc_kw = dict(width=1200, height=600, background_color="white",
                 colormap="viridis", max_words=200, collocations=False)
    if fp := _wc_font():
        wc_kw["font_path"] = fp
    wc = WordCloud(**wc_kw).generate(words)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("划线与笔记高频词云", fontsize=16)

    path = os.path.join(OUTPUT_DIR, "4_wordcloud.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def plot_top_highlights(az: WeReadAnalyzer) -> str:
    if not az.bookmarks:
        return _no_data_plot("划线排行", "5_highlights.png", "暂无划线数据")

    counter = Counter(bm.get("bookId") for bm in az.bookmarks)
    top10   = counter.most_common(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    labels  = [az.title(bid) for bid, _ in top10]
    vals    = [cnt for _, cnt in top10]
    colors  = sns.color_palette("Oranges_r", len(top10))

    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1])
    for bar, v in zip(bars, vals[::-1]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", fontsize=9)

    ax.set_xlabel("划线数量")
    ax.set_title(f"划线最多的书 Top 10（共 {len(az.bookmarks)} 条）", fontsize=14)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "5_highlights.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def generate_text_report(az: WeReadAnalyzer) -> str:
    rd = az.rd_overall or az.rd_annual or az.rd_monthly
    total_sec  = rd.get("totalReadTime", 0)
    read_days  = rd.get("readDays", 0)
    read_stat  = rd.get("readStat", [])

    finished_cnt = sum(1 for b in az.books if b.get("finishReading") == 1)
    total_books  = len(az.books) + len(az.albums)

    longest = rd.get("readLongest", [])
    cats    = az.prefer_category()
    pt_word = (rd.get("preferTimeWord") or az.rd_annual.get("preferTimeWord", ""))
    prefer_author = rd.get("preferAuthor") or az.rd_annual.get("preferAuthor", [])

    bm_cnt = Counter(bm.get("bookId") for bm in az.bookmarks)
    rv_cnt = Counter((rv.get("review") or rv).get("bookId") for rv in az.reviews)

    lines = [
        "=" * 52,
        "       微信读书个人阅读报告",
        "=" * 52,
        "",
        "【总览】",
        f"  书架总数  : {total_books} 本（电子书 {len(az.books)}，有声书 {len(az.albums)}）",
        f"  已读完    : {finished_cnt} 本",
        f"  完读率    : {finished_cnt/max(len(az.books),1)*100:.1f}%",
        f"  累计时长  : {_sec_fmt(total_sec)}",
        f"  有效阅读天: {read_days} 天",
        f"  划线总数  : {len(az.bookmarks)} 条",
        f"  笔记总数  : {len(az.reviews)} 条",
    ]

    if read_stat:
        lines += ["", "【阅读统计】"]
        for s in read_stat:
            lines.append(f"  {s.get('stat',''):8}: {s.get('counts','')}")

    if cats:
        lines += ["", "【偏好分类 Top 5】"]
        for c in sorted(cats, key=lambda x: x.get("readingTime", 0), reverse=True)[:5]:
            rt = _sec_fmt(c.get("readingTime", 0))
            lines.append(f"  {c.get('categoryTitle',''):<12}: {c.get('readingCount',0)} 本  {rt}")

    if longest:
        lines += ["", "【阅读时长 Top 5】"]
        for item in longest[:5]:
            b = item.get("book") or item.get("albumInfo", {})
            t = b.get("title") or b.get("name", "未知")
            lines.append(f"  《{t[:15]}》  {_sec_fmt(item.get('readTime', 0))}")

    if prefer_author:
        lines += ["", "【偏好作者 Top 5】"]
        for a in prefer_author[:5]:
            lines.append(f"  {a.get('name',''):12}: {a.get('count',0)} 本  {a.get('readTime','')}")

    if pt_word:
        lines += ["", f"【阅读时段偏好】", f"  {pt_word}"]

    lines += ["", "【划线最多 Top 5】"]
    for bid, cnt in bm_cnt.most_common(5):
        lines.append(f"  《{az.title(bid)}》  {cnt} 条")

    lines += ["", "【笔记最多 Top 5】"]
    for bid, cnt in rv_cnt.most_common(5):
        lines.append(f"  《{az.title(bid)}》  {cnt} 条")

    lines += ["", "=" * 52]
    report = "\n".join(lines)
    path = os.path.join(OUTPUT_DIR, "report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path


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
def run_analysis(data: dict) -> list[str]:
    az = WeReadAnalyzer(data)
    paths = []
    print("\n📊 生成总览图...")
    paths.append(plot_overview(az))
    print("📈 生成月度趋势图...")
    paths.append(plot_monthly_trend(az))
    print("🕐 生成偏好时段图...")
    paths.append(plot_prefer_time(az))
    print("☁️  生成词云...")
    paths.append(plot_wordcloud(az))
    print("🔖 生成划线排行...")
    paths.append(plot_top_highlights(az))
    print("📝 生成文字报告...")
    paths.append(generate_text_report(az))
    print(f"\n✅ 所有图表已保存到 {OUTPUT_DIR}/")
    return paths
