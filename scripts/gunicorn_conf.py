import json
import multiprocessing
import os

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)

workers_str = os.getenv("WORKERS")
max_workers_str = os.getenv("MAX_WORKERS")
workers_per_core_str = os.getenv("WORKERS_PER_CORE")
if max_workers_str:
    web_concurrency = int(max_workers_str)
elif workers_per_core_str:
    cores = multiprocessing.cpu_count()
    web_concurrency = int(float(workers_per_core_str) * cores)
elif workers_str:
    web_concurrency = int(workers_str)
else:
    web_concurrency = 4

# Gunicorn config variables
loglevel = os.getenv("LOG_LEVEL", "info")
workers = web_concurrency
bind = bind_env if bind_env else f"{host}:{port}"
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "120"))
timeout = int(os.getenv("TIMEOUT", "120"))
keepalive = int(os.getenv("KEEP_ALIVE", "5"))
errorlog = os.getenv("ERROR_LOG", "-")
accesslog = os.getenv("ACCESS_LOG", "-")
worker_tmp_dir = "/dev/shm"

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core_str,
    "max_workers": max_workers_str,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))
