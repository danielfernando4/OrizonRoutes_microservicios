import pytest
from pydantic import ValidationError

from app.schemas.chat import IncomingWSMessage


def test_incoming_message_valid():
    msg = IncomingWSMessage(content="Hola, ¿todo bien?")
    assert msg.content == "Hola, ¿todo bien?"


def test_incoming_message_rejects_empty_content():
    with pytest.raises(ValidationError):
        IncomingWSMessage(content="")


def test_incoming_message_rejects_too_long_content():
    with pytest.raises(ValidationError):
        IncomingWSMessage(content="a" * 2001)
