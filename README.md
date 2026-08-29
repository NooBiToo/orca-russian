# orca-russian · Русский язык-пак для Orca

![Version](https://img.shields.io/github/v/tag/NooBiToo/orca-russian?label=%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%8F)
![Coverage](https://img.shields.io/badge/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4-13%20660%2F13%20676-brightgreen)
![Orca](https://img.shields.io/badge/Orca-%3E%3D1.4.0-blue)
![Plugin API](https://img.shields.io/badge/pluginApi-1-informational)

Полный русский перевод интерфейса [Orca](https://github.com/stablyai/orca) —
Agent Development Environment для работы с парком параллельных AI-агентов.
Оформлен как официальный плагин-язык-пак (`contributes.languagePacks`).

**English:** Complete Russian UI translation for
[Orca](https://github.com/stablyai/orca) (ADE for parallel AI coding agents),
packaged as a language-pack plugin. 13 559 / 13 676 translatable strings —
the only exceptions are inline-CSS animation entries and the strings
protected by Orca's plugin loader.

## Возможности

- **Переведено всё, что разрешено загрузчиком Orca** — 13 559 из 13 676 строк
  (исключения: security-copy поверхности плагинов, защищённые загрузчиком, и
  inline-CSS): настройки, сайдбары, редактор, терминал,
  браузер, GitHub/GitLab/Linear/Jira, дашборд агентов, скиллы, автоматизации,
  мобильный компаньон, трей, меню.
- **Русские plural-формы** (1 агент / 2 агента / 5 агентов) добавлены ко всем
  plural-семействам в стиле каждого семейства (`_few`/`_many` или CamelCase).
- **Sparse-каталог**: недостающие строки автоматически падают в английский,
  плагин безопасно включать на любой версии Orca.
- Каталог проверяется скриптом сборки по правилам загрузчика Orca
  (`parsePluginLanguagePackArtifact`): плейсхолдеры посимвольно, лимиты
  записей/глубины/длины, защищённые пространства.

## Установка

1. **Settings → Plugins** → включить систему плагинов.
2. Добавить источник (Git URL) — с явным `#ref`, как требует Orca:

   ```
   https://github.com/NooBiToo/orca-russian#v1.0.2
   ```

3. Установить плагин **Русский** и включить его.
4. **Settings → Appearance → Language** → **Русский**.

Обновление — на новый тег: `#v1.1.0`, `#v1.2.0` и т.д. Откат — на любой
прошлый тег.

## Структура

```
orca-plugin.json           # манифест плагина (contributes.languagePacks, locale ru)
locales/ru.json            # собранный вложенный каталог — артефакт, не редактировать
translations/*.json        # источник перевода: плоские ключи a.b.c -> русский текст
work/en.json               # снимок английского каталога из stablyai/orca
scripts/build.py           # сборка locales/ru.json + валидация по правилам Orca
scripts/chunk.py           # нарезка непереведённых строк на чанки
TERMINOLOGY.md             # глоссарий и правила перевода
```

## Рабочий процесс

Перевод ведётся в `translations/*.json` (одна строка = одна запись — удобно
для ревью и диффов), затем:

```bash
python scripts/build.py
```

Скрипт сливает все файлы перевода, проверяет существование ключей в en.json,
паритет плейсхолдеров `{{...}}`, правила загрузчика Orca (≤ 20 000 записей,
глубина ≤ 16, строки ≤ 8 192 символов, безопасные ключи, запрет вторжения
в `auto.components.settings.plugin*`) и предупреждает о строках без
кириллицы. Результат — `locales/ru.json`.

Обновление снимка en.json из апстрима:

```bash
curl -sL https://raw.githubusercontent.com/stablyai/orca/main/src/renderer/src/i18n/locales/en.json -o work/en.json
python scripts/chunk.py   # покажет новые непереведённые строки
```

## Соглашения перевода

Полный глоссарий и правила — в [TERMINOLOGY.md](TERMINOLOGY.md). Коротко:

- обращение — «вы» со строчной (стиль локализаций VS Code / GitHub);
- не переводим: `worktree`, `PR`/`MR`, имена продуктов, CLI-литералы;
- устоявшиеся заимствования кириллицей: «воркспейс», «коммит», «дифф»,
  «ревью», «дашборд», «скилл», «промпт»;
- кавычки — «ёлочки», вложенные — „лапки"; плейсхолдеры `{{...}}`
  переносятся посимвольно.

## Благодарности

Структура плагина и рабочий процесс повторяют официальный
[orca-portuguese](https://github.com/stablyai/orca-portuguese) от команды
Orca — спасибо за образец.
