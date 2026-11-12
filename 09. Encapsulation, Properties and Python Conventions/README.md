# 09 — Encapsulation, Properties and Python Conventions

**Audience:** Senior C# developers familiar with access modifiers, properties and validation. Focus: Python's real access model, property descriptors, runtime attribute lookup, and object layout.

## 1. Underscores communicate intent, not a C# access modifier

Python does not enforce C#-style `public`/`private`/`protected` visibility through its ordinary attribute syntax.

- `name` is a public attribute.
- `_name` is a **convention** meaning “non-public/internal use.” External code can still read or write it directly; this is not a security boundary.
- `__student_id` inside class `Student` is transformed by **name mangling** to `_Student__student_id`. This helps avoid accidental name clashes in subclasses, but is **not access control** and is still accessible via the transformed name.
- `__name__`, `__init__`, `__get__`, and other names with double underscores **on both sides** are special interpreter protocols (dunder methods), not the same name-mangling feature.

Python can preserve validation invariants behind a property, but deliberately bypassing the property and mutating `_age` can violate them. Treat your object's public API and documentation as the primary boundary, supplemented by tests, not as protection against hostile in-process callers.

## 2. `Student`: managed attributes with `@property`

Complete independently executable `examples/student_properties.py`:

```python
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
```

**Expected output:**

```text
student: Ada 20
updated: 21
id: S-42
name mangled: True
negative age: ValueError
bool age: TypeError
read-only name: AttributeError
```

### How `@property` works

- `@property` converts the following getter method into a **descriptor** stored on the class. Reading `student.age` runs the getter; it looks like a field but behaves like a C# property getter.
- `@age.setter` is another decorator: it creates/assigns a property that routes `student.age = 21` to the setter method. `self.age = age` in `__init__` deliberately uses validation rather than writing `self._age` without checking.
- `self._age` is the backing storage; without a distinct storage name, a setter doing `self.age = value` would recurse indefinitely.
- `name` has a getter but no setter, so assignment `student.name = "Eve"` raises `AttributeError` in an ordinary instance.
- `type(value) is not int` rejects `bool` as an age despite `isinstance(True, int)` being true in Python. This is a deliberate strict-contract decision; `bool` is a subclass of `int`.
- `0 <= value <= 150` is a **chained comparison** equivalent to `0 <= value and value <= 150`, with the middle expression evaluated once.
- `hasattr(student, "_Student__student_id")` demonstrates mangling and intentionally reveals that it is not an access guard.

**Important:** type annotations `: int` and `-> int` do not automatically enforce validation. The explicit setter checks do.

## 3. The descriptor protocol: what a property delegates to

A **descriptor** is an object placed as a class attribute that implements `__get__`, `__set__` and/or `__delete__`. Python's attribute lookup consults descriptors. A **data descriptor** implementing `__set__` generally takes precedence over a normal instance `__dict__` entry. A `property` is a built-in data descriptor.

`__set_name__(owner, name)` is a hook called during class creation when Python attaches the descriptor to its owner class. Our reusable `ValidatedPort` derives a backing attribute name such as `_port` and stores it on the *descriptor object*. Each `Endpoint` instance stores its own port value. `__get__(instance, owner)` receives the instance when read through an object; accessing through the class passes `None`, so returning `self` exposes the descriptor for introspection.

`getattr(instance, key)` and `setattr(instance, key, value)` are built-ins for dynamic attribute access, similar to reflection-driven member access in C#. `instance.__dict__` is the writable per-instance attribute dictionary in ordinary classes. The `__slots__` class attribute declares fixed instance slot names: instances of this simple slotted class lack a normal instance `__dict__` and reject arbitrary new attributes. Slots are a **layout/attribute restriction**, not strong encapsulation, and inheritance can reintroduce a `__dict__`.

Complete executable `examples/descriptors_and_slots.py`:

```python
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
```

**Expected output:**

```text
port: 443
storage: {'_port': 443}
class descriptor: ValidatedPort
invalid port: ValueError
point: 2 3
slot restriction: AttributeError
```

## 4. Attribute-resolution rules and pitfalls

- A **data descriptor** (such as `property` or `ValidatedPort` with `__set__`) usually wins over an instance attribute with the same name. A **non-data descriptor** (`__get__` without `__set__`) can be shadowed by the instance's dictionary. Normal bound methods arise from functions acting as descriptors.
- A class attribute holding a mutable list is **shared** among instances unless they override it with per-instance state. Avoid `class Student: grades = []` if each student needs independent grades.
- `__slots__` may reduce per-instance memory overhead for many instances, but exact savings are implementation-dependent. It does not make objects immutable; assigning to existing slots remains possible.
- Overriding `__getattribute__` changes every attribute read, including descriptor resolution. It can easily cause recursion and is rarely the right first tool for ordinary validation.
- Python `@property` should normally be cheap and unsurprising; expensive I/O hidden in an attribute read can be dangerous. Prefer explicit `load()` or async operations for network access.
- Never rely on `_name` or mangling to protect secrets from untrusted code running in the same interpreter. They are maintainability conventions, not sandboxing.

| C# | Python | Difference |
|---|---|---|
| `public string Name { get; }` | `@property def name(...)` | Read-only public access, but backing attribute not truly private |
| `private int _age` | `self._age` | Naming convention, no runtime access protection |
| Setter with validation | `@age.setter` | Validation executed only via the property API |
| `private` name hiding | `__name` name mangling | Avoids subclass clashes, not visibility security |
| Reflection / property metadata | Descriptor protocol | Descriptor controls ordinary runtime attribute lookup |
| `__slots__` | No direct C# equivalent | Changes Python instance layout and dynamic attributes |

## 5. Validation and exercises

```bash
python examples/student_properties.py
python examples/descriptors_and_slots.py
python -m unittest discover -s tests -v
```

1. Add a validated `Student.name` setter that rejects blank names and update initialization to use it.
2. Mutate `student._age` directly. Explain why a property is an invariant boundary by convention and API design, not a security guarantee.
3. Give `Endpoint` two `ValidatedPort` descriptors named `http_port` and `admin_port` and verify that `__set_name__` creates independent backing fields.
4. Attempt to assign `point.x = 9` and `point.color = "blue"` to distinguish mutability from a slots restriction.
5. Explain how the `@property` example from Lesson 04 relates to the descriptor protocol and ordinary method binding.

**References:** [Python descriptor HOWTO](https://docs.python.org/3/howto/descriptor.html), [Python data model](https://docs.python.org/3/reference/datamodel.html), [properties](https://docs.python.org/3/library/functions.html#property).
