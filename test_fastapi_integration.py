"""
Test script for FastAPI + Django + AI Integration
Run this to verify everything is set up correctly.
"""

import os
import sys
import time

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from services import get_ai_client


def test_service_availability():
    """Test if FastAPI service is running."""
    print("\n🔍 Testing FastAPI Service Availability...")
    with get_ai_client() as client:
        is_available = client.is_service_available()
        if is_available:
            print("✅ FastAPI service is running!")
            return True
        else:
            print(
                "❌ FastAPI service not running!"
            )
            print("   Start it with: python fastapi_app.py")
            return False


def test_local_description():
    """Test local ML model for description generation."""
    print("\n📝 Testing Local ML Model - Description Generation...")
    try:
        with get_ai_client() as client:
            description = client.generate_description_local(
                product_name="Blue Denim Jacket",
                category="Outerwear",
                price=89.99,
            )

            if description:
                print("✅ Local Model Description Generated:")
                print(f"   '{description}'")
                return True
            else:
                print("❌ Failed to generate description")
                return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_local_tags():
    """Test local ML model for tag generation."""
    print("\n🏷️  Testing Local ML Model - Tag Generation...")
    try:
        with get_ai_client() as client:
            tags = client.generate_tags_local(product_name="Summer T-Shirt")

            if tags:
                print("✅ Local Model Tags Generated:")
                print(f"   {', '.join(tags[:5])}")
                return True
            else:
                print("❌ Failed to generate tags")
                return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_openai_description():
    """Test OpenAI for description generation."""
    print("\n🤖 Testing OpenAI - Description Generation...")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not configured (skip with local model)")
        return None

    try:
        with get_ai_client() as client:
            description = client.generate_description_openai(
                product_name="Winter Coat",
                category="Outerwear",
                price=149.99,
            )

            if description:
                print("✅ OpenAI Description Generated:")
                print(f"   '{description}'")
                return True
            else:
                print("❌ Failed to generate description")
                return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_openai_tags():
    """Test OpenAI for tag generation."""
    print("\n🤖 Testing OpenAI - Tag Generation...")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not configured (skip with local model)")
        return None

    try:
        with get_ai_client() as client:
            tags = client.generate_tags_openai(
                product_name="Casual Sneakers",
                description="Comfortable casual sneakers",
            )

            if tags:
                print("✅ OpenAI Tags Generated:")
                print(f"   {', '.join(tags[:5])}")
                return True
            else:
                print("❌ Failed to generate tags")
                return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_local_recommendations():
    """Test local recommendation endpoint."""
    print("\n🧠 Testing Local ML - Recommendations...")
    try:
        with get_ai_client() as client:
            recommendations = client.get_recommendations_local(
                user_preference="casual summer outfit",
                category="Tops",
                count=3,
            )

            if recommendations:
                print("✅ Local Recommendations Generated:")
                print(f"   {recommendations[0]['product_name']}")
                return True
            else:
                print("❌ Failed to generate recommendations")
                return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_local_similar_products():
    """Test local similar products endpoint."""
    print("\n🔁 Testing Local ML - Similar Products...")
    try:
        with get_ai_client() as client:
            recommendations = client.get_similar_products_local(
                product_name="Blue Denim Jacket",
                count=2,
            )

            if recommendations:
                print("✅ Local Similar Products Generated:")
                print(f"   {recommendations[0]['product_name']}")
                return True
            else:
                print("❌ Failed to generate similar products")
                return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("FastAPI + Django + AI Integration Test Suite")
    print("=" * 60)

    results = {}

    # Test service availability first
    if not test_service_availability():
        print("\n" + "=" * 60)
        print("❌ Cannot proceed - FastAPI service not running")
        print("   Start it in another terminal: python fastapi_app.py")
        print("=" * 60)
        return

    # Run tests
    results["Local Description"] = test_local_description()
    time.sleep(1)  # Small delay between requests

    results["Local Tags"] = test_local_tags()
    time.sleep(1)

    results["OpenAI Description"] = test_openai_description()
    time.sleep(1)

    results["OpenAI Tags"] = test_openai_tags()
    time.sleep(1)

    results["Local Recommendations"] = test_local_recommendations()
    time.sleep(1)

    results["Local Similar Products"] = test_local_similar_products()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}")
        elif result is False:
            print(f"❌ {test_name}")
        else:
            print(f"⏭️  {test_name} (skipped)")

    print("\n" + "-" * 60)
    print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 60)

    if failed > 0:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)
    elif passed > 0:
        print("\n✅ All tests passed! You're ready to go.")
        print("\n📚 Next steps:")
        print("   1. Import in your views:")
        print("      from services import get_ai_client")
        print("   2. Use in views:")
        print("      with get_ai_client() as client:")
        print("          desc = client.generate_description_local(...)")
        print("\n   3. See README_FASTAPI_SETUP.md for more examples")
        sys.exit(0)
    else:
        print("\n⚠️  No tests could be run (all skipped)")
        sys.exit(1)


if __name__ == "__main__":
    main()
