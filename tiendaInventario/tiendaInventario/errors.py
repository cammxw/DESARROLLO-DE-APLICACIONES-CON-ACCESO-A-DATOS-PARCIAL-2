class ShopError(Exception):
    pass


class ValidationError(ShopError):
    pass


class ProductNotFoundError(ShopError):
    pass


class InsufficientStockError(ShopError):
    pass


class ProductInUseError(ShopError):
    pass


class SimulatedFailureError(ShopError):
    pass
