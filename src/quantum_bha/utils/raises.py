class DifferentLengthError(Exception):
    """
    Exception raised when the elements have a different
    length
    """

    pass


class NumberOfParametersError(Exception):
    """
    Exception raised when the number of parameters is invalid
    """

    pass


class NonExistentFunctionError(Exception):
    """
    Exception raised when the requested function doesn't exist
    """

    pass
