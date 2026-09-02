import uuid


class TurnProviderError(RuntimeError):
    """Safe, stable provider-stage failure returned by the turn API."""

    def __init__(
        self,
        message: str,
        *,
        turn_id: uuid.UUID,
        stage: str,
        error_code: str,
        resumable: bool,
    ) -> None:
        super().__init__(message)
        self.turn_id = turn_id
        self.stage = stage
        self.error_code = error_code
        self.resumable = resumable

    def api_detail(self) -> dict[str, str | bool]:
        return {
            "turn_id": str(self.turn_id),
            "stage": self.stage,
            "error_code": self.error_code,
            "message": str(self),
            "resumable": self.resumable,
        }
