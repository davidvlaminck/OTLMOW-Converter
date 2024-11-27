from typing import Sequence, Optional


class ExceptionsDictGroup(Exception):
    """
    Provides the same functions a ExceptionGroup.py but instead of a list of Exceptions it returns
    a dictionary of structure:
     {
        "ex": Exception
        "tab": str
    }
    """
    def __init__(self, message, exceptions: Sequence[BaseException] = None, cause_tabs: Optional[Sequence[str]]= None):
        super().__init__(message)
        if exceptions is None:
            exceptions = []
            if cause_tabs:
                self.exceptions = [{"ex": exceptions[i], "tab": cause_tabs[i]} for i in
                                   range(len(exceptions))]
            else:
                self.exceptions = [{"ex": exceptions[i], "tab": None} for i in
                                   range(len(exceptions))]

    def add_exception(self, error: BaseException, cause_tab: str = None):
        self.exceptions.append({"ex": error, "tab": cause_tab})


    def __str__(self):
        return (f'ExceptionGroup with {len(self.exceptions)} error(s): ' +
                ('\n'.join([str(error) for error in self.exceptions])))

