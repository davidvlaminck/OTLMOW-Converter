class OTLAttributeError(BaseException):
    def __init__(self, message: str, attribute_dotnotation: str, attribute_value: object,
                 orig_exception: BaseException):
        super().__init__(message)
        self.attribute_dotnotation = attribute_dotnotation
        self.attribute_value = attribute_value
        self.orig_exception = orig_exception

    def __str__(self):
        return f'OTLAttributeError on attribute "{self.attribute_dotnotation}" with value "{self.attribute_value}": {str(self.orig_exception.__class__.__name__)}'
