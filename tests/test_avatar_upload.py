import requests
import io
from PIL import Image


def create_test_image():
    """Створює тестове зображення в пам'яті"""
    # Створюємо простий білий квадрат 100x100
    img = Image.new("RGB", (100, 100), color="white")

    # Зберігаємо в байтовий буфер
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes


def test_avatar_upload():
    """Тестуємо завантаження аватару без подвійних розширень"""

    base_url = "http://localhost:8000"

    # 1. Спочатку потрібно залогінитися
    print("1. Attempting to login...")
    login_data = {"username": "testuser", "password": "testpassword123"}

    try:
        response = requests.post(
            f"{base_url}/api/auth/login", data=login_data, timeout=10
        )
        print(f"Login status: {response.status_code}")

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Login successful")

            # 2. Завантажуємо аватар
            print("\n2. Uploading avatar...")
            headers = {"Authorization": f"Bearer {access_token}"}

            # Створюємо тестове зображення
            test_image = create_test_image()

            files = {"file": ("test_avatar.png", test_image, "image/png")}

            response = requests.patch(
                f"{base_url}/api/auth/avatar",
                headers=headers,
                files=files,
                timeout=30,  # Збільшуємо timeout для завантаження
            )

            print(f"Upload status: {response.status_code}")

            if response.status_code == 200:
                user_data = response.json()
                avatar_url = user_data.get("avatar_url")
                print(f"✅ Avatar uploaded successfully!")
                print(f"Avatar URL: {avatar_url}")

                # Перевіряємо чи немає подвійних розширень
                if (
                    avatar_url
                    and ".png.png" not in avatar_url
                    and "/avatars/avatars/" not in avatar_url
                ):
                    print("✅ SUCCESS: No double extensions in URL!")
                else:
                    print("❌ FAILED: Double extensions still present!")

            else:
                print(f"❌ Upload failed: {response.text}")

        else:
            print(f"❌ Login failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_avatar_upload()
