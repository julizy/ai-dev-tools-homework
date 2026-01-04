"""
Test script for the web content reader tools.
This tests the read_web_content and read_web_content_markdown functions.
"""

from main import read_web_content, read_web_content_markdown


def test_read_web_content():
    """Test reading web content as plain text"""
    print("=" * 60)
    print("Test 1: read_web_content() - Plain Text")
    print("=" * 60)

    url = "https://www.wikipedia.org"
    print(f"\nFetching content from: {url}")

    try:
        content = read_web_content(url)

        if content.startswith("Error"):
            print(f"❌ FAILED: {content}")
        else:
            print(f"✅ SUCCESS: Retrieved {len(content)} characters")
            print(f"\nFirst 500 characters of content:")
            print("-" * 60)
            print(content[:500])
            print("-" * 60)

        return not content.startswith("Error")
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        return False


def test_read_web_content_markdown():
    """Test reading web content as markdown"""
    print("\n" + "=" * 60)
    print("Test 2: read_web_content_markdown() - Markdown Format")
    print("=" * 60)

    url = "https://github.com"
    print(f"\nFetching content from: {url}")

    content = read_web_content_markdown(url)

    if content.startswith("Error"):
        print(f"❌ FAILED: {content}")
    else:
        print(f"✅ SUCCESS: Retrieved {len(content)} characters")
        print(f"\nFirst 500 characters of markdown content:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)

    return not content.startswith("Error")


def test_invalid_url():
    """Test with an invalid URL"""
    print("\n" + "=" * 60)
    print("Test 3: Invalid URL Handling")
    print("=" * 60)

    url = "https://this-domain-does-not-exist-12345.com"
    print(f"\nFetching content from invalid URL: {url}")

    content = read_web_content(url)

    if content.startswith("Error"):
        print(f"✅ SUCCESS: Properly handled error - {content[:80]}")
    else:
        print(f"❌ FAILED: Should have returned an error")

    return content.startswith("Error")


def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("Web Content Reader - Test Suite")
    print("🚀 " * 20 + "\n")

    results = []

    try:
        results.append(("Plain Text Reading", test_read_web_content()))
    except Exception as e:
        print(f"❌ Exception in test_read_web_content: {e}")
        results.append(("Plain Text Reading", False))

    try:
        results.append(("Markdown Reading", test_read_web_content_markdown()))
    except Exception as e:
        print(f"❌ Exception in test_read_web_content_markdown: {e}")
        results.append(("Markdown Reading", False))

    try:
        results.append(("Invalid URL Handling", test_invalid_url()))
    except Exception as e:
        print(f"❌ Exception in test_invalid_url: {e}")
        results.append(("Invalid URL Handling", False))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    print("=" * 60 + "\n")

    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
