import subprocess


def ping(host="8.8.8.8", count=4):
    try:
        out = subprocess.check_output(["ping", host, "-n", str(count)], text=True)
        # Đơn giản: trả về raw text; nâng cao thì parse ra avg latency
        return {"host": host, "raw": out}
    except Exception:
        return {"host": host, "raw": None}


def collect():
    return {"ping_google": ping()}


