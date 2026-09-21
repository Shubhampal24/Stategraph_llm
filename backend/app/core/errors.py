class StateFlowError(Exception):
    def __init__(self, category: str, message: str, status_code: int = 400):
        self.category = category
        self.message = message
        self.status_code = status_code
        super().__init__(message)
