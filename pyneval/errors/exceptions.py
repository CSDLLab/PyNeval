
class PyNevalError(Exception):
    default_detail = "ERROR: PyNeval Error"

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail
        self.detail = "ERROR: {}".format(detail)

    def __str__(self):
        return self.detail


class InvalidSwcFileError(PyNevalError):
    """
    invalid swc file
    """
    default_detail = "ERROR: Invalid swc file"
    def __init__(self, file=None):
        if file is not None:
            self.detail = "ERROR: {} is a invalid swc file".format(file)
        else:
            self.detail = self.default_detail


class InvalidTiffFileError(PyNevalError):
    """
    invalid swc file
    """
    default_detail = "ERROR: Invalid tiff file"
    def __init__(self, file=None):
        if file is not None:
            self.detail = "ERROR: {} is a invalid tiff file".format(file)
        else:
            self.detail = self.default_detail


class InvalidMetricError(PyNevalError):
    """
    invalid metric
    """
    default_detail = "ERROR: The metric is not supported."
    def __init__(self, metric=None, valid_metrics=None):
        self.detail = self.default_detail
        if metric is not None:
            self.detail = "ERROR: The metric '{}' is not supported.".format(metric)
        if valid_metrics is not None:
            self.detail += "\nValid options for --metric:\n{}".format(valid_metrics)

class InvalidEuclideanPoint(PyNevalError):
    """
    Invalid Euclidean point
    """
    default_detail = "ERROR: invalid euclidean point"

    def __init__(self, param=None):
        self.detail = self.default_detail
        if param is not None:
            self.detail = "ERROR: {} is not a valid eculidean point".format(param)

class InvalidNode(PyNevalError):
    """
    Invalid node
    """
    default_detail = "ERROR: invalid node"

    def __init__(self, detail=""):
        self.detail = self.default_detail
        if detail:
            self.detail = "ERROR: {}".format(detail)