"""Override dispatch, unrelated duck-typed objects, and runtime failures."""


class Bird:
    def speak(self) -> str:
        return "generic chirp"


class Duck(Bird):
    def speak(self) -> str:
        return "quack"


class MechanicalDuck:
    def speak(self) -> str:
        return "synthetic quack"


class Silent:
    pass


class WrongSignature:
    def speak(self, volume: int) -> str:
        return f"volume={volume}"


def make_bird_speak(bird) -> str:
    return bird.speak()


if __name__ == "__main__":
    for bird in (Bird(), Duck(), MechanicalDuck()):
        print("speak:", make_bird_speak(bird))
    print("unrelated subclass:", isinstance(MechanicalDuck(), Bird))
    try:
        make_bird_speak(Silent())
    except AttributeError:
        print("silent: AttributeError")
    try:
        make_bird_speak(WrongSignature())
    except TypeError:
        print("wrong signature: TypeError")
