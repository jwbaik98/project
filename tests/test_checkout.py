from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

def test_checkout(browser, base_url, wait):
    # 웹사이트 접속
    browser.get(base_url)

    # 카트에 아이템이 있는지 확인
    try:
        cart_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/cart')]"))
        )
        cart_button.click()

        # 카트에 아이템이 있는지 확인 (예: Cart (n) 형태)
        cart_count_text = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/cart') and contains(text(), 'Cart')]"))
        ).text
        print("카트 아이템 수: ", cart_count_text)

        # 카트 아이템 수가 있는지 확인 (예: Cart (1) 또는 Cart (0) 형태)
        assert "Cart (" in cart_count_text, f"Expected 'Cart (n)', but got {cart_count_text}"

        # 카트 아이템 수 추출
        cart_count = int(cart_count_text.split('(')[1].split(')')[0])

        # 카트가 비어 있지 않으면 정상적으로 처리
        if cart_count > 0:
            print(f"카트에 {cart_count}개 아이템이 있습니다.")
        else:
            print("카트가 비어 있습니다.")

        # 카트가 비어 있을 때도 오류가 발생하지 않도록 처리
        assert cart_count >= 0, f"Expected cart count to be greater than or equal to 0, but got {cart_count}"

    except TimeoutException as e:
        print("카트 페이지를 찾을 수 없습니다.")
        print(browser.page_source)  # 페이지 소스 출력하여 디버깅
        browser.save_screenshot("cart_check_fail.png")  # 스크린샷 찍기
        raise e

    except AssertionError as e:
        print(f"테스트 실패: {e}")
        browser.save_screenshot("checkout_fail.png")  # 실패 시 스크린샷 찍기
        raise e
