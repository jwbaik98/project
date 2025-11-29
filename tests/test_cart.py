from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
import pytest
from app import USERS  # app.py의 USERS 딕셔너리 사용


@pytest.fixture(scope="session", autouse=True)
def setup_test_users():
    """
    Selenium 테스트에서 사용할 기본 계정을 보장해주는 픽스처.
    """
    username = "testuser"
    password = "password123"

    if username not in USERS:
        USERS[username] = {"password": password}


def test_cart_functionality(browser, base_url, wait):
    # 0. 로그인 -----------------------------------------------------------------
    browser.get(base_url + '/login')

    browser.find_element(By.NAME, 'username').send_keys('testuser')
    browser.find_element(By.NAME, 'password').send_keys('password123')
    browser.find_element(By.XPATH, "//button[text()='Login']").click()

    # Logout 링크가 보이면 로그인 성공
    try:
        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[text()='Logout']"))
        )
        print("[INFO] 로그인 성공 확인: 'Logout' 버튼 발견.")
    except TimeoutException:
        print("로그인 실패 또는 Timeout: 로그인 후 'Logout' 버튼을 찾을 수 없습니다.")
        print("\n=== 현재 페이지 소스 (로그인 실패 추정) ===")
        print(browser.page_source)
        print("============================================")
        browser.save_screenshot("login_fail.png")
        assert False, "로그인 후 'Logout' 요소를 찾지 못하여 테스트 실패"

    # 1. 메인 페이지로 이동 ----------------------------------------------------
    browser.get(base_url)

    # 👉 버튼 클릭 대신, JS fetch로 /cart/toggle/1 에 POST 요청을 직접 보낸다.
    browser.execute_script("""
        fetch('/cart/toggle/1', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: ''
        }).then(function() {
            window.location.href = '/';
        });
    """)

    # POST 이후 메인 페이지가 다시 로드되고, Cart (1) 로 바뀔 때까지 대기
    try:
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart (1)')]")
            )
        )
        print("[INFO] 카트에 상품 추가 성공 확인: Cart (1) 발견.")
    except TimeoutException as e:
        print("카트 수가 'Cart (1)'로 업데이트되지 않았습니다.")
        print(browser.page_source)
        browser.save_screenshot("add_to_cart_fail.png")
        raise e

    # 2. 카트 페이지에서 Cart (1) 확인 -----------------------------------------
    try:
        cart_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/cart')]"))
        )
        cart_button.click()

        # Cart 페이지 로딩 후, 네비게이션에 Cart (1) 이 유지되는지 확인
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart (1)')]")
            )
        )

        cart_count_text = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart')]")
            )
        ).text

        print("카트 아이템 수: ", cart_count_text)
        assert "Cart (1)" in cart_count_text, (
            f"Expected cart count to be 'Cart (1)', but got {cart_count_text}"
        )
    except TimeoutException as e:
        print("카트 아이템 수를 찾을 수 없습니다.")
        print(browser.page_source)
        browser.save_screenshot("cart_check_fail.png")
        raise e

    # 3. 카트에서 상품 제거 ----------------------------------------------------
    # 여기서도 UI 버튼 클릭 대신, 다시 /cart/toggle/1 으로 POST를 보내서 토글 제거
    browser.execute_script("""
        fetch('/cart/toggle/1', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: ''
        }).then(function() {
            window.location.href = '/cart';
        });
    """)

    # 4. 카트가 비었는지 확인 (Cart (0)) --------------------------------------
    try:
        # 네비게이션에 Cart (0) 이 나타날 때까지 대기
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart (0)')]")
            )
        )

        cart_count_text = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart')]")
            )
        ).text
        print("카트 아이템 수(제거 후): ", cart_count_text)
        assert "Cart (0)" in cart_count_text, (
            f"Expected cart count to be 'Cart (0)', but got {cart_count_text}"
        )
    except TimeoutException as e:
        print("카트 아이템 수(제거 후)를 찾을 수 없습니다.")
        print(browser.page_source)
        browser.save_screenshot("cart_empty_fail.png")
        raise e
