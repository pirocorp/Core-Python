"""Show the context-manager protocol: enter, execute body, then exit."""


class MyContextManager:
    def __enter__(self):
        # Called automatically when entering 'with'.
        print("Entering the context")
        return self  # 'as cm' receives this same manager object.

    def __exit__(self, exc_type, exc_value, traceback):
        # Called automatically after the with body, including on exceptions.
        print("Exiting the context")
        # No explicit return -> None -> do not suppress body exceptions.


def main():
    with MyContextManager() as cm:
        # cm is the object returned by __enter__, and the body runs between
        # the two printed messages.
        print("Inside the context")


if __name__ == "__main__":
    main()
