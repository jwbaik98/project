from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from app import app, USERS, get_product
import time
import pytest

# 🌟 중요: 상대 경로(.)를 사용하여 app.py 모듈을 임포트합니다. get_product 함수를 포함합니다.


# ----------------------------------------------------
# 1. 필수 Fixture: client 정의 (test_login.py와 동일하게 유지)
# ----------------------------------------------------
@pytest.fixture
def client():
    """테스트용 Flask 클라이언트 생성 및 환경 설정"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    original_users = USERS.copy()

    with app.test_client() as client:
        yield client

    USERS.clear()
    USERS.update(original_users)


# ----------------------------------------------------
# 2. 통합 Fixture: login_test_env 정의 (test_login.py와 동일하게 유지)
# ----------------------------------------------------
@pytest.fixture
def login_test_env(client):
    """로그인 테스트에 필요한 환경 및 데이터를 통합 제공합니다."""
    test_username = "fixture_testuser"
    test_password = "fixture_password123"
    USERS[test_username] = {"password": test_password}
    return client, test_username, test_password


# ----------------------------------------------------
# 3. 상품 상세 정보 및 카트 연동 테스트 함수 (5가지)
# ----------------------------------------------------

def test_product_detail_existing(client):
    """유효한 상품 ID로 상품 상세 페이지 접근 테스트"""
    existing_pid = 1
    product = get_product(existing_pid)
    response = client.get(f'/product/{existing_pid}')
    assert response.status_code == 200
    assert product["name"].encode('utf-8') in response.data


def test_product_detail_non_existent(client):
    """존재하지 않는 상품 ID로 접근 시 메인 페이지로 리디렉션되는지 테스트"""
    non_existent_pid = 999
    response = client.get(f'/product/{non_existent_pid}', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


# --- 카트 연동 테스트 (인증 담당 범위) ---

def test_toggle_cart_unauthenticated(client):
    """비로그인 상태에서 카트 추가 시도 시 /login으로 리디렉션되는지 테스트 (인증 게이트웨이 검증)"""
    test_pid = 2
    response = client.post(f'/cart/toggle/{test_pid}', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].startswith('/login')
    assert "next=" in response.headers['Location']


def test_toggle_cart_add_success(login_test_env):
    """로그인 상태에서 장바구니에 상품을 성공적으로 추가하고 세션 상태가 변하는지 확인합니다."""
    client, username, password = login_test_env
    test_pid = 3
    client.post('/login', data={"username": username, "password": password})
    client.post(f'/cart/toggle/{test_pid}')

    with client.session_transaction() as sess:
        assert 'cart' in sess
        assert str(test_pid) in sess['cart']


def test_toggle_cart_remove_success(login_test_env):
    """카트에 있는 상품을 제거할 때 성공적으로 세션에서 제거되는지 테스트"""
    client, username, password = login_test_env
    test_pid = 3
    client.post('/login', data={"username": username, "password": password})
    client.post(f'/cart/toggle/{test_pid}')  # 상품 미리 추가

    client.post(f'/cart/toggle/{test_pid}')  # 제거 요청

    with client.session_transaction() as sess:
        assert str(test_pid) not in sess['cart']
        assert len(sess['cart']) == 0