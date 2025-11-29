import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 💡 app.py에서 Flask 앱 인스턴스와 USERS 딕셔너리 가져오기
from app import app, USERS 

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
    return WebDriverWait(browser, 20)

# 테스트 실패 시 스크린샷 저장
def pytest_runtest_makereport(item, call):
    if call.when == "call" and call.excinfo is not None:
        browser = item.funcargs.get("browser")
        if browser:
            ts = time.strftime("%Y%m%d-%H%M%S")
            filename = f"screenshot-{item.name}-{ts}.png"
            os.makedirs("screenshot", exist_ok=True)
            browser.save_screenshot(os.path.join("screenshot", filename))
            print(f"\n❌ Test failed. Screenshot saved to {os.path.join('screenshot', filename)}")

SELENIUM_TEST_USERNAME = "testuser"
SELENIUM_TEST_PASSWORD = "password123"

# ----------------------------------------------------
# 🛠️ Flask Client Fixtures (통합)
# ----------------------------------------------------

@pytest.fixture
def client():
    """
    모든 Flask Client 테스트를 위한 표준 클라이언트 Fixture.
    테스트 시작 전 app.USERS를 백업하고, 종료 후 복원하여 테스트 간 격리를 보장합니다.
    """
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key' # 세션 관리를 위해 필요
    
    # 💡 USERS 딕셔너리 백업
    original_users = USERS.copy() 

    with app.test_client() as client:
        # 테스트 전 Flask 세션을 깨끗하게 시작합니다.
        with client.session_transaction() as sess:
            sess.clear() 
        yield client

    # 💡 Teardown: USERS 딕셔너리 복원
    USERS.clear()
    USERS.update(original_users)
    

@pytest.fixture
def login_test_env(client):
    """
    로그인 관련 테스트에 필요한 환경 및 데이터를 제공합니다.
    (client Fixture의 USERS 백업/복원 기능에 의존)
    """
    test_username = "fixture_user_id"
    test_password = "fixture_password_123"
    
    # client Fixture에 의해 USERS가 복원되므로, 여기에 사용자 등록
    USERS[test_username] = {"password": test_password} 
    
    return client, test_username, test_password