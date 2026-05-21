# Лабораторная работа №11 — Настройка CI/CD с использованием GitHub Actions

## Цель работы

Настроить непрерывную интеграцию (CI) и непрерывную доставку (CD) для веб-приложения с использованием GitHub Actions: автоматический запуск UI-тестов при каждом пуше и автоматический деплой на GitHub Pages при слиянии в ветку `main`.

## Структура проекта

```
Lab11/
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI-пайплайн: запуск тестов
│       └── deploy.yml      # CD-пайплайн: деплой на GitHub Pages
├── tests/
│   ├── __init__.py
│   └── test_form.py        # Selenium-тесты формы
├── index.html              # Веб-страница с контактной формой
├── requirements.txt        # Зависимости Python
├── .gitignore              # Исключения для Git
└── README.md               # Документация
```

## Описание веб-приложения

Разработана простая веб-страница — **контактная форма** с полями:

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | `text` | Имя пользователя |
| `email` | `email` | Электронная почта |
| `message` | `textarea` | Текст сообщения |

**Валидация на стороне клиента (JavaScript):**
- Все поля обязательны — при пустой отправке выводится сообщение: *«Пожалуйста, заполните все поля!»*
- Email должен содержать символ `@` — иначе: *«Введите корректный email!»*
- При успешной отправке: *«Спасибо, {имя}! Сообщение отправлено.»*

## Модульные тесты (Selenium)

Файл: [tests/test_form.py](tests/test_form.py)

Написано **4 автоматизированных теста** пользовательского интерфейса с использованием Selenium WebDriver:

### Тест 1 — `test_page_title`

```python
def test_page_title(self, driver):
    """Заголовок страницы содержит 'Контактная форма'."""
    driver.get(get_index_path())
    assert "Контактная форма" in driver.title
```

Проверяет, что заголовок HTML-страницы (`<title>`) содержит текст «Контактная форма».

### Тест 2 — `test_form_fields_present`

```python
def test_form_fields_present(self, driver):
    """На странице есть все обязательные поля формы."""
    driver.get(get_index_path())
    wait = WebDriverWait(driver, 10)
    name = wait.until(EC.presence_of_element_located((By.ID, "name")))
    email = driver.find_element(By.ID, "email")
    message = driver.find_element(By.ID, "message-text")
    submit = driver.find_element(By.ID, "submit-btn")
    assert name.is_displayed()
    assert email.is_displayed()
    assert message.is_displayed()
    assert submit.is_displayed()
```

Проверяет наличие и видимость всех элементов формы: поле имени, email, текстовое поле сообщения и кнопка отправки.

### Тест 3 — `test_successful_submission`

```python
def test_successful_submission(self, driver):
    """Успешная отправка формы с заполненными полями."""
    driver.get(get_index_path())
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("Иван")
    driver.find_element(By.ID, "email").send_keys("ivan@test.com")
    driver.find_element(By.ID, "message-text").send_keys("Привет!")
    driver.find_element(By.ID, "submit-btn").click()
    result = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".message.success"))
    )
    assert "Спасибо" in result.text
```

Заполняет все поля формы валидными данными, нажимает кнопку отправки и проверяет появление сообщения об успехе.

### Тест 4 — `test_empty_form_shows_error`

```python
def test_empty_form_shows_error(self, driver):
    """Отправка пустой формы показывает сообщение об ошибке."""
    driver.get(get_index_path())
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "submit-btn"))).click()
    result = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".message.error"))
    )
    assert "заполните все поля" in result.text.lower()
```

Нажимает кнопку отправки без заполнения полей и проверяет появление сообщения об ошибке.

### Запуск тестов локально

```bash
pip install -r requirements.txt
cd tests
python -m pytest test_form.py -v
```

## Настройка CI (Continuous Integration)

Файл: [.github/workflows/ci.yml](.github/workflows/ci.yml)

### Триггеры

```yaml
on:
  push:
    branches: [main, dev, "fix/**"]
  pull_request:
    branches: [main, dev]
```

Тесты запускаются автоматически при:
- **push** в ветки `main`, `dev` или любую ветку вида `fix/...`
- создании **pull request** в ветки `main` или `dev`

### Шаги пайплайна

