# test_login.py
# -*- coding: utf-8 -*-\r\n
import pytest
from flask import session

# 🌟 중요: app.py 모듈을 임포트합니다.
from app import app, USERS

# ----------------------------------------------------
# 1. 필수 Fixture: client 정의 (두 파일에 모두 필요)
# ----------------------------------------------------
@pytest.fixture
def client():
    """테스트용 Flask 클라이언트 생성 및 환경 설정"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    # USERS 딕셔너리 백업
    original_users = USERS.copy()

    with app.test_client() as client:
        yield client

        # Teardown: USERS 딕셔너리 복원
    USERS.clear()
    USERS.update(original_users)


# ----------------------------------------------------
# 2. 통합 Fixture: login_test_env 정의 (두 파일에 모두 필요)
# ----------------------------------------------------
@pytest.fixture
def login_test_env(client):
    """로그인 테스트에 필요한 환경 및 데이터를 통합 제공합니다."""
    test_username = "fixture_testuser"
    test_password = "fixture_password123"
    USERS[test_username] = {"password": test_password}
    return client, test_username, test_password


# ----------------------------------------------------
# 3. 인증 시스템 테스트 함수 (6가지)
# ----------------------------------------------------

def test_login_page_get(client):
    """로그인 페이지 GET 요청 테스트"""
    response = client.get('/login')
    assert response.status_code == 200
    assert "집사 로그인".encode('utf-8') in response.data


def test_login_success(login_test_env):
    """유효한 자격 증명으로 로그인 성공 테스트"""
    client, username, password = login_test_env
    response = client.post('/login', data={"username": username, "password": password}, follow_redirects=True)
    assert response.status_code == 200
    assert "로그인 성공!".encode('utf-8') in response.data


def test_login_invalid_credential(login_test_env):
    """잘못된 비밀번호로 로그인 실패 테스트"""
    client, username, _ = login_test_env
    response = client.post('/login', data={"username": username, "password": "wrong"}, follow_redirects=True)
    assert response.status_code == 200
    assert "아이디 또는 비밀번호가 올바르지 않습니다.".encode('utf-8') in response.data


def test_login_next_url(login_test_env):
    """'next' URL 파라미터가 있을 때 로그인 후 리디렉션 테스트"""
    client, username, password = login_test_env
    next_url = "/checkout"
    response = client.post(f'/login?next={next_url}', data={"username": username, "password": password},
                           follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == next_url


def test_register_success(client):
    """회원가입 성공 후 리디렉션 및 사용자 등록 확인 테스트"""
    new_username = "new_cat_butler"
    new_password = "password123"
    response = client.post('/register',
                           data={"username": new_username, "password": new_password, "confirm": new_password},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "회원가입 성공! 이제 로그인해주세요.".encode('utf-8') in response.data
    assert new_username in USERS


def test_logout_success(client):
    """로그아웃 시 세션 클리어 및 /index 리디렉션 테스트"""
    with client.session_transaction() as sess:
        sess['user_id'] = 'temp_user'
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert "로그아웃되었습니다.".encode('utf-8') in response.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess