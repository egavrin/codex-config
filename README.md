# Codex config

Личная конфигурация Codex для `egavrin`. Снимок настроек macOS от 10 сентября 2026 года.

## Содержимое

- `codex/config.toml` — исходные настройки модели, MCP, плагинов, доверенных проектов и интерфейса приложения.
- `codex/AGENTS.md` — глобальные инструкции; на момент снимка файл пустой.
- `codex/agents/` — профили `worker` и `explorer`.
- `codex/rules/` — локальные правила выполнения команд.
- `codex/skills/` — пользовательские skills: `gh-address-comments`, `gh-fix-ci`, `hatch-pet`, `repo-modernizer`, включая скрипты, ресурсы и имеющиеся лицензии.

Настройки скопированы без изменения значений. В частности, сохранены `gpt-6-astra`, reasoning `high`, `approval_policy = "never"` и `sandbox_mode = "danger-full-access"`.

В репозиторий не включены авторизация, токены, история задач, базы данных, память, вложения, автоматизации, скачанные плагины и системные skills. Проектные инструкции и skills из других репозиториев также не включены. Ресурсы питомца `custom:rivet` не сохранены; в конфиге осталась только настройка его выбора.

## Восстановление

Общий пользовательский конфиг находится в `~/.codex/config.toml`; подробнее — [официальная документация](https://learn.chatgpt.com/docs/config-file/config-basic).

Сначала установите Codex и необходимые плагины. Для клонирования приватного репозитория нужен доступ к аккаунту GitHub:

```sh
gh repo clone egavrin/codex-config
cd codex-config
```

Это снимок конкретного Mac. Перед восстановлением на другой машине проверьте `codex/config.toml`: абсолютные пути `/Users/egavrin`, расположение `/Applications/ChatGPT.app`, пути и версии встроенных плагинов, список доверенных проектов и настройки MCP. Файлы плагинов, MCP-авторизация и ресурсы питомца устанавливаются отдельно. Наличие записей плагинов в конфиге не заменяет их установку.

Закройте Codex перед восстановлением, чтобы приложение не перезаписало настройки. Следующие команды сохраняют резервные копии заменяемых файлов в отдельной временной папке, затем копируют только содержимое `codex/`. Лишние файлы в целевой папке не удаляются:

```sh
codex_target="${CODEX_HOME:-$HOME/.codex}"
codex_backup_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-config-backup.XXXXXX")"
mkdir -p "$codex_target"
rsync -av --backup --backup-dir="$codex_backup_dir" codex/ "$codex_target/"
printf 'Резервная копия заменённых файлов: %s\n' "$codex_backup_dir"
```

Затем снова откройте Codex. Если потребуется, войдите в аккаунт и подключите интеграции.

## Обновление снимка

Из корня клона скопируйте только перечисленные настройки и skills:

```sh
codex_source="${CODEX_HOME:-$HOME/.codex}"
cp "$codex_source/config.toml" codex/config.toml
cp "$codex_source/AGENTS.md" codex/AGENTS.md
for codex_part in agents rules skills/gh-address-comments skills/gh-fix-ci skills/hatch-pet skills/repo-modernizer; do
  mkdir -p "codex/$codex_part"
  rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' --exclude='.git' \
    "$codex_source/$codex_part/" "codex/$codex_part/"
done
git diff --stat
git diff
```

Команды не удаляют из снимка файлы, удалённые в исходной папке; такие удаления нужно перенести вручную. Перед коммитом проверьте diff, особенно значения MCP `env`, HTTP-заголовков и правил команд. `.gitignore` исключает типовые служебные файлы, но не обнаруживает секреты внутри `config.toml` или других отслеживаемых файлов.

```sh
git add codex
git commit -m "Update Codex configuration"
git push
```

Синхронизация выполняется вручную: создание этого репозитория не изменяет активные настройки Codex и не настраивает автоматическую отправку на GitHub.
