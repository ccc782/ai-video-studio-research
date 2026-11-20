# -*- coding: utf-8 -*-
"""校验 E 文档里的最小工程样例是否过 schema。"""
import json, re, sys, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schema_path = next(p for p in (os.path.join(root, "E_avs_project.schema.json"), os.path.join(root, "schema", "E_avs_project.schema.json")) if os.path.exists(p))
doc_path = next(p for p in (os.path.join(root, "E_统一工程文件格式.md"), os.path.join(root, "docs", "E_统一工程文件格式.md")) if os.path.exists(p))

schema = json.load(open(schema_path, encoding="utf-8"))
print("schema 载入成功；$defs 数量 =", len(schema["$defs"]),
      "；顶层 required =", schema["required"])

text = open(doc_path, encoding="utf-8").read()
m = re.search(r"## 10\..*?```json\n(.*?)```", text, re.S)
if not m:
    print("样例块未找到"); sys.exit(1)
sample = json.loads(m.group(1))
os.makedirs(os.path.join(root, "samples"), exist_ok=True)
json.dump(sample, open(os.path.join(root, "samples", "min_project.json"), "w",
                       encoding="utf-8"), ensure_ascii=False, indent=2)
print("样例已抽出 -> samples/min_project.json，顶层键 =", len(sample))

try:
    import jsonschema
except ImportError:
    print("jsonschema 未安装，跳过严格校验"); sys.exit(0)

validator = jsonschema.Draft202012Validator(schema)
errs = sorted(validator.iter_errors(sample), key=lambda e: list(e.path))
if not errs:
    print("PASS：样例通过 AVS 1.0 schema 校验")
else:
    for e in errs[:20]:
        print("FAIL", list(e.path), e.message)
    print("共", len(errs), "处")