"""Ordinary inheritance, mixins and method lookup order."""


class Animal:
    def speak(self) -> str:
        return "generic sound"


class Dog(Animal):
    def speak(self) -> str:
        return f"{super().speak()} + woof"


class Flyable:
    def fly(self) -> str:
        return "flying"


class Bird(Flyable, Animal):
    def speak(self) -> str:
        return "chirp"


if __name__ == "__main__":
    animal = Animal()
    dog = Dog()
    bird = Bird()
    print("animal:", animal.speak())
    print("dog:", dog.speak())
    print("bird:", bird.speak())
    print("fly:", bird.fly())
    print("bird MRO:", " > ".join(cls.__name__ for cls in Bird.__mro__))
