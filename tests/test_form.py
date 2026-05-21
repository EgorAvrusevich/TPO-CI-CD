import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=options)
    yield d
    d.quit()


def get_index_path():
    return "file://" + os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "index.html")
    )


class TestContactForm:
    def test_page_title(self, driver):
        """Заголовок страницы содержит 'Контактная форма'."""
        driver.get(get_index_path())
        assert "Контактная форма" in driver.title

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

    def test_empty_form_shows_error(self, driver):
        """Отправка пустой формы показывает сообщение об ошибке."""
        driver.get(get_index_path())
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "submit-btn"))).click()
        result = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".message.error"))
        )
        assert "заполните все поля" in result.text.lower()
