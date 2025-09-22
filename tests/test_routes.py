import requests


# Тестуємо чи існує правильний маршрут
def test_confirmed_email_route():
    # Спочатку перевіримо чи працює API
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Root endpoint status: {response.status_code}")

        # Тестуємо неправильний маршрут (старий)
        try:
            response = requests.get(
                "http://localhost:8000/auth/confirmed_email/test", timeout=5
            )
            print(f"OLD route /auth/confirmed_email/test: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"OLD route connection error: {e}")

        # Тестуємо правильний маршрут (новий)
        try:
            response = requests.get(
                "http://localhost:8000/api/auth/confirmed_email/test", timeout=5
            )
            print(f"NEW route /api/auth/confirmed_email/test: {response.status_code}")
            if response.status_code != 404:
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"NEW route connection error: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Server not running: {e}")


if __name__ == "__main__":
    test_confirmed_email_route()
