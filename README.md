# Petrovich

Склонение русских имён, фамилий и отчеств по падежам. Python 3.12 и новее.
Библиотека использует [общие правила Petrovich](https://github.com/petrovich/petrovich-rules)
и работает без сети и без дополнительных runtime-зависимостей.

Новая реализация разрабатывается в `petrovich_2`. Ветка `legacy/1.x` сохраняет
исходный код на момент начала миграции; `master` и существующие теги не изменены.
Новая версия — `3.0.0`. Прежняя версия `2.0.1` для Python 3.6+ остаётся в PyPI.

## Установка

Из рабочей копии ветки `petrovich_2`:

```sh
python -m pip install .
```

После публикации стабильной версии в PyPI:

```sh
python -m pip install 'petrovich>=3,<4'
```

Для старого приложения на Python 2 закрепите `petrovich==1.0.0`,
для прежней реализации на Python 3.6+ — `petrovich==2.0.1`.
См. [миграцию](docs/migration.md) и [процесс разработки](docs/development.md).

## Использование

```python
from petrovich import Petrovich, Case, Gender

p = Petrovich()
print(p.lastname("Алексеев", Case.GENITIVE, Gender.MALE))  # Алексеева
print(p.firstname("Анна-Мария", Case.DATIVE, Gender.FEMALE))  # Анне-Марии
print(p.middlename("Васильевич", Case.INSTRUMENTAL))  # Васильевичем
```

Методы `firstname`, `lastname`, `middlename` принимают имя в именительном падеже,
целевой `Case` и необязательный `Gender`. Поддерживаются `GENITIVE`, `DATIVE`,
`ACCUSATIVE`, `INSTRUMENTAL`, `PREPOSITIONAL` и `NOMINATIVE`.
`Gender.MALE` и `Gender.FEMALE` задают род явно; общие правила `ANDROGYNOUS`
применяются к обоим родам. Без рода используется эвристика порядка правил;
это не полноценное определение пола. Для неоднозначных имён задавайте род явно.

Пробелы и дефисы сохраняются, исключения применяются к каждому компоненту.
Слова в верхнем регистре остаются в верхнем регистре. Неизвестные слова
возвращаются без изменения, если подходящих правил нет. Пустое значение
вызывает `ValueError`, значение не строкового типа — `TypeError`.

## Правила и CLI

В wheel и sdist включён проверенный снимок правил; Git submodule не нужен.
По умолчанию загрузка локальная. Источник и SHA-256 снимка записаны в
`src/petrovich/data/PROVENANCE.json`, лицензия — рядом.

```sh
petrovich rules validate
petrovich rules update --output ./rules.json --ref master
petrovich rules validate ./rules.json
petrovich inflect lastname Алексеев --case genitive --gender male
petrovich inflect firstname Пётр --case dative --rules ./rules.json
```

Для воспроизводимого обновления укажите SHA коммита вместо `master`.
Без `--ref` используется зафиксированный в библиотеке коммит.
Возможны `--url https://.../rules.json`, `--sha256 HEX` и `--timeout 30`.
`--ref` и `--url` взаимоисключающие. Размер документа ограничен 2 MiB.
CLI возвращает 0 при успехе, 1 при ошибке загрузки/валидации и 2 при неверных аргументах.
Эквивалентная точка входа: `python -m petrovich`.

Обновление проверяет документ до атомарной замены файла. Ошибка сети, JSON,
контрольной суммы или записи оставляет прежний файл на месте. Пакет в
`site-packages` автоматически не изменяется. Чтобы использовать обновление:

```python
p = Petrovich(rules_path="./rules.json")
```

Созданный экземпляр хранит неизменяемый снимок правил. После обновления файла
создайте новый экземпляр. Конкурентные обновления одного файла координирует
приложение: действует последнее завершённое обновление.

## Асинхронный ввод-вывод

```python
import asyncio
from petrovich import Petrovich, Case
from petrovich.rules import aupdate_rules


async def main():
    await aupdate_rules("./rules.json")
    p = await Petrovich.create("./rules.json")
    print(p.firstname("Павел", Case.GENITIVE))


asyncio.run(main())
```

`aload_rules`, `aupdate_rules` и `Petrovich.create` выносят файловый и сетевой
ввод-вывод в рабочий поток через `asyncio.to_thread`. Отмена coroutine не прерывает
операцию потока: обновление может завершиться после отмены.
Склонение — короткая синхронная операция без ввода-вывода. Для больших пакетов
данных приложение может использовать `asyncio.to_thread` или пул процессов.

## Разработка

```sh
python -m pip install -e '.[dev]'
python -m pytest --cov=petrovich --cov-branch
ruff check .
ruff format --check .
mypy
python -m build
python -m twine check --strict dist/*
```

GitHub Actions проверяет Python 3.12, 3.13 и 3.14, собирает wheel/sdist и публикует
защищённые релизные теги в PyPI через Trusted Publishing. Также сохранена
конфигурация GitLab CI. Настройка доступа и Git flow описаны в
[docs/development.md](docs/development.md).

Лицензия кода и правил — MIT.
