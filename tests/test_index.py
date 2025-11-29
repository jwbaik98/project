# test_index.py

import pytest
# 💡 실제 Flask 애플리케이션 파일명에 맞게 'app'과 필요한 함수를 수정하세요.
# 여기서는 앱 인스턴스가 'app.py'에 정의되어 있고,
# 상품 목록을 가져오는 함수가 app.get_all_products라고 가정합니다.
from app import app


# ----------------------------------------------------
# 🧪 테스트 환경을 위한 더미 데이터 및 Mock 함수
# ----------------------------------------------------

DUMMY_PRODUCTS = [
    {
        "id": 1,
        "name": "프리미엄 캣타워",
        "price": 129000,
        "brand": "Resona Cat",
        "description": "3단 구조와 편안한 해먹이 포함된 프리미엄 캣타워.",
        "image_url": "https://images.pexels.com/photos/1276553/pexels-photo-1276553.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 2,
        "name": "터널 놀이 텐트",
        "price": 39000,
        "brand": "PlayLand",
        "description": "숨었다 나왔다를 반복하며 스트레스를 해소할 수 있는 터널형 텐트.",
        "image_url": "https://images.pexels.com/photos/1170986/pexels-photo-1170986.jpeg?auto=compress&cs=tinysrgb&w=600"
    }
]

# 상품 ID 1만 장바구니에 있다고 가정하는 Mock 함수
def mock_product_in_cart():
    """테스트를 위해 ID 1인 상품만 True를 반환합니다."""
    return {1}

# ----------------------------------------------------
# 🛠️ Fixture: Flask 테스트 클라이언트 설정
# ----------------------------------------------------

@pytest.fixture
def client():
    """테스트 클라이언트 설정 및 Flask 애플리케이션 컨텍스트 초기화"""
    # 애플리케이션을 테스트 모드로 설정
    app.config['TESTING'] = True
    
    # 테스트 클라이언트 생성
    with app.test_client() as client:
        yield client

# ----------------------------------------------------
# 📝 테스트 케이스
# ----------------------------------------------------

def test_home_page_loads_successfully(client):
    """루트 경로 접속 시 메인 페이지가 성공적으로 로드되는지 테스트"""
    # GET 요청을 보냅니다.
    response = client.get('/')

    # 1. 상태 코드 확인
    assert response.status_code == 200
    
    # 2. 페이지 내용 확인
    response_data = response.data.decode('utf-8')
    assert "Home - Resona Cat Shop" in response_data # 제목 블록
    assert "애완묘 용품 전문 쇼핑몰" in response_data # H1 제목
    assert "집사와 고양이를 위한" in response_data # 설명 텍스트

def test_product_listing_and_cart_buttons(client, monkeypatch):
    """
    상품 목록이 올바르게 렌더링되고, 장바구니 상태에 따라 버튼이 다르게 표시되는지 테스트
    (Flask 뷰 함수가 DUMMY_PRODUCTS와 mock_product_in_cart를 사용하도록 Mocking 필요)
    """
    
    # 💡 Mocking: Flask 뷰 함수가 DUMMY_PRODUCTS를 반환하도록 가정합니다.
    # 실제 앱의 데이터 로딩 함수를 Mocking해야 합니다. (예: app.get_all_products)
    
    # 이 테스트에서는 Flask 뷰 함수가 템플릿을 렌더링할 때
    # product_in_cart=mock_product_in_cart, products=DUMMY_PRODUCTS를 전달한다고 가정합니다.
    
    # ⚠️ 이 테스트를 실행하려면 실제 Flask 뷰 함수 (예: @app.route('/'))가
    # 테스트 모드일 때 DUMMY_PRODUCTS와 mock_product_in_cart를 사용하도록
    # **애플리케이션 코드를 수정하거나** mock 함수를 사용해야 합니다.
    
    # 간단한 Mocking을 위해, 이 테스트는 response.data를 기반으로 템플릿의 최종 출력 결과를 검증합니다.
from app import product_in_cart
def mock_product_in_cart(pid):
    return pid == 1

    monkeypatch.setattr(mock_product_in_cart)
    response = client.get('/')
    response_data = response.data.decode('utf-8')
    
    # 1. 상품 1 (고양이 장난감 A) 검증
    assert "프리미엄 캣타워" in response_data
    assert "129,000원" in response_data
    
    # 템플릿 로직 검증: ID 1은 장바구니에 있으므로 '카트에서 제거' 버튼이 보여야 합니다.
    assert f'<form action="{app.url_for("toggle_cart", pid=1)}" method="post"' in response_data
    # 💡 URL이 실제로 /cart/toggle/1로 렌더링되는지 확인 (url_for('toggle_cart', pid=product.id) 검증)
    assert '카트에서 제거</button>' in response_data
    assert '카트에 담기</button>' not in response_data # 동시에 나타나면 안 됨 (ID 1 기준)
    
    # 2. 상품 2 (터널 놀이 텐트) 검증
    assert "터널 놀이 텐트" in response_data
    assert "39,000원" in response_data
    
    # 템플릿 로직 검증: ID 2는 장바구니에 없으므로 '카트에 담기' 버튼이 보여야 합니다.
    assert f'<form action="{app.url_for("toggle_cart", pid=2)}" method="post"' in response_data
    assert '카트에 담기</button>' in response_data
    assert '카트에서 제거</button>' not in response_data # 동시에 나타나면 안 됨 (ID 2 기준)
    
    # 3. 상세보기 링크 검증
    assert f'<a href="{app.url_for("product_detail", pid=1)}" class="btn' in response_data
    assert f'<a href="{app.url_for("product_detail", pid=2)}" class="btn' in response_data