import json
import logging

from django.apps import apps
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from mayan.apps.common.class_mixins import AppsModuleLoaderMixin

from .exceptions import QuotaExceeded
from .handlers import handler_process_quota_signal

__all__ = ('QuotaBackend',)
logger = logging.getLogger(name=__name__)


class QuotaBackendMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(
            mcs, name, bases, attrs
        )
        if not new_class.__module__ == 'mayan.apps.quotas.classes':
            mcs._registry[
                '{}.{}'.format(new_class.__module__, name)
            ] = new_class
            new_class.id = '{}.{}'.format(new_class.__module__, name)

        return new_class


class QuotaBackendBase(AppsModuleLoaderMixin):
    """
    Base class for the mailing backends. This class is mainly a wrapper
    for other Django backends that adds a few metadata to specify the
    fields it needs to be instantiated at runtime.

    The fields attribute is a list of dictionaries with the format:
    {
        'name': ''  # Field internal name
        'label': ''  # Label to show to users
        'class': ''  # Field class to use. Field classes are Python dot
                       paths to Django's form fields.
        'initial': ''  # Field initial value
        'default': ''  # Default value.
    }
    """
    fields = {}
    signal = None
    widgets = {}


class QuotaBackend(QuotaBackendBase, metaclass=QuotaBackendMetaclass):
    _loader_module_name = 'quota_backends'

    @staticmethod
    def _queryset_to_text_list(queryset):
        return ','.join(
            list(
                map(str, queryset)
            )
        ) or _(message='none')

    @staticmethod
    def connect_signals():
        for backend in QuotaBackend.get_all():
            if backend.signal:
                backend.signal.connect(
                    dispatch_uid='quotas_handler_process_signal',
                    receiver=handler_process_quota_signal,
                    sender=backend.sender
                )

    @classmethod
    def _initialize(cls):
        """
        Allow the quota backend to run code when the app initializes.
        """

    @classmethod
    def create(cls, **kwargs):
        Quota = apps.get_model(app_label='quotas', model_name='Quota')

        return Quota.objects.create(
            backend_data=json.dumps(obj=kwargs),
            backend_path=cls.get_dotted_path()
        )

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return sorted(
            cls._registry.values(), key=lambda x: x.label
        )

    @classmethod
    def get_choices(cls):
        return [
            (
                backend.id, backend.label
            ) for backend in QuotaBackend.get_all()
        ]

    @classmethod
    def get_dotted_path(cls):
        return '{}.{}'.format(cls.__module__, cls.__name__)

    @classmethod
    def get_fields(cls):
        return cls.fields

    @classmethod
    def get_field_order(cls):
        return cls.field_order

    @classmethod
    def get_instances(cls):
        Quota = apps.get_model(app_label='quotas', model_name='Quota')

        return Quota.objects.filter(
            backend_path=cls.get_dotted_path()
        )

    @classmethod
    def get_widgets(cls):
        return cls.widgets

    @classmethod
    def post_load_modules(cls):
        for backend in QuotaBackend.get_all():
            backend._initialize()

        QuotaBackend.connect_signals()

    def _allowed_filter_display(self):
        return ''

    def filters(self):
        result = self.get_filter_text()

        return format_lazy(
            ', '.join(
                ['{}'] * len(result)
            ), *result.values()
        )

    def get_filter_text(self):
        return {
            'limit': self._allowed_filter_display()
        }

    def process(self, **kwargs):
        if self._usage() >= self._allowed():
            raise QuotaExceeded(self.error_message)

    def usage(self):
        return _(message='Does not apply')


class NullBackend(QuotaBackend):
    label = _(message='Null backend')
    signal = None

    def display(self):
        return _(message='Null backend')
