"""Python naming conventions, properties, validation, and name mangling."""


class Student:
    def __init__(self, name: str, age: int) -> None:
        self._name = name
        self._age = 0
        self.age = age
        self.__student_id = "S-42"

    @property
    def name(self) -> str:
        return self._name

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if type(value) is not int:
            raise TypeError("age must be an int")
        if not 0 <= value <= 150:
            raise ValueError("age out of range")
        self._age = value

    def identifier(self) -> str:
        return self.__student_id


if __name__ == "__main__":
    student = Student("Ada", 20)
    print("student:", student.name, student.age)
    student.age = 21
    print("updated:", student.age)
    print("id:", student.identifier())
    print("name mangled:", hasattr(student, "_Student__student_id"))
    try:
        student.age = -1
    except ValueError:
        print("negative age: ValueError")
    try:
        student.age = True
    except TypeError:
        print("bool age: TypeError")
    try:
        student.name = "Eve"
    except AttributeError:
        print("read-only name: AttributeError")
