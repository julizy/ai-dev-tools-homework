"""
Download FastMCP docs and index them with minsearch.
"""

import os
import zipfile
import requests
from pathlib import Path
from minsearch import Index

# Configuration
ZIP_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"
ZIP_FILE = "fastmcp-main.zip"
EXTRACT_DIR = "fastmcp-extracted"


def download_zip_if_needed():
    """Download the zip file if it doesn't already exist."""
    if os.path.exists(ZIP_FILE):
        print(f"✓ {ZIP_FILE} already exists, skipping download")
        return

    print(f"Downloading {ZIP_URL}...")
    response = requests.get(ZIP_URL, timeout=60)
    response.raise_for_status()

    with open(ZIP_FILE, 'wb') as f:
        f.write(response.content)

    print(f"✓ Downloaded {ZIP_FILE} ({len(response.content)} bytes)")


def extract_markdown_files():
    """Extract markdown files from the zip."""
    documents = []

    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            # Check if it's a .md or .mdx file
            if not (file_info.filename.endswith('.md') or file_info.filename.endswith('.mdx')):
                continue

            # Read file content
            try:
                content = zip_ref.read(file_info.filename).decode('utf-8')
            except Exception as e:
                print(f"⚠ Skipping {file_info.filename}: {e}")
                continue

            # Remove the first part of the path (fastmcp-main/)
            parts = file_info.filename.split('/', 1)
            if len(parts) == 2:
                filename = parts[1]
            else:
                filename = file_info.filename

            # Create document
            doc = {
                'filename': filename,
                'content': content
            }
            documents.append(doc)
            print(f"✓ Indexed: {filename}")

    return documents


def index_with_minsearch(documents):
    """Index documents with minsearch."""
    # Create index
    index = Index(
        text_fields=['content'],
        keyword_fields=['filename']
    )

    # Add documents using fit method
    index.fit(documents)

    print(f"\n✓ Indexed {len(documents)} markdown files")

    return index


def search_index(index, query):
    """Search the index."""
    results = index.search(query, boost_dict={'content': 3.0})
    return results


def main():
    print("=" * 60)
    print("FastMCP Documentation Indexer")
    print("=" * 60)

    # Download
    download_zip_if_needed()

    # Extract and index
    print("\nExtracting markdown files...")
    documents = extract_markdown_files()

    if not documents:
        print("No markdown files found!")
        return None

    print("\nIndexing with minsearch...")
    index = index_with_minsearch(documents)

    print("\n" + "=" * 60)
    print("Indexing Complete!")
    print("=" * 60)

    return index


def interactive_search(index):
    """Interactive search loop."""
    print("\nEnter search queries (type 'quit' to exit):\n")

    while True:
        query = input("Search: ").strip()
        if query.lower() == 'quit':
            break

        if not query:
            continue

        results = search_index(index, query)

        if results:
            print(f"\nFound {len(results)} results:")
            for i, doc in enumerate(results, 1):
                print(f"\n{i}. {doc['filename']}")
                # Print first 200 chars of content
                content_preview = doc['content'][:200].replace('\n', ' ')
                print(f"   {content_preview}...")
        else:
            print("No results found.\n")


if __name__ == "__main__":
    index = main()

    if index:
        # Example search
        print("\n" + "=" * 60)
        print("Example Searches:")
        print("=" * 60)

        queries = ["getting started", "installation", "server"]
        for query in queries:
            results = search_index(index, query)
            print(f"\nSearching for '{query}': {len(results)} results")
            if results:
                print(f"  Top result: {results[0]['filename']}")

        # Interactive search
        print("\n" + "=" * 60)
        interactive_search(index)
