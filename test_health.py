"""
Test script for health check endpoint
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_health_check():
    """Test the health check function directly"""
    print("🏥 Testing health check...")

    try:
        from main import health_check

        # Call the health check function
        result = await health_check()

        print("✅ Health check results:")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Version: {result['version']}")
        print("   Services:")
        for service, status in result["services"].items():
            emoji = "✅" if status == "healthy" else "❌"
            print(f"     {emoji} {service}: {status}")

        return result

    except Exception as e:
        print(f"❌ Error testing health check: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_health_check())

    if result:
        if result["status"] == "healthy":
            print("\n🎉 All systems are healthy!")
        elif result["status"] == "degraded":
            print("\n⚠️  Some services are degraded")
        else:
            print("\n🚨 System is unhealthy")
    else:
        print("\n💥 Health check failed to run")
