"""Structural annotations versus functools single-dispatch on runtime type."""

from functools import singledispatch
from typing import Protocol, runtime_checkable


@runtime_checkable
class Speaker(Protocol):
    def speak(self) -> str:
        ...


class Robot:
    def speak(self) -> str:
        return "beep"


class InvalidSpeaker:
    def speak(self, *, volume: int) -> str:
        return str(volume)


def announce(speaker: Speaker) -> str:
    return f"announcement: {speaker.speak()}"


@singledispatch
def render(value: object) -> str:
    return f"default:{type(value).__name__}"


@render.register
def _(value: int) -> str:
    return f"integer:{value}"


@render.register(str)
def _(value: str) -> str:
    return f"string:{value}"


if __name__ == "__main__":
    print(announce(Robot()))
    print("structural:", isinstance(Robot(), Speaker))
    print("presence-only:", isinstance(InvalidSpeaker(), Speaker))
    print("dispatch int:", render(42))
    print("dispatch str:", render("hi"))
    print("dispatch float:", render(3.5))
    print("bool resolves as int:", render(True))
