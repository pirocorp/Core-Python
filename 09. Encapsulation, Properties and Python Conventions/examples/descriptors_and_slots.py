"""Data descriptors, __set_name__, instance dictionaries and __slots__."""


class ValidatedPort:
    def __set_name__(self, owner: type, name: str) -> None:
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value: int) -> None:
        if type(value) is not int or not 1 <= value <= 65535:
            raise ValueError("invalid TCP port")
        setattr(instance, self.storage_name, value)


class Endpoint:
    port = ValidatedPort()

    def __init__(self, port: int) -> None:
        self.port = port


class SlottedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


if __name__ == "__main__":
    endpoint = Endpoint(443)
    print("port:", endpoint.port)
    print("storage:", endpoint.__dict__)
    print("class descriptor:", type(Endpoint.port).__name__)
    try:
        endpoint.port = 0
    except ValueError:
        print("invalid port: ValueError")
    point = SlottedPoint(2, 3)
    print("point:", point.x, point.y)
    try:
        point.color = "blue"
    except AttributeError:
        print("slot restriction: AttributeError")
