
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"

USERS = {}

PRODUCTS = [
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
    },
    {
        "id": 3,
        "name": "스크래쳐 박스",
        "price": 19000,
        "brand": "Scratch&Joy",
        "description": "골판지 재질로 발톱 관리에 좋은 고양이 스크래쳐.",
        "image_url": "https://images.pexels.com/photos/1056251/pexels-photo-1056251.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 4,
        "name": "자동 레이저 장난감",
        "price": 49000,
        "brand": "LaserFun",
        "description": "무작위 패턴으로 빛을 움직이며 고양이의 사냥 본능 자극.",
        "image_url": "https://images.pexels.com/photos/96938/pexels-photo-96938.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 5,
        "name": "캣닢 봉제 인형 세트",
        "price": 15000,
        "brand": "CatHerb",
        "description": "유기농 캣닢이 들어있는 물고기 모양 봉제 인형 3종 세트.",
        "image_url": "https://images.pexels.com/photos/2071873/pexels-photo-2071873.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 6,
        "name": "자동 급식기",
        "price": 89000,
        "brand": "FeedSmart",
        "description": "정해진 시간에 맞춰 사료를 배급해주는 스마트 자동 급식기.",
        "image_url": "https://images.pexels.com/photos/6869639/pexels-photo-6869639.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 7,
        "name": "고양이 정수기",
        "price": 59000,
        "brand": "PureFlow",
        "description": "순환 여과 시스템으로 항상 신선한 물을 제공하는 정수기.",
        "image_url": "https://images.pexels.com/photos/6231723/pexels-photo-6231723.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 8,
        "name": "캣 하우스 쿠션",
        "price": 39000,
        "brand": "SoftNest",
        "description": "동굴 형태의 폭신한 쿠션 하우스, 겨울철 필수템.",
        "image_url": "https://images.pexels.com/photos/127028/pexels-photo-127028.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 9,
        "name": "고양이 빗 그루밍 브러쉬",
        "price": 12000,
        "brand": "Groomy",
        "description": "털 빠짐을 줄여주는 실리콘 핀 브러쉬.",
        "image_url": "https://images.pexels.com/photos/6869649/pexels-photo-6869649.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
        "id": 10,
        "name": "LED 깃털 막대 장난감",
        "price": 17000,
        "brand": "NightPlay",
        "description": "빛나는 LED와 깃털 조합으로 야간 놀이에 특화된 장난감.",
        "image_url": "https://images.pexels.com/photos/208984/pexels-photo-208984.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
]

def get_product(pid):
    return next((p for p in PRODUCTS if p["id"] == pid), None)

@app.context_processor
def inject_globals():
    cart = session.get("cart", {})
    return {
        "current_user": session.get("user_id"),
        "cart_count": len(cart),
        "product_in_cart": lambda pid: str(pid) in cart,
    }

def require_login():
    if not session.get("user_id"):
        flash("로그인이 필요합니다.", "warning")
        return False
    return True

@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)

@app.route("/product/<int:pid>")
def product_detail(pid):
    product = get_product(pid)
    if not product:
        flash("상품이 존재하지 않습니다.", "danger")
        return redirect(url_for("index"))
    return render_template("product_detail.html", product=product)

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []
    total = 0
    for pid_str in cart:
        product = get_product(int(pid_str))
        if product:
            total += product["price"]
            items.append(product)
    return render_template("cart.html", items=items, total=total)

@app.route("/cart/toggle/<int:pid>", methods=["POST"])
def toggle_cart(pid):
    if not require_login():
        return redirect(url_for("login", next=request.referrer or url_for("index")))
    cart = session.get("cart", {})
    pid_str = str(pid)
    if pid_str in cart:
        cart.pop(pid_str)
        flash("장바구니에서 제거되었습니다.", "info")
    else:
        cart[pid_str] = 1
        flash("장바구니에 추가되었습니다.", "success")
    session["cart"] = cart
    return redirect(request.referrer or url_for("index"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not require_login():
        return redirect(url_for("login", next=url_for("checkout")))
    if not session.get("cart"):
        flash("장바구니가 비어 있습니다.", "warning")
        return redirect(url_for("index"))
    if request.method == "POST":
        if "cancel" in request.form:
            flash("결제가 취소되었습니다.", "info")
            return redirect(url_for("cart"))
        name = request.form.get("name","").strip()
        phone = request.form.get("phone","").strip()
        address = request.form.get("address","").strip()
        if not (name and phone and address):
            flash("모든 필수 정보를 입력해주세요.", "danger")
        else:
            session["cart"] = {}
            flash("결제가 완료되었습니다! 주문이 접수되었습니다.", "success")
            return redirect(url_for("index"))
    return render_template("checkout.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"].strip()
        password=request.form["password"].strip()
        user=USERS.get(username)
        if not user or user["password"]!=password:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.","danger")
        else:
            session["user_id"]=username
            flash("로그인 성공!","success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("index"))
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"].strip()
        password=request.form["password"].strip()
        confirm=request.form["confirm"].strip()
        if username in USERS:
            flash("이미 존재하는 사용자입니다.","danger")
        elif password!=confirm:
            flash("비밀번호가 일치하지 않습니다.","danger")
        else:
            USERS[username]={"password":password}
            flash("회원가입 성공! 이제 로그인해주세요.","success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.","info")
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(debug=True)

def get_product(pid):
    """주어진 ID로 상품 정보를 찾아 반환합니다."""
    # pid가 문자열로 넘어올 수 있으므로 int로 변환 시도
    try:
        pid = int(pid)
    except ValueError:
        return None

    for product in PRODUCTS:
        if product['id'] == pid:
            return product
    return None
