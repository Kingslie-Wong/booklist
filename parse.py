# -*- coding: utf-8 -*-
"""解析书单 txt -> books.json"""
import re
import json
import os

SRC = "/Users/geraltwang/Library/Mobile Documents/com~apple~CloudDocs/01-Downloads/02-TXT/6.6w字自制纯爱后宫刘备书单分享.txt"
OUT = "/Users/geraltwang/booklist/books.json"

with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")


def section_of(line):
    s = line.strip()
    s2 = re.sub(r'^[一二三四五六七八九十]+[.、．·]\s*', '', s)
    if s2.startswith('纯爱后宫盘点'):
        return ('纯爱后宫盘点', '10')
    if s2.startswith('韩轻神作'):
        return ('韩轻神作', '5')
    if s2.startswith('刘备肉文'):
        return ('刘备肉文', '5')
    if s2.startswith('擦边小说'):
        return ('擦边小说', '5')
    if s2.startswith('综漫同人'):
        return ('综漫同人', '5')
    if s2.startswith('最后感言'):
        return ('最后感言', None)
    return None


# 评分候选：3-9 的孤立数字（可带一位小数），且后面跟行尾/括号/逗号/空格
def find_score(s):
    # 返回 (start, end, score_str)
    for mm in re.finditer(r'([3-9](?:\.\d)?)', s):
        end = mm.end()
        nxt = s[end] if end < len(s) else ''
        if nxt not in ('', '（', '('):
            continue
        prev = s[mm.start()-1] if mm.start() > 0 else ''
        if prev.isdigit() or prev == '.':
            continue
        return mm.start(), mm.end(), mm.group(1)
    return None


def parse_line(line):
    """返回 (title, score, meta, rest) 或 None"""
    s = line.strip()
    if not s:
        return None
    sc = find_score(s)
    if sc is None:
        return None
    start, end, score_str = sc
    title_part = s[:start].strip()
    # 书名部分若含中文句号，判定为正文（非书名行）
    if '。' in title_part:
        return None
    if not title_part:
        return None
    # 提取 title_part 中评分前的括号内容为 meta
    meta_parts = re.findall(r'[（(][^）)]*[）)]', title_part)
    title = title_part
    for mp in meta_parts:
        title = title.replace(mp, '')
    meta_list = [m.strip('（）()') for m in meta_parts]

    # 评分后紧跟的括号内容也作为 meta（篇幅状态）
    rest = s[end:]
    m2 = re.match(r'^\s*[（(]([^）)]*)[）)]', rest)
    if m2:
        meta_list.append(m2.group(1).strip())
        rest = rest[m2.end():]

    rest = rest.strip().lstrip('，,。；;').strip()
    meta = ' '.join(x for x in meta_list if x)
    title = re.sub(r'\s+', '', title)
    return title, score_str, meta, rest


def main():
    # 1. 找章节标题行号
    section_lines = []  # (line_index, category, score_system)
    for i, line in enumerate(lines):
        sec = section_of(line)
        if sec and sec[1] is not None:
            section_lines.append((i, sec[0], sec[1]))

    books = []
    for idx, (start_i, cat, sys_) in enumerate(section_lines):
        end_i = section_lines[idx + 1][0] if idx + 1 < len(section_lines) else len(lines)
        # 遍历该章节，识别书名行
        entries = []  # (line_i, title, score, meta, rest)
        for i in range(start_i + 1, end_i):
            r = parse_line(lines[i])
            if r:
                entries.append((i, *r))
        # 合并书评（段落化，过滤噪声行）
        def is_noise(t):
            return ('日更新' in t or '日版本' in t
                    or re.fullmatch(r'[\d.]+', t))

        for e_i, (li, title, score, meta, rest) in enumerate(entries):
            next_li = entries[e_i + 1][0] if e_i + 1 < len(entries) else end_i
            paras = []
            cur = []
            if rest:
                cur.append(rest)
            for j in range(li + 1, next_li):
                t = lines[j].strip()
                if not t:
                    if cur:
                        paras.append(''.join(cur))
                        cur = []
                else:
                    if is_noise(t):
                        continue
                    cur.append(t)
            if cur:
                paras.append(''.join(cur))
            review = '\n\n'.join(p for p in paras if p).strip()
            books.append({
                "title": title,
                "score": float(score) if score else None,
                "score_system": sys_,
                "category": cat,
                "meta": meta,
                "is_classic": ('《' in title or '》' in title),
                "is_jialiao": ('加料' in title or '加料' in meta),
                "review": review,
            })

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=1)

    print(f"总条目数: {len(books)}")
    # 按分类统计
    from collections import Counter
    c = Counter(b["category"] for b in books)
    for k, v in c.items():
        print(f"  {k}: {v}")
    # 无评分统计
    nos = [b for b in books if b["score"] is None]
    print(f"无评分条目: {len(nos)}")
    # 书名疑似异常（含数字/评分残留）
    for b in books:
        if re.search(r'\d', b["title"]):
            print("  [标题含数字]", b["title"], "->", b["score"])


if __name__ == "__main__":
    main()
