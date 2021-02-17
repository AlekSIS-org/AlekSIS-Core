import pkg_resources

try:
    from .celery import app as celery_app
except ModuleNotFoundError:
    # Celery is not available
    celery_app = None

try:
    __version__ = pkg_resources.get_distribution("AlekSIS-Core").version
except Exception:
    __version__ = "unknown"

default_app_config = "aleksis.core.apps.CoreConfig"
