#!/usr/bin/env python3
"""Нарезка непереведённых строк en.json на чанки для перевода.

Каждый чанк — translations-независимый файл chunks/chunk-NN.json вида
{flat_key: english_value}. Агенты кладут переводы в translations/chunk-NN.json
(то же базовое имя). Защищённое пространство auto.components.settings.plugin* (кроме белого
списка translatable plugin chrome из plugin_chrome.py) и CSS-строки
пропускаются. Уже переведённое не попадает в чанки.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugin_chrome import protected_translation

ROOT = Path(__file__).resolve().parents[1]
EN = json.loads((ROOT / "work" / "en.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "chunks"
OUT_DIR.mkdir(exist_ok=True)
CAP = 460

SKIP_KEYS = {
    # inline CSS анимированных визуалов — переводу не подлежат
    "auto.components.feature.wall.BrowserAnimatedVisual.1bec24acc1",
    "auto.components.feature.wall.EditorAnimatedVisual.e16479c1c5",
    "auto.components.feature.wall.review.animated.visual.notes.styles.db6691aa0a",
    "auto.components.feature.wall.review.animated.visual.pr.view.styles.fc9a23c83d",
    "auto.components.feature.wall.review.animated.visual.ship.styles.90cdcd2ecc",
}


def flatten(node, path=""):
    pairs = []
    for key, value in node.items():
        full = f"{path}.{key}" if path else key
        if isinstance(value, str):
            pairs.append((full, value))
        else:
            pairs.extend(flatten(value, full))
    return pairs


already: set[str] = set()
for path in (ROOT / "translations").glob("*.json"):
    already.update(json.loads(path.read_text(encoding="utf-8")))

todo = [
    (k, v)
    for k, v in flatten(EN)
    if k not in already and k not in SKIP_KEYS and not protected_translation(k)
]

# группировка: сегмент пути (первые 3 сегмента для auto.components.X)
def group_of(key: str) -> tuple[str, ...]:
    parts = key.split(".")
    head = parts[:3] if parts[0] == "auto" else parts[:2]
    return tuple(head)


groups: dict[tuple, list] = {}
for k, v in todo:
    groups.setdefault(group_of(k), []).append((k, v))

# дробим группы больше CAP по следующему сегменту, рекурсивно
def split(group):
    pairs = groups[group]
    if len(pairs) <= CAP:
        return [(group, pairs)]
    depth = len(group)
    subs: dict[tuple, list] = {}
    for k, v in pairs:
        parts = k.split(".")
        sub = group + (parts[depth],) if len(parts) > depth else group
        subs.setdefault(sub, []).append((k, v))
    if len(subs) == 1:
        # дальше резать нечем — режем пополам
        pairs = sorted(pairs)
        mid = len(pairs) // 2
        return [(group + ("#a",), pairs[:mid]), (group + ("#b",), pairs[mid:])]
    out = []
    for sub, sub_pairs in subs.items():
        groups[sub] = sub_pairs
        out.extend(split(sub))
    return out


units = sorted(
    sorted(sum((split(g) for g in list(groups)), []), key=lambda u: -len(u[1]))
)

chunks = []
current: dict[str, str] = {}

for _, pairs in units:
    if len(current) + len(pairs) > CAP and current:
        chunks.append(current)
        current = {}
    for k, v in pairs:
        current[k] = v
if current:
    chunks.append(current)

# старые чанки не смешиваем
for old in OUT_DIR.glob("chunk-*.json"):
    old.unlink()

manifest = {}
for i, chunk in enumerate(chunks, 1):
    name = f"chunk-{i:02d}"
    (OUT_DIR / f"{name}.json").write_text(
        json.dumps(chunk, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    manifest[name] = len(chunk)

print(f"чанков: {len(chunks)}; строк к переводу: {len(todo)}")
print(manifest)
