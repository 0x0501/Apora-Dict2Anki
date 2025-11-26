class QueryAPIError(Exception):
    """General exception for Apora API errors."""

    pass


class BalanceInsufficientException(Exception):
    def __init__(self, message: str = "Insufficient balance to perform querying."):
        self.message = message
        super().__init__(self.message)
