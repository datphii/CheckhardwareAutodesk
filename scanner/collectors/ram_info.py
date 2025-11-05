import psutil


def collect():
    vm = psutil.virtual_memory()
    return {"total_gb": round(vm.total / (1024**3), 2)}


