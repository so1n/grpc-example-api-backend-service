import multiprocessing
import pathlib
import socket
import sys

try:
    import gevent
except ImportError:
    pass
else:
    if socket.socket is gevent.socket.socket:
        import grpc.experimental.gevent

        grpc.experimental.gevent.init_gevent()


pro_path = str(pathlib.Path(__file__).parent.absolute())

sys.path.append(pro_path)


loglevel: str = "info"
workers: int = multiprocessing.cpu_count() * 2 + 1
daemon: bool = False
graceful_timeout: int = 0
worker_class: str = "gevent"
worker_connections: int = 8048
chdir: str = pro_path
access_log_format: str = '%(t)s %(p)s %({X-Real-Ip}i)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
