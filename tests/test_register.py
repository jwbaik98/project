# test_register.py

import pytest
# 💡 실제 Flask 애플리케이션 인스턴스가 정의된 모듈에서 'app'을 가져옵니다.
# 예: from my_app import app
from app import app 

# ----------------------------------------------------
# 🛠️ Fixture: 테스트 클라이언트 설정
# ----------------------------------------------------

@pytest.fixture
def client():
    """테스트 클라이언트 설정 및 Flask 애플리케이션 컨텍스트 초기화"""
    # 애플리케이션을 테스트 모드로 설정
    app.config['TESTING'] = True
    
    # 세션 관리를 위해 SECRET_KEY 설정이 필요할 수 있습니다.
    # app.config['SECRET_KEY'] = 'test_secret_key' 
    
    with app.test_client() as client:
        yield client

# ----------------------------------------------------
# 📝 테스트 1: GET 요청 (페이지 로드)
# ----------------------------------------------------

def test_register_page_loads_successfully(client):
    """GET 요청 시 회원가입 페이지가 성공적으로 로드되고 필수 폼 요소가 있는지 검증"""
    # 💡 애플리케이션의 회원가입 경로에 맞게 URL을 사용합니다.
    response = client.get('/register') 

    # 1. 상태 코드 확인
    assert response.status_code == 200
    
    # 2. 페이지 내용 확인 (폼의 제목 및 필드 확인)
    response_data = response.data.decode('utf-8')
    assert "집사 회원가입" in response_data # 페이지 제목/헤더
    assert 'name="username"' in response_data # 사용자 이름 필드
    assert 'name="password"' in response_data # 비밀번호 필드
    assert 'name="confirm"' in response_data # 비밀번호 확인 필드
    assert 'Sign Up' in response_data # 제출 버튼

# ----------------------------------------------------
# 📝 테스트 2: POST 요청 (성공적인 제출 시나리오)
# ----------------------------------------------------

def test_successful_registration_submission(client):
    """유효한 데이터로 폼 제출 시 성공적으로 처리되고 리디렉션되는지 테스트"""
    # 유효한 폼 데이터 시뮬레이션
    valid_data = {
        'username': 'newcatbutler',
        'password': 'SecurePass123!',
        'confirm': 'SecurePass123!'
    }

    # POST 요청을 보내고 리디렉션 자동 추적
    response = client.post('/register', data=valid_data, follow_redirects=True)

    # 1. 최종 상태 코드 확인 
    # (성공 후 로그인 또는 메인 페이지로 리디렉션되어 200 OK 예상)
    assert response.status_code == 200
    
    # 2. 최종 페이지 내용 확인 (성공 후 이동할 페이지의 고유 텍스트를 검증)
    # 💡 여기에 성공 후 이동하는 페이지의 내용을 확인하는 코드를 추가하세요.
    # response_data = response.data.decode('utf-8')
    # assert "로그인하십시오" in response_data 


# ----------------------------------------------------
# 📝 테스트 3: POST 요청 (비밀번호 불일치 오류 시나리오)
# ----------------------------------------------------

def test_registration_password_mismatch_error(client):
    """비밀번호와 확인 비밀번호가 일치하지 않을 때 오류가 발생하는지 테스트"""
    # 비밀번호가 일치하지 않는 폼 데이터
    mismatch_data = {
        'username': 'mismatchuser',
        'password': 'Password123!',
        'confirm': 'DifferentPass456!'
    }

    # POST 요청
    response = client.post('/register', data=mismatch_data)

    # 1. 상태 코드 확인 
    # (일반적으로 오류 메시지를 표시하며 회원가입 페이지를 다시 렌더링 -> 200 OK 예상)
    assert response.status_code == 200
    
    # 2. 오류 메시지 내용 확인 
    # 💡 실제 애플리케이션이 표시하는 오류 메시지 텍스트를 검증합니다.
    # response_data = response.data.decode('utf-8')
    # assert "비밀번호가 일치하지 않습니다" in response_data