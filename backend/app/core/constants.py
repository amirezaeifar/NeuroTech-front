from decimal import Decimal

DEFAULT_LOCALE = "fa"
SUPPORTED_LOCALES = ("fa", "en")
DEFAULT_ROLE_NAMES = ("admin", "specialist", "content_manager", "user")
MONEY_PRECISION = 18
MONEY_SCALE = 2
ZERO_MONEY = Decimal("0.00")
