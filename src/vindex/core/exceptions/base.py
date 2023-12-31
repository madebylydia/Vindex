class VindexException(Exception):
    """Base exception for Vindex."""

    def __init__(self, error: object | None = None) -> None:
        super().__init__(error or "Internal error within Vindex. No specific error were raised.")
