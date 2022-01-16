""" Celery app init """

from celery import Celery
from wsgi import app


def make_celery():
    """ Celery conf and init """
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):  # pylint: disable=too-few-public-methods
        """ Run celery in app context """
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
