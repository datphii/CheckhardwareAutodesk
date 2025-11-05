import psutil, platform


def collect():
    freq = psutil.cpu_freq()
    return {
        "brand": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "logical_processors": psutil.cpu_count(logical=True) or 0,
        "max_freq_mhz": round(freq.max, 0) if freq else None
    }


