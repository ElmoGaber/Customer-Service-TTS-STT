import time

def measure_latency(func, *args, **kwargs):
    """
    Measures latency (in milliseconds) for any callable function.
    Returns: (result, latency_ms)
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    latency_ms = (end - start) * 1000
    return result, latency_ms
