from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

def test_cart_functionality(browser, base_url, wait):
    # 웹사이트 접속
    browser.get(base_url)

    # 페이지 로딩 대기 (확인: readyState가 complete일 때까지 기다리기)
    while browser.execute_script('return document.readyState') != 'complete':
        time.sleep(1)

    # 대기 시간을 30초로 설정
    wait = WebDriverWait(browser, 30)

    # 1. "카트에 담기" 버튼을 찾고 클릭
    try:
        add_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/cart/toggle/5']//button[text()='카트에 담기']"))
        )
        add_button.click()
        time.sleep(2)  # 클릭 후 2초 대기
    except TimeoutException as e:
        print("Add to Cart 버튼을 찾을 수 없습니다.")
        print(browser.page_source)  # 페이지 소스 출력하여 디버깅
        browser.save_screenshot("add_to_cart_fail.png")  # 스크린샷 찍기
        raise e

    # 2. 카트 아이템 수가 정상적으로 업데이트될 때까지 대기
    try:
        # 카트 페이지로 이동하여 카트 아이템 수 확인
        cart_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/cart')]"))
        )
        cart_button.click()

        # 페이지 리프레시 또는 추가 대기
        wait.until(lambda driver: "Cart (1)" in driver.page_source)  # 카트 아이템 수가 1로 변경될 때까지 기다림
        
        cart_count_text = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart')]"))
        ).text
        print("카트 아이템 수: ", cart_count_text)
        assert "Cart (1)" in cart_count_text, f"Expected cart count to be 'Cart (1)', but got {cart_count_text}"
    except TimeoutException as e:
        print("카트 아이템 수를 찾을 수 없습니다.")
        print(browser.page_source)  # 페이지 소스 출력하여 디버깅
        browser.save_screenshot("cart_check_fail.png")  # 스크린샷 찍기
        raise e

    # 3. "카트에서 제거" 버튼을 찾아서 클릭
    try:
        # "카트에서 제거" 버튼이 나타날 때까지 대기
        remove_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='카트에서 제거']"))
        )
        remove_button.click()
        time.sleep(2)  # 클릭 후 2초 대기
    except TimeoutException as e:
        print("Remove from Cart 버튼을 찾을 수 없습니다.")
        print(browser.page_source)  # 페이지 소스 출력하여 디버깅
        browser.save_screenshot("remove_from_cart_fail.png")  # 스크린샷 찍기
        raise e

    # 4. 카트가 비었는지 확인
    try:
        cart_count_text = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart')]"))
        ).text
        print("카트 아이템 수: ", cart_count_text)
        assert "Cart (0)" in cart_count_text, f"Expected cart count to be 'Cart (0)', but got {cart_count_text}"
    except TimeoutException as e:
        print("카트 아이템 수를 찾을 수 없습니다.")
        print(browser.page_source)  # 페이지 소스 출력하여 디버깅
        browser.save_screenshot("cart_empty_fail.png")  # 스크린샷 찍기
        raise e
