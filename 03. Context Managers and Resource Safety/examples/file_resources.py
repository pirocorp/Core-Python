"""Safe file handling using built-in context managers and temporary paths."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory


def write_and_read(text: str) -> tuple[str, bool]:
    """Return file contents and whether the reader was closed on exit."""
    # TemporaryDirectory is itself a context manager. It deletes its
    # temporary directory when this with block exits, even on exceptions.
    with TemporaryDirectory(prefix="context-lesson-") as directory:
        path = Path(directory) / "example.txt"

        # __enter__ opens the file. The 'as writer' target is the value
        # returned by __enter__, not a new variable scope.
        with path.open("w", encoding="utf-8") as writer:
            writer.write(text)

        with path.open("r", encoding="utf-8") as reader:
            result = reader.read()
            assert not reader.closed  # The resource is still open in the body.

        # __exit__ already ran, so the file has been closed.
        return result, reader.closed


def close_after_exception() -> tuple[bool, str]:
    """Prove that a file closes even if the with body raises an exception."""
    with TemporaryDirectory(prefix="context-lesson-") as directory:
        path = Path(directory) / "example.txt"
        path.write_text("contents", encoding="utf-8")

        try:
            with path.open("r", encoding="utf-8") as reader:
                raise RuntimeError("simulated processing failure")
        except RuntimeError as exc:
            # Unlike C# using declarations, Python's 'with' variable is still
            # bound after the block. The file object, however, is closed.
            return reader.closed, str(exc)


def main() -> None:
    text, closed = write_and_read("Python context managers")
    print(f"Read: {text}")
    print(f"File closed: {closed}")

    closed_on_error, message = close_after_exception()
    print(f"Closed after exception: {closed_on_error}")
    print(f"Caught: {message}")


if __name__ == "__main__":
    main()
