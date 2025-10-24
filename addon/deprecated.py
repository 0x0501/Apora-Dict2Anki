import warnings
from functools import wraps


def deprecated(message=None):
    """
    A helper function that mark classes or functions as deprecated

    :param message: A warning message, for example "This function is deprecated since version 1.0. Use new_func instead."
    """
    if message is None:
        message = "This is deprecated."

    def decorator(obj):
        if isinstance(obj, type):  # 如果是类
            # 为类创建包装器
            class DeprecatedClass(obj):
                def __init__(self, *args, **kwargs):
                    warnings.warn(
                        f"Class '{obj.__name__}' is deprecated: {message}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    super().__init__(*args, **kwargs)

            DeprecatedClass.__name__ = obj.__name__
            DeprecatedClass.__doc__ = obj.__doc__
            DeprecatedClass.__module__ = obj.__module__
            return DeprecatedClass
        else:  # 如果是函数或方法

            @wraps(obj)
            def wrapper(*args, **kwargs):
                warnings.warn(
                    f"Function '{obj.__name__}' is deprecated: {message}",
                    DeprecationWarning,
                    stacklevel=2,
                )
                return obj(*args, **kwargs)

            return wrapper

    return decorator
