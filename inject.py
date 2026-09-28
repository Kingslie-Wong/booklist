# -*- coding: utf-8 -*-
import json

TPL = "/Users/geraltwang/booklist/index.template.html"
DATA = "/Users/geraltwang/booklist/books.json"
OUT = "/Users/geraltwang/booklist/index.html"

books = json.load(open(DATA, encoding="utf-8"))
tpl = open(TPL, encoding="utf-8").read()

js = json.dumps(books, ensure_ascii=False, separators=(",", ":"))
# 防止 </script> 提前闭合
js = js.replace("</", "<\\/")

html = tpl.replace("__BOOKS_JSON__", js)
open(OUT, "w", encoding="utf-8").write(html)

import os
print("生成", OUT, f"{os.path.getsize(OUT)/1024:.1f} KB")
