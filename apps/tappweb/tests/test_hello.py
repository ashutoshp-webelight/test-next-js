"""Hello unit test module."""

from tappweb.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello tappweb"
