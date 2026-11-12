"""C3 linearization and cooperative multiple-inheritance initialization."""


class Root:
    def __init__(self, *, events: list[str], **kwargs) -> None:
        if kwargs:
            raise TypeError("unexpected keyword arguments")
        self.events = events
        events.append("Root")

    def path(self) -> list[str]:
        return ["Root"]


class Left(Root):
    def __init__(self, *, left: str, events: list[str], **kwargs) -> None:
        self.left = left
        super().__init__(events=events, **kwargs)
        events.append("Left")

    def path(self) -> list[str]:
        return ["Left", *super().path()]


class Right(Root):
    def __init__(self, *, right: str, events: list[str], **kwargs) -> None:
        self.right = right
        super().__init__(events=events, **kwargs)
        events.append("Right")

    def path(self) -> list[str]:
        return ["Right", *super().path()]


class Diamond(Left, Right):
    def __init__(self, *, events: list[str], **kwargs) -> None:
        super().__init__(events=events, **kwargs)
        events.append("Diamond")

    def path(self) -> list[str]:
        return ["Diamond", *super().path()]


def inconsistent_hierarchy_fails() -> bool:
    class X:
        pass

    class Y:
        pass

    class A(X, Y):
        pass

    class B(Y, X):
        pass

    try:
        class Impossible(A, B):
            pass
    except TypeError:
        return True
    return False


if __name__ == "__main__":
    events: list[str] = []
    item = Diamond(events=events, left="L", right="R")
    print("MRO:", " > ".join(cls.__name__ for cls in Diamond.__mro__))
    print("init unwind:", events)
    print("attributes:", item.left, item.right)
    print("method chain:", item.path())
    print("inconsistent MRO:", inconsistent_hierarchy_fails())