| Шаг | Действие |
|-----|----------|
| 1. Checkout | Получение кода из репозитория |
| 2. Setup Python | Установка Python 3.11 |
| 3. Install dependencies | Установка `selenium` и `pytest` из `requirements.txt` |
| 4. Setup Chrome | Установка браузера Chrome в контейнер |
| 5. Run tests | Запуск `pytest tests/ -v --tb=short` |

## Настройка CD (Continuous Delivery)

Файл: [.github/workflows/deploy.yml](.github/workflows/deploy.yml)

### Триггер

```yaml
on:
  push:
    branches: [main]
```

Деплой происходит **только** при пуше в ветку `main` (т.е. после успешного слияния pull request).

### Шаги пайплайна

| Шаг | Действие |
|-----|----------|
| 1. Checkout | Получение кода |
| 2. Setup Pages | Настройка GitHub Pages |
| 3. Upload artifact | Загрузка файлов приложения как артефакта |
| 4. Deploy | Публикация на GitHub Pages |

### Разграничение прав

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

Workflow имеет минимально необходимые права: чтение кода и запись в Pages.

## Работа с ветками

### Модель ветвления

```
main  ←── dev  ←── fix/update-form-text
  ↑          ↑
  │          └── PR #2 (финальная проверка)
  └── PR #1 (ревью изменений)
```

| Ветка | Назначение |
|-------|-----------|
| `main` | Стабильная  production-версия. Прямые коммиты запрещены. |
| `dev` | Основная ветка для разработки. Все изменения попадают сюда через PR. |
| `fix/*` | Ветки для конкретных задач (исправление багов, добавление фич). Создаются от `dev`. |

### Порядок работы

1. Создать ветку `fix/...` от `dev`
2. Внести изменения, сделать коммит и пуш
3. Создать **Pull Request** `fix/...` → `dev`
4. GitHub Actions запускает тесты автоматически
5. Если тесты прошли — выполнить **Merge** в `dev`
6. Создать **Pull Request** `dev` → `main`
7. Тесты запускаются повторно для финальной проверки
8. После успеха — **Merge** в `main`, автоматический деплой на GitHub Pages

### Текущая структура коммитов

```
* 3a7b820  chore: add .gitignore
| * 8ff34d7  fix: обновлён заголовок формы и текст кнопки
|/
* cc0b90c  Initial commit: add web form, Selenium tests, and CI/CD workflows
```

Ветка `fix/update-form-text` содержит изменения:
- Заголовок: «Контактная форма» → «Форма обратной связи»
- Кнопка: «Отправить» → «Отправить сообщение»
- Тест `test_page_title` обновлён под новый заголовок

## Проверка работоспособности тестов

### Тесты проходят (ветка main)

```
test_form.py::TestContactForm::test_page_title            PASSED
test_form.py::TestContactForm::test_form_fields_present   PASSED
test_form.py::TestContactForm::test_successful_submission PASSED
test_form.py::TestContactForm::test_empty_form_shows_error PASSED
```

### Тесты падают при ошибке в коде

При замене заголовка на некорректный:

```
test_form.py::TestContactForm::test_page_title            FAILED
assert 'Контактная форма' in 'Lab11 — Сломанный Заголовок'
```

Тест `test_page_title` обнаруживает несоответствие ожидаемого заголовка и фактического.

## Использованные технологии

| Технология | Назначение |
|-----------|-----------|
| **HTML5 / CSS3** | Вёрстка и стилизация формы |
| **JavaScript** | Клиентская валидация формы |
| **Selenium WebDriver** | Автоматизация браузера для UI-тестов |
| **pytest** | Фреймворк для написания и запуска тестов |
| **GitHub Actions** | Платформа CI/CD |
| **GitHub Pages** | Хостинг статического сайта |
| **Git** | Система контроля версий |

## Выводы

В ходе лабораторной работы было выполнено:

1. ✅ Разработана веб-страница с контактной формой и клиентской валидацией
2. ✅ Написано 4 автоматизированных UI-теста с использованием Selenium
3. ✅ Настроен CI-пайплайн (GitHub Actions) для автоматического запуска тестов при push/PR
4. ✅ Настроен CD-пайплайн для автоматического деплоя на GitHub Pages при слиянии в `main`
5. ✅ Организована работа с ветками: `main`, `dev`, `fix/*`
6. ✅ Подтверждено, что тесты проходят при корректном коде и падают при ошибках
