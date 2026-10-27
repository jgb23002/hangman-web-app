"""Keep ordinary tests in-process; only browser integration may use sockets."""

import socket

import pytest


@pytest.fixture(autouse=True)
def prevent_network_in_ordinary_tests(request, monkeypatch):
    if request.node.get_closest_marker("browser") is not None:
        return

    def reject_network(*args, **kwargs):
        raise AssertionError(
            "Ordinary tests must not open network connections or HTTP listeners. "
            "Use Flask's test client; mark real-browser integration as browser."
        )

    monkeypatch.setattr(socket, "create_connection", reject_network)
    for method in ("connect", "connect_ex", "bind", "listen"):
        monkeypatch.setattr(socket.socket, method, reject_network)
