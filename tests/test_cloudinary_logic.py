def test_cloudinary_logic():
    """Тестуємо логіку обробки імен файлів в Cloudinary сервісі"""

    # Симуляція логіки з cloudinary.py
    def process_filename_for_cloudinary(filename, folder="avatars"):
        """Обробляє ім'я файлу для Cloudinary без подвійних розширень"""
        # Remove file extension from filename to avoid double extensions
        filename_without_ext = filename
        if filename_without_ext and "." in filename_without_ext:
            filename_without_ext = filename_without_ext.rsplit(".", 1)[0]

        # Cloudinary автоматично додасть розширення і folder
        expected_url_part = f"{folder}/{filename_without_ext}"

        return filename_without_ext, expected_url_part

    print("Testing Cloudinary filename processing logic...")
    print("=" * 50)

    test_cases = [
        "2025-04-30_02h01_00.png",
        "avatar.jpg",
        "user_photo.jpeg",
        "profile.PNG",
        "image.gif",
    ]

    for filename in test_cases:
        processed_id, url_part = process_filename_for_cloudinary(filename)

        print(f"Original filename: {filename}")
        print(f"Processed public_id: {processed_id}")
        print(f"Expected URL part: {url_part}")
        print(f"❌ OLD (wrong): avatars/avatars/{filename}.{filename.split('.')[-1]}")
        print(f"✅ NEW (correct): {url_part}.{filename.split('.')[-1]}")
        print("-" * 30)


if __name__ == "__main__":
    test_cloudinary_logic()
