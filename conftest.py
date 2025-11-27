import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Pytest 옵션 추가
def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="http://127.0.0.1:5000",
        help="Target base URL"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser headless"
    )

# Base URL fixture
@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url")

# WebDriver fixture
@pytest.fixture(scope="session")
def browser(pytestconfig):
    headless = pytestconfig.getoption("--headless")

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # 최신 headless 모드
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    prefs = {
        "credentials_enable_service" : False,
        "profile.password_manager_enabled" : False
    }
    options.add_experimental_option("prefs", prefs)

    # ✅ 최신 방식으로 capability 설정
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()

# WebDriverWait fixture
@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 10)

# 테스트 실패 시 스크린샷 저장
def pytest_runtest_makereport(item, call):
    if call.when == "call" and call.excinfo is not None:
        browser = item.funcargs.get("browser")
        if browser:
            ts = time.strftime("%Y%m%d-%H%M%S")
            name = f"screenshot_{item.name}_{ts}.png"
            path = os.path.join(os.getcwd(), name)
            try:
                browser.save_screenshot(path)
                item.user_properties.append(("screenshot", path))
            except Exception:
                pass