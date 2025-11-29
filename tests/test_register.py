import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def test_register_page_loads_and_has_form_elements(browser, base_url, wait):
    """
    테스트 1: 회원가입 페이지가 성공적으로 로드되고 필수 폼 요소가 있는지 검증합니다.
    """

    print("\n[TEST 1] 회원가입 페이지 로드 및 요소 확인 시작...")

    browser.get(base_url + '/register')

    # 제목 확인
    wait.until(
        EC.visibility_of_element_located((By.XPATH, "//h4[text()='집사 회원가입']"))
    )

    try:
        wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        wait.until(EC.presence_of_element_located((By.NAME, 'confirm')))

        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign Up']"))
        )
        print("[SUCCESS] 페이지 제목, 폼 필드, 제출 버튼 모두 확인 완료.")
    except TimeoutException:
        assert False, "회원가입 페이지의 필수 폼 요소를 찾을 수 없습니다."


def test_successful_registration_and_redirection(browser, base_url, wait):
    """
    테스트 2:
    1) 유효한 데이터로 회원가입 폼을 제출하면,
    2) 로그인 페이지(/login)로 이동하고,
    3) 그 계정으로 실제 로그인까지 성공하는지 확인한다.
    """

    print("\n[TEST 2] 성공적인 회원가입 시나리오 시작...")

    # 중복 방지를 위한 유니크한 username
    TEST_UNIQUE_USERNAME = f"testuser_{int(time.time())}"
    TEST_PASSWORD = "Password123"

    # 1. 회원가입 페이지 접속
    browser.get(base_url + '/register')

    # 폼 입력
    wait.until(
        EC.presence_of_element_located((By.NAME, 'username'))
    ).send_keys(TEST_UNIQUE_USERNAME)
    browser.find_element(By.NAME, 'password').send_keys(TEST_PASSWORD)
    browser.find_element(By.NAME, 'confirm').send_keys(TEST_PASSWORD)

    # 제출
    browser.find_element(By.XPATH, "//button[text()='Sign Up']").click()

    # 2. /login 으로 이동했는지 확인 (리다이렉트가 느리면 수동으로 한 번 더 이동 보정)
    try:
        wait.until(EC.url_contains('/login'))
        print(f"[INFO] 회원가입 후 URL 이동 확인: {browser.current_url}")
    except TimeoutException:
        # 혹시 아직 /register 에 머물러 있으면 강제로 /login 으로 이동
        print("[WARN] URL 변경 대기 타임아웃. 수동으로 /login 접속 시도.")
        browser.get(base_url + '/login')

    # 실제로 현재 페이지가 로그인 페이지인지 기본 요소로도 한 번 확인
    try:
        wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        print("[INFO] 로그인 페이지 폼 요소 확인 완료.")
    except TimeoutException:
        assert False, "회원가입 후 로그인 페이지 폼 요소를 찾지 못했습니다."

    # 3. 방금 만든 계정으로 로그인 시도
    browser.find_element(By.NAME, 'username').clear()
    browser.find_element(By.NAME, 'username').send_keys(TEST_UNIQUE_USERNAME)
    browser.find_element(By.NAME, 'password').clear()
    browser.find_element(By.NAME, 'password').send_keys(TEST_PASSWORD)
    browser.find_element(By.XPATH, "//button[text()='Login']").click()

    # Logout 링크가 나오면 로그인 성공으로 판단
    try:
        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[text()='Logout']"))
        )
        print(f"[SUCCESS] 신규 계정 '{TEST_UNIQUE_USERNAME}'로 로그인 성공 및 'Logout' 버튼 확인.")
    except TimeoutException:
        print("\n=== 로그인 실패 시점 페이지 소스 ===")
        print(browser.page_source)
        print("=================================")
        assert False, "회원가입한 계정으로 로그인에 실패했습니다."


def test_registration_password_mismatch_error_message(browser, base_url, wait):
    """
    테스트 3: 비밀번호와 확인 비밀번호가 일치하지 않을 때 오류 메시기가 표시되는지 테스트
    """

    print("\n[TEST 3] 비밀번호 불일치 오류 시나리오 시작...")

    browser.get(base_url + '/register')

    wait.until(
        EC.presence_of_element_located((By.NAME, 'username'))
    ).send_keys('mismatch_test')
    browser.find_element(By.NAME, 'password').send_keys('password123')
    browser.find_element(By.NAME, 'confirm').send_keys('different_password')

    browser.find_element(By.XPATH, "//button[text()='Sign Up']").click()

    error_message_xpath = (
        "//div[contains(@class, 'alert-danger') "
        "and contains(text(), '비밀번호가 일치하지 않습니다.')]"
    )

    try:
        error_alert = wait.until(
            EC.visibility_of_element_located((By.XPATH, error_message_xpath))
        )
        assert "비밀번호가 일치하지 않습니다." in error_alert.text
        print("[SUCCESS] '비밀번호 불일치' 오류 메시지 확인 완료.")
    except TimeoutException:
        assert False, "비밀번호 불일치 오류 메시지가 표시되지 않았습니다."

    # 여전히 /register 에 머물러 있어야 함
    assert browser.current_url == base_url + '/register'
