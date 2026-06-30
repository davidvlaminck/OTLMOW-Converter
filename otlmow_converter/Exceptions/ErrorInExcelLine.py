class ErrorInExcelLine(BaseException):
    def __init__(self, message, line_number: int, error: BaseException):
        super().__init__(message)
        self.line_number = line_number
        self.error = error

    def __str__(self):
        return f'Error in line {self.line_number}: {self.error}'
