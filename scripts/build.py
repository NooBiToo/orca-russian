#!/usr/bin/env python3
"""Сборка и валидация русского языка-пака для Orca.

Читает work/en.json (снимок английского каталога из stablyai/orca,
src/renderer/src/i18n/locales/en.json) и translations/ru.flat.json
(плоские ключи «a.b.c» -> русский текст), собирает locales/ru.json
и прогоняет его по правилам загрузчика Orca
(src/shared/plugins/plugin-language-pack-artifact.ts):

  - корень — объект; максимум 20 000 записей; глубина <= 16
  - ключи: не пустые, <= 128 символов, без точек и управляющих символов,
    не __proto__/prototype/constructor
  - значения — только строки, каждая <= 8192 символов
  - запрещено перекрывать защищённое пространство auto.components.settings.plugin*
  - без повторяющихся/циклических объектов

Дополнительно проверяет паритет плейсхолдеров {{...}} между en и ru.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "work" / "en.json"
TRANSLATIONS_DIR = ROOT / "translations"
OUT_PATH = ROOT / "locales" / "ru.json"

MAX_ENTRIES = 20_000
MAX_DEPTH = 16
MAX_STRING = 8_192
DANGEROUS_KEYS = {"__proto__", "prototype", "constructor"}
PROTECTED_ROOT = "auto.components.settings."
PROTECTED_MODULE = re.compile(r"^plugin")
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")

errors: list[str] = []
warnings: list[str] = []


def main() -> int:
    en = json.loads(EN_PATH.read_text(encoding="utf-8"))
    flat: dict[str, str] = {}
    for path in sorted(TRANSLATIONS_DIR.glob("*.json")):
        part = json.loads(path.read_text(encoding="utf-8"))
        for key, value in part.items():
            if key in flat:
                errors.append(f"дубликат ключа {key} в {path.name}")
            flat[key] = value

    def lookup(node, dotted):
        cur = node
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur

    # 1. Ключи должны существовать в en.json; исключение — добавленные
    #    plural-формы к существующему семейству (в русском четыре категории,
    #    в английском две). Стиль суффиксов должен повторять семейство:
    #    en встречает и x_one/x_other, и CamelCase xOne/xOther.
    PLURAL_SUFFIXES = ("zero", "one", "two", "few", "many", "other")
    CAMEL = {"one": "One", "two": "Two", "few": "Few", "many": "Many",
             "other": "Other", "zero": "Zero"}

    def family_exists(base: str) -> bool:
        return lookup(en, base) is not None or any(
            lookup(en, f"{base}_{s}") is not None for s in PLURAL_SUFFIXES
        ) or any(lookup(en, f"{base}{CAMEL[s]}") is not None for s in PLURAL_SUFFIXES)

    added_plurals = []
    unknown = []
    for k in list(flat):
        if lookup(en, k) is not None:
            continue
        base, sep, suffix = k.rpartition("_")
        m = re.match(r"^(.+?)(One|Two|Few|Many|Other|Zero)$", k)
        if sep and suffix in PLURAL_SUFFIXES and family_exists(base):
            added_plurals.append(k)  # стиль как у семейства с _
        elif m and family_exists(m.group(1)):
            camel_family = any(
                lookup(en, f"{m.group(1)}{CAMEL[s]}") is not None for s in PLURAL_SUFFIXES
            )
            if camel_family:
                added_plurals.append(k)  # CamelCase-семейство — оставляем как есть
            else:
                nk = f"{m.group(1)}_{m.group(2).lower()}"
                if nk in flat:
                    errors.append(f"дубликат plural-ключа после нормализации: {k}")
                else:
                    warnings.append(f"нормализован plural-ключ: {k} -> {nk}")
                    flat[nk] = flat.pop(k)
                    added_plurals.append(nk)
        else:
            unknown.append(k)
    for k in unknown:
        errors.append(f"ключа нет в en.json: {k}")

    # 2. Паритет плейсхолдеров
    for k, ru in flat.items():
        en_val = lookup(en, k)
        if not isinstance(en_val, str):
            continue
        en_ph = sorted(PLACEHOLDER.findall(en_val))
        ru_ph = sorted(PLACEHOLDER.findall(ru))
        if en_ph != ru_ph:
            errors.append(
                f"плейсхолдеры не совпадают для {k}:\n  en: {en_ph}\n  ru: {ru_ph}"
            )

    # 3. Идентичные английскому строки (не ошибка, но взгляд притянуть стоит)
    identical = [
        k
        for k, ru in flat.items()
        if isinstance(lookup(en, k), str)
        and ru == lookup(en, k)
        and not k.endswith(("_one", "_few", "_many", "_other"))
        and re.search(r"[а-яА-ЯёЁ]", ru) is None
    ]
    for k in identical:
        warnings.append(f"строка совпадает с английской (кириллицы нет): {k}")

    # 4. Вложенный каталог: только переведённые ключи (sparse-каталог)
    nested: dict = {}
    for dotted, value in sorted(flat.items()):
        parts = dotted.split(".")
        cur = nested
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value

    # 5. Правила загрузчика Orca
    count = 0

    def walk(node, path="", depth=0):
        global errors
        nonlocal count
        if depth > MAX_DEPTH:
            errors.append(f"глубина каталога > {MAX_DEPTH} на {path or '(root)'}")
            return
        for key, value in node.items():
            count += 1
            if count > MAX_ENTRIES:
                errors.append(f"каталог превышает {MAX_ENTRIES} записей")
                return
            if not key or len(key) > 128 or key in DANGEROUS_KEYS or "." in key:
                errors.append(f"небезопасный ключ: {key!r} на {path}")
                continue
            if any(ord(c) <= 31 for c in key):
                errors.append(f"управляющий символ в ключе: {key!r} на {path}")
                continue
            full = f"{path}.{key}" if path else key
            if full.startswith(PROTECTED_ROOT) and PROTECTED_MODULE.match(
                full[len(PROTECTED_ROOT):]
            ):
                errors.append(f"защищённое пространство перекрыто: {full}")
            if isinstance(value, str):
                if len(value) > MAX_STRING:
                    errors.append(f"строка > {MAX_STRING} символов на {full}")
            elif isinstance(value, dict):
                walk(value, full, depth + 1)
            else:
                errors.append(f"значение не строка и не объект: {full}")

    walk(nested)

    total_en = 0

    def count_en(node):
        nonlocal total_en
        for v in node.values():
            if isinstance(v, str):
                total_en += 1
            else:
                count_en(v)

    count_en(en)

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    print(f"\nПереведено: {len(flat)} из {total_en} строк en.json "
          f"({len(flat) / total_en:.1%})")
    if added_plurals:
        print(f"Добавлены русские plural-формы ({len(added_plurals)}): "
              + ", ".join(added_plurals))

    if errors:
        print("\nСБОРКА ПРЕРВАНА: исправьте ошибки выше.")
        return 1

    OUT_PATH.write_text(
        json.dumps(nested, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: locales/ru.json собран ({count} записей).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
