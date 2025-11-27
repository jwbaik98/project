
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <title>{% block title %}Resona Cat Shop{% endblock %}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap CSS CDN -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
      crossorigin="anonymous"
    >
  </head>
  <body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
      <div class="container">
        <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">RESONA CAT SHOP</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="mainNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <a class="nav-link" href="{{ url_for('index') }}">Home</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="{{ url_for('cart') }}">Cart ({{ cart_count or 0 }})</a>
            </li>
          </ul>
          <ul class="navbar-nav ms-auto">
            {% if current_user %}
              <li class="nav-item">
                <span class="navbar-text me-2">집사, {{ current_user }}님</span>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
              </li>
            {% else %}
              <li class="nav-item">
                <a class="nav-link" href="{{ url_for('login') }}">Login</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="{{ url_for('register') }}">Sign Up</a>
              </li>
            {% endif %}
          </ul>
        </div>
      </div>
    </nav>

    <main class="container">
      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          <div class="mb-3">
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} mb-2" role="alert">
                {{ message }}
              </div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}

      {% block content %}{% endblock %}
    </main>

    <script
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
      integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
      crossorigin="anonymous"
    ></script>
  </body>
</html>
