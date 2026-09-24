"""Simple rolling-window utilities."""


def rolling_average(values, width: int) -> list[float]:
    """Return the average of each complete width-sized consecutive window."""
    if width <= 0:
        raise ValueError("width must be positive")
    return [sum(values[index:index + width]) / width for index in range(len(values) - width + 1)]
