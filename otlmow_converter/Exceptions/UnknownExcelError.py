
class  UnknownExcelError(Exception):
    def __init__(self, original_exception, tab: str = None):
        # Copy the original exception's message
        self.original_exception = original_exception
        self.original_message = str(original_exception)

        # Call the parent constructor with the original message
        super().__init__(self.original_message)
        self.tab = tab
        # Copy additional attributes from the original exception if any
        if hasattr(original_exception, '__dict__'):
            self.__dict__.update(original_exception.__dict__)


    def __str__(self):
        if self.tab:
            return f"{super().__str__()} in {self.tab}"
        else:
            return super().__str__()