# -*- coding: utf-8 -*-
"""从 books.json 生成 Obsidian 书单 markdown"""
import json

DATA = "/Users/geraltwang/booklist/books.json"
OUT = "/Users/geraltwang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault II/纯爱后宫书单.md"

books = json.load(open(DATA, encoding="utf-8"))

STATUS_WORDS = ['未完结', '停更', '烂尾', '太监', '完本', '连载', '完结']
LENGTH_WORDS = ['超长篇', '长篇', '中篇', '短篇']
KW = ['ntl', '调教', '催眠', '萝莉', '巨乳', '人妻', '母子', '乱伦', '触手',
      '综漫', '同人', '仙侠', '都市', '西幻', '武侠', '历史', '末世', '游戏',
      '纯爱', '后宫', '父女', '姐妹', '兄妹', '逆推', '明星', '偶像', '百合']


def derive(b):
    meta = (b['meta'] or '').replace('（', '').replace('）', '').replace('(', '').replace(')', '')
    head = meta + ' ' + (b['review'] or '')[:50]
    status = next((w for w in STATUS_WORDS if w in head), '')
    length = next((w for w in LENGTH_WORDS if w in head), '')
    tags = []
    if b['is_classic']:
        tags.append('经典')
    if b['is_jialiao']:
        tags.append('加料')
    hay = b['title'] + meta
    for k in KW:
        if k in hay:
            tags.append(k)
    seen = set()
    tags = [t for t in tags if not (t in seen or seen.add(t))]
    return status, length, tags


def grade(b):
    s = b['score']
    if b['score_system'] == '10':
        if s >= 9:
            return '神作'
        if s >= 8.5:
            return '推荐'
        if s >= 8:
            return '可读'
        return '一般'
    if s >= 6:
        return '神作'
    if s >= 5:
        return '佳作'
    if s >= 4:
        return '推荐'
    if s >= 3:
        return '平庸'
    return '一般'


CAT_ORDER = ['纯爱后宫盘点', '韩轻神作', '刘备肉文', '擦边小说', '综漫同人']
CAT_INTRO = {
    '纯爱后宫盘点': '核心推荐区 · 10 分制长评',
    '韩轻神作': '图文结合模式 · 5 分制 · 配图质量是重要加分项',
    '刘备肉文': '纯肉文为主 · 5 分制 · 含纯爱 / 后宫 / ntl / 调教',
    '擦边小说': '5 分制 · 多来自次元姬 / 少年梦 · 大多有加料',
    '综漫同人': '5 分制 · 次元姬 / 少年梦车速平台 · 动漫角色同人',
}

L = []
A = L.append

# ===== Frontmatter =====
A('---')
A('title: 纯爱后宫书单')
A('source: 尚香书苑 (sxsy.org)')
A('author: 纯爱战神风行')
A('date: 2026-09-28')
A('tags:')
A('  - 书单')
A('  - 纯爱后宫')
A('  - 刘备')
A('---')
A('')
A('# 纯爱后宫书单')
A('')
A('> 6.6 万字长评 · **409** 本 · 带评分与阅读指南')
A('>')
A('> 整理自作者「纯爱战神风行」的公开书单分享。原文为纯爱 / 后宫向刘备（成人小说）书单，')
A('> 含两套评分体系：前段为 10 分制长评，2026.9.24 更新部分为 5 分制。')
A('')

# ===== 阅读指南 =====
A('## 阅读指南')
A('')
A('### 10 分制（纯爱后宫盘点·长评）')
A('')
A('- **9 分以上**：无雷点，剧情 / 人设 / 感情 / 肉戏俱全的神作，必看')
A('- **8.5–8.9 分**：有情感、有剧情人物和世界观，较推荐')
A('- **8 分**：纯粹肉文，无脑无绿式后宫，可作手冲文')
A('- **8.4 分及以下**：肉多无感情戏，仅作消遣')
A('')
A('- 用《书名号》标注的是**经典**（早年作品），往往有些小雷，需有一定防御观看')
A('- **加料版**指在原作基础上增补了肉戏描写的版本')
A('')
A('### 5 分制（2026.9.24 更新）')
A('')
A('- **6 分**：神作必读　·　**5 分**：佳作推荐　·　**4 分**：可以一读　·　**3 分**：平庸凑数')
A('')
A('### 分类概览')
A('')
A('| 分类 | 数量 | 评分制 | 说明 |')
A('| ---- | ---: | ---- | ---- |')
for c in CAT_ORDER:
    n = sum(1 for b in books if b['category'] == c)
    sys = '10 分制' if c == '纯爱后宫盘点' else '5 分制'
    A(f'| {c} | {n} | {sys} | {CAT_INTRO[c].split(" · ", 1)[-1]} |')
A('')
A('---')
A('')

# ===== 分类章节 =====
for cat in CAT_ORDER:
    items = [b for b in books if b['category'] == cat]
    items.sort(key=lambda b: -b['score'])
    A(f'## {cat}')
    A('')
    A(f'> {CAT_INTRO[cat]} · 共 {len(items)} 本')
    A('')
    for b in items:
        status, length, tags = derive(b)
        g = grade(b)
        sys = '10' if b['score_system'] == '10' else '5'
        A(f'### {b["title"]}　`{b["score"]}/{sys}`　`{g}`')
        A('')
        metas = [x for x in [length, status,
                             '加料版' if b['is_jialiao'] else '',
                             '经典' if b['is_classic'] else ''] if x]
        if metas:
            A('**' + ' · '.join(metas) + '**')
            A('')
        if tags:
            A(' '.join(f'`{t}`' for t in tags))
            A('')
        review = (b['review'] or '').strip()
        if review:
            paras = [p.strip() for p in review.split('\n\n') if p.strip()]
            A('> [!note]- 书评')
            for i, para in enumerate(paras):
                A('> ' + para.replace('\n', ' '))
                if i < len(paras) - 1:
                    A('>')
            A('')
        A('')

open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print(f"已生成 {OUT}")
print(f"总条目 {len(books)} · 行数 {len(L)}")
