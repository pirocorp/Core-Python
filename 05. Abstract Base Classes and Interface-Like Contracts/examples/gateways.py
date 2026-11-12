"""ABC nominal contracts, structural Protocols, and virtual registration."""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_cents: int) -> str:
        """Charge an amount expressed as whole cents."""

    def checkout(self, amount_cents: int) -> str:
        if amount_cents <= 0:
            raise ValueError("amount must be positive")
        return self.charge(amount_cents)


class CardGateway(PaymentGateway):
    def charge(self, amount_cents: int) -> str:
        return f"card:{amount_cents}"


class PayPalGateway(PaymentGateway):
    def charge(self, amount_cents: int) -> str:
        return f"paypal:{amount_cents}"


class ExternalGateway:
    def charge(self, amount_cents: int) -> str:
        return f"external:{amount_cents}"


@runtime_checkable
class SupportsCharge(Protocol):
    def charge(self, amount_cents: int) -> str:
        ...


class RegisteredWithoutMethods:
    pass


PaymentGateway.register(RegisteredWithoutMethods)


if __name__ == "__main__":
    for gateway in (CardGateway(), PayPalGateway()):
        print("checkout:", gateway.checkout(150))
    external = ExternalGateway()
    print("external nominal:", isinstance(external, PaymentGateway))
    print("external structural:", isinstance(external, SupportsCharge))
    print("registered nominal:", isinstance(RegisteredWithoutMethods(), PaymentGateway))
    print("registered callable:", callable(getattr(RegisteredWithoutMethods(), "charge", None)))
    try:
        CardGateway().checkout(0)
    except ValueError:
        print("invalid amount: ValueError")
