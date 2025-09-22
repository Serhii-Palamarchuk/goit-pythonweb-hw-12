def test_filename_processing():
    """Тестуємо обробку імен файлів для запобігання подвійним розширенням"""

    # Симуляція логіки з cloudinary.py
    def process_filename(filename):
        """Видаляє розширення з імені файлу"""
        if filename and "." in filename:
            return filename.rsplit(".", 1)[0]
        return filename

    # Тестові випадки
    test_cases = [
        ("2025-04-30_02h01_00.png", "2025-04-30_02h01_00"),
        ("avatar.jpg", "avatar"),
        ("user_photo.jpeg", "user_photo"),
        ("image.PNG", "image"),
        ("test_file.gif", "test_file"),
        ("no_extension", "no_extension"),
        ("multiple.dots.in.name.png", "multiple.dots.in.name"),
    ]

    print("Testing filename processing...")
    for original, expected in test_cases:
        result = process_filename(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{original}' -> '{result}' (expected: '{expected}')")

    print("\nThis should prevent URLs like:")
    print(
        "❌ https://res.cloudinary.com/desvkbtdb/image/upload/v1757893415/avatars/avatars/2025-04-30_02h01_00.png.png"
    )
    print(
        "✅ https://res.cloudinary.com/desvkbtdb/image/upload/v1757893415/avatars/2025-04-30_02h01_00.png"
    )


if __name__ == "__main__":
    test_filename_processing()
