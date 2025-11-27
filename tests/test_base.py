import pytest
from app import app, USERS # app.py에서 필요한 것들을 import 합니다.
from flask import session, flash
import re  # 파일 상단에 이 모듈을 import 해야 합니다.
from flask import flash, get_flashed_messages # app.py에서 import 했겠지만, 명시적으로 확인

# --- Pytest Fixture: 테스트 환경 설정 ---

@pytest.fixture
def client():
    """
    Flask 애플리케이션의 테스트 클라이언트를 생성하고 환경을 초기화합니다.
    """
    app.config['TESTING'] = True
    app.secret_key = "test-secret-key"
    
    # 테스트용 임시 사용자 등록
    USERS.clear()
    USERS['testuser'] = {"password": 'password123'}

    with app.test_client() as client:
        # 테스트 시작 시 클라이언트 반환
        yield client 

# --- 헬퍼 함수: 세션 설정 ---
def login_test_user(client):
    """테스트를 위해 세션에 사용자 정보를 강제로 설정합니다."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'testuser'

# --- A. 기본 라우트 및 페이지 구조 테스트 ---

def test_base_layout_loads(client):
    """기본 레이아웃 (base.html)이 포함된 페이지가 정상 로드되는지 확인합니다."""
    # /index 라우트는 base.html을 상속받으므로, 이를 테스트합니다.
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    
    # 필수 HTML 요소 및 Bootstrap CSS CDN 링크 확인
    assert b"<!doctype html>" in response.data
    assert b"Resona Cat Shop" in response.data
    assert b"Bootstrap CSS CDN" in response.data

def test_navigation_links(client):
    """base.html에 정의된 주요 네비게이션 링크가 올바른 url_for를 사용하는지 확인합니다."""
    response = client.get('/')
    
    # Home 링크가 /로 연결되는지 확인
    assert b'<a class="nav-link" href="/">Home</a>' in response.data 
    # Cart 링크가 /cart로 연결되고 기본 카운트 0을 표시하는지 확인
    assert b'href="/cart">Cart (0)</a>' in response.data 
    # 비로그인 상태에서 Login 링크가 /login으로 연결되는지 확인
    assert b'<a class="nav-link" href="/login">Login</a>' in response.data 
    assert b'<a class="nav-link" href="/register">Sign Up</a>' in response.data 

# --- B. 로그인 상태에 따른 UI 변화 테스트 ---

def test_navbar_unauthenticated(client):
    """비로그인 상태 (current_user 없음)에서 내비게이션 바 확인."""
    response = client.get('/')
    # 로그인/회원가입 버튼이 보여야 함
    assert b"Login" in response.data
    assert b"Sign Up" in response.data
    # 사용자 이름이나 로그아웃 버튼은 보이지 않아야 함
    assert "집사," not in response.data.decode('utf-8')
    assert b"Logout" not in response.data

def test_navbar_authenticated(client):
    """로그인 상태 (current_user 있음)에서 내비게이션 바 확인."""
    # 테스트 사용자를 강제로 로그인 시킵니다.
    login_test_user(client)

    response = client.get('/')
    # 사용자 이름과 로그아웃 버튼이 보여야 함
    assert "집사, testuser\ub2d8" in response.data.decode('utf-8') # '님' 포함 확인
    assert b'href="/logout">Logout</a>' in response.data 
    # 로그인/회원가입 버튼은 보이지 않아야 함
    assert b"Login" not in response.data
    assert b"Sign Up" not in response.data

# --- C. 플래시 메시지 렌더링 테스트 ---
# tests/test_base.py 파일의 test_flash_messages_rendering 함수를 다음과 같이 수정합니다.

def test_flash_messages_rendering(client):
    """get_flashed_messages가 base.html에서 올바르게 렌더링되는지 확인합니다."""

    # 1. 플래시 메시지를 세션에 직접 설정하여 다음 요청에 메시지가 전달되도록 보장
    with client.session_transaction() as sess:
        # Flask는 '_flashes'라는 세션 키에 메시지를 (카테고리, 메시지) 튜플 리스트 형태로 저장합니다.
        sess['_flashes'] = [
            ('success', '성공 메시지입니다.'),
            ('warning', '경고 메시지입니다.')
        ]

    # 2. 클라이언트 요청 및 메시지 확인
    # 이 요청이 세션의 메시지를 읽어 HTML로 렌더링합니다.
    response = client.get('/')

    assert response.status_code == 200
    
    # response.data를 문자열로 변환하고, 정규 표현식을 사용해 모든 공백을 하나의 공백으로 대체합니다.
    html_content = response.data.decode('utf-8')
    cleaned_content = re.sub(r'\s+', ' ', html_content) 
    
    # 1. success 메시지 확인: 공백이 제거된 단순화된 문자열로 비교
    # (Jinja2 렌더링 시 메시지 앞뒤에 공백이 생길 수 있으므로, 비교 문자열에도 공백을 포함합니다.)
    assert '<div class="alert alert-success mb-2" role="alert"> 성공 메시지입니다. </div>' in cleaned_content
    
    # 2. warning 메시지 확인
    assert '<div class="alert alert-warning mb-2" role="alert"> 경고 메시지입니다. </div>' in cleaned_content

# --- D. 스크립트 로딩 테스트 ---

def test_bootstrap_js_loads(client):
    """Bootstrap JavaScript 번들 CDN이 올바르게 포함되었는지 확인합니다."""
    response = client.get('/')
    # Bootstrap JS CDN 링크 확인
    assert b'bootstrap.bundle.min.js' in response.data