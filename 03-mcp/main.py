import requests
from fastmcp import FastMCP

# Standalone functions that can be imported and used directly
def read_web_content(url: str) -> str:
    """
    Download and extract content from any web page using Jina Reader.

    Args:
        url: The URL of the web page to read

    Returns:
        The extracted text content from the web page
    """
    try:
        # Use Jina Reader API to extract content
        jina_url = f"https://r.jina.ai/{url}"

        response = requests.get(jina_url, timeout=30)
        response.raise_for_status()

        return response.text

    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error reading web content: {str(e)}"


def read_web_content_markdown(url: str) -> str:
    """
    Download and extract content from a web page as markdown using Jina Reader.

    Args:
        url: The URL of the web page to read

    Returns:
        The extracted content as markdown
    """
    try:
        # Use Jina Reader API with markdown accept header
        jina_url = f"https://r.jina.ai/{url}"

        response = requests.get(
            jina_url,
            headers={"Accept": "application/markdown"},
            timeout=30
        )
        response.raise_for_status()

        return response.text

    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error reading web content: {str(e)}"


# FastMCP server setup
mcp = FastMCP("web-content-reader")

@mcp.tool
def web_read(url: str) -> str:
    """Download and extract content from any web page using Jina Reader."""
    return read_web_content(url)


@mcp.tool
def web_read_markdown(url: str) -> str:
    """Download and extract content from a web page as markdown using Jina Reader."""
    return read_web_content_markdown(url)



if __name__ == "__main__":
    mcp.run()
