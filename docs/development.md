# Разработка и релизы

## Структура

`src/petrovich/main.py` содержит движок, `enums.py` — перечисления,
`rules.py` — неизменяемые модели, валидацию и ввод-вывод, `cli.py` — команды.
Runtime использует только стандартную библиотеку. В `tests/` — pytest-тесты
без обращений к сети. `py.typed` включает поддержку типизации для пользователей.

## Git flow

Долгоживущая ветка разработки — `petrovich_2` (роль `develop`).
Стабильная ветка новых версий — `main`; её создают при первом стабильном релизе.
`master` остаётся исторической веткой, `legacy/1.x` — линией сопровождения 1.x.
Это адаптация Git flow с сохранением запрошенного имени ветки разработки.

Рабочие ветки `feature/*` создавайте от `petrovich_2`, вливайте через pull request.
Для подготовки 2.0 создайте `release/2.0` от `petrovich_2`. В release-ветке
допускаются исправления, обновление документации и версии, без новых функций.
После релиза влейте изменения в `main` и обратно в `petrovich_2`.
Срочные исправления делайте в `hotfix/*` от соответствующего тега и вливайте
в стабильную и разрабатываемую ветки.

Версия хранится в `pyproject.toml`. `scripts/ci_version.py` проверяет её:

- Обычные ветки собираются с версией из файла.
- `release/2.0` с базой `2.0.0` или `2.0.0.dev0` даёт артефакт
  `2.0.0.dev<N>`, где N — номер запуска GitHub Actions или `CI_PIPELINE_IID`
  в GitLab. Для базы `2.0.1` получается `2.0.1.dev<N>`.
- Тег `v2.0.0` требует точного совпадения с версией `2.0.0` в файле.
- Разрешены предварительные релизы: `v2.0.0rc1`, `v2.0.0a1`, `v2.0.0b1`.
- Версии 1.x новой сборкой не публикуются.

Release-ветки создают скачиваемые wheel/sdist, но не публикуют их в PyPI.
Публикация запускается автоматически только для защищённого тега новой версии
после успешных тестов и сборки. Push ветки разработки не выпускает релиз.

## Настройка GitHub и PyPI

Основной репозиторий: https://github.com/damirazo/Petrovich.
Workflow `.github/workflows/ci.yml` запускает тесты на Python 3.12–3.14,
собирает wheel/sdist и сохраняет их как артефакт `distributions`.
Публикация использует тот же артефакт после успешных тестов и сборки.

1. Включите GitHub Actions в репозитории. Ветка разработки — `petrovich_2`.
2. Настройте rulesets для `petrovich_2`, `main`, `release/*`, `legacy/*`.
   Для тегов `v*` создайте активный ruleset с ограничением права создания
   релизных тегов. Задание публикации требует `github.ref_protected == true`.
3. Создайте окружение GitHub `pypi`, разрешите deployment только из тегов `v*`.
4. В настройках существующего проекта Petrovich на PyPI добавьте GitHub
   Trusted Publisher: owner `damirazo`, repository `Petrovich`, workflow
   `ci.yml`, environment `pypi`. Постоянный API-токен для GitHub не нужен.
5. Подготовьте `release/2.0`, установите версию `2.0.0` в `pyproject.toml`,
   дождитесь зелёной сборки и отправьте тег `v2.0.0` на проверенный коммит.

```sh
git switch -c release/2.0 petrovich_2
# Подготовьте и проверьте релиз, установите version = "2.0.0".
git add pyproject.toml
git commit -m "Prepare 2.0.0 release"
git push origin release/2.0
# После зелёного pipeline:
git tag -a v2.0.0 -m "Petrovich 2.0.0"
git push origin v2.0.0
```

Push `petrovich_2` не публикует пакет. Неподходящие версии и несовпадение тега
с `pyproject.toml` останавливают сборку. Без настроенного Trusted Publisher
публикация не пройдёт. Повторно загружать одну версию нельзя — выпускайте patch.
См. [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## Альтернативная настройка GitLab и PyPI

1. Подключите существующий проект GitLab и Docker runner для официальных
   образов `python:3.12-slim`, `3.13-slim`, `3.14-slim`.
2. Выберите `petrovich_2` основной веткой разработки в настройках проекта.
   Защитите `petrovich_2`, `main`, `release/*`, `legacy/*` и теги `v*`.
   Право создания релизных тегов выдайте только сопровождающим релизы.
3. В PyPI создайте токен с правом публикации существующего проекта `Petrovich`.
   В GitLab Settings → CI/CD → Variables сохраните его как `TWINE_PASSWORD`,
   с флагами Masked и Protected и scope окружения `pypi`.
   Не записывайте токен в git и не передавайте его в чат.
4. При наличии этой функции GitLab ограничьте доступ к окружению `pypi`.
5. Проверьте конфигурацию в GitLab CI Lint, дождитесь успешного pipeline
   release-ветки. Обновите версию в `pyproject.toml`, сделайте коммит,
   затем создайте и отправьте соответствующий тег.

```sh
git switch -c release/2.0 petrovich_2
# Подготовьте и проверьте релиз, установите version = "2.0.0".
git add pyproject.toml
git commit -m "Prepare 2.0.0 release"
git push gitlab release/2.0
# После зелёного pipeline:
git tag -a v2.0.0 -m "Petrovich 2.0.0"
git push gitlab v2.0.0
```

Сборка проверяет метаданные через `twine check --strict`, устанавливает wheel
в чистое окружение и проверяет включённые правила. Публикация использует артефакты
этой сборки. Секрет доступен только при запуске на защищённом теге.
Версию PyPI нельзя перезаписать: для исправлений выпускайте новый patch.

Справочники: [GitLab CI YAML](https://docs.gitlab.com/ci/yaml/),
[Twine](https://twine.readthedocs.io/en/stable/).

## Обновление встроенного снимка

Выберите и просмотрите коммит в `petrovich/petrovich-rules`.
Вызовите `petrovich rules update --output src/petrovich/data/rules.json --ref SHA`.
Обновите `DEFAULT_REF` и `data/PROVENANCE.json` (commit, url, sha256), сохраните
лицензию источника, запустите тесты и оформите отдельный pull request.
Обновление пользовательского файла не меняет встроенный снимок пакета.
