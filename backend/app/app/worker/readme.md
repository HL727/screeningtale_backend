# Worker folder for Celery

Folder to initiate `Celery`-app and import tasks. The `Celery`-app is instantiated in the `__init__.py`-file.

When new files with tasks are created in this folder they must be included in the `./__init__.py`-file. Example with the file `./task.py` within this folder:

```
app = Celery(
    "worker",
    backend="redis://redis",
    broker="amqp://guest@queue//",
    include=["app.worker.test"],
)
```
