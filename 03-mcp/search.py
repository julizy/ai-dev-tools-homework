"""
Search functionality for FastMCP documentation using minsearch.
"""

import sys
from pathlib import Path
from minsearch import Index


def load_index():
    """Load or create the minsearch index."""
    # Import from index_docs to reuse the indexing logic
    sys.path.insert(0, str(Path(__file__).parent))
    from index_docs import download_zip_if_needed, extract_markdown_files, index_with_minsearch

    # Download and extract
    download_zip_if_needed()
    documents = extract_markdown_files()

    if not documents:
        raise ValueError("No documents found to index")

    # Create index
    index = index_with_minsearch(documents)
    return index, documents


def search_fastmcp_docs(query, num_results=5):
    """
    Search FastMCP documentation with minsearch.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)

    Returns:
        List of dictionaries with 'filename' and 'content' fields
    """
    index, _ = load_index()

    # Search with boost on content field
    results = index.search(
        query,
        boost_dict={'content': 3.0},
        num_results=num_results
    )

    return results


def display_results(results, query):
    """Display search results in a formatted way."""
    print("\n" + "=" * 80)
    print(f"Search Results for: '{query}'")
    print(f"Found {len(results)} results")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['filename']}")
        print("-" * 80)

        # Display first 300 characters of content
        content = result['content']
        preview = content[:300].replace('\n', ' ')
        if len(content) > 300:
            preview += "..."

        print(f"   {preview}")

    print("\n" + "=" * 80 + "\n")


def interactive_search():
    """Run interactive search mode."""
    print("\n" + "=" * 80)
    print("FastMCP Documentation Search")
    print("=" * 80)
    print("Loading index...")

    try:
        index, _ = load_index()
        print("✓ Index loaded successfully\n")
    except Exception as e:
        print(f"✗ Error loading index: {e}")
        return

    print("Enter search queries (type 'quit' to exit):\n")

    while True:
        query = input("Search: ").strip()

        if query.lower() == 'quit':
            print("\nGoodbye!")
            break

        if not query:
            continue

        try:
            results = index.search(
                query,
                boost_dict={'content': 3.0},
                num_results=5
            )
            display_results(results, query)
        except Exception as e:
            print(f"\n✗ Search error: {e}\n")


def main():
    """Main entry point."""
    print("FastMCP Documentation Search with minsearch")
    print("=" * 80)

    # Example searches
    print("\nRunning example searches...\n")

    queries = [
        "authentication",
        "tools and resources",
        "error handling",
    ]

    try:
        print("Loading index...")
        index, documents = load_index()
        print(f"✓ Index loaded with {len(documents)} documents\n")

        for query in queries:
            results = index.search(
                query,
                boost_dict={'content': 3.0},
                num_results=5
            )
            display_results(results, query)

    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Start interactive search
    interactive_search()


if __name__ == "__main__":
    main()
