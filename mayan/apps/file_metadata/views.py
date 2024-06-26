from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _, ngettext

from mayan.apps.documents.forms.document_type_forms import DocumentTypeFilteredSelectForm
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.views.generics import (
    FormView, MultipleObjectConfirmActionView, SingleObjectEditView,
    SingleObjectListView
)
from mayan.apps.views.view_mixins import ExternalObjectViewMixin

from .classes import FileMetadataDriver
from .icons import (
    icon_document_file_metadata_single_submit,
    icon_document_type_file_metadata_settings,
    icon_document_type_file_metadata_submit, icon_file_metadata,
    icon_document_file_metadata_driver_list,
    icon_file_metadata_driver_attribute_list, icon_file_metadata_driver_list
)
from .links import link_document_file_metadata_single_submit
from .models import DocumentFileDriverEntry
from .permissions import (
    permission_document_type_file_metadata_setup,
    permission_file_metadata_submit, permission_file_metadata_view
)


class DocumentFileMetadataDriverListView(
    ExternalObjectViewMixin, SingleObjectListView
):
    external_object_permission = permission_file_metadata_view
    external_object_pk_url_kwarg = 'document_file_id'
    external_object_queryset = DocumentFile.valid.all()
    view_icon = icon_document_file_metadata_driver_list

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_file_metadata,
            'no_results_main_link': link_document_file_metadata_single_submit.resolve(
                context=RequestContext(
                    dict_={
                        'resolved_object': self.external_object
                    }, request=self.request
                )
            ),
            'no_results_text': _(
                'File metadata are the attributes of the document\'s file. '
                'They can range from camera information used to take a photo '
                'to the author that created a file. File metadata are set '
                'when the document\'s file was first created. File metadata '
                'attributes reside in the file itself. They are not the '
                'same as the document metadata, which are user defined and '
                'reside in the database.'
            ),
            'no_results_title': _(message='No file metadata available.'),
            'object': self.external_object,
            'title': _(
                'File metadata drivers for: %s'
            ) % self.external_object
        }

    def get_source_queryset(self):
        return self.external_object.file_metadata_drivers.all()


class DocumentFileMetadataDriverAttributeListView(
    ExternalObjectViewMixin, SingleObjectListView
):
    external_object_permission = permission_file_metadata_view
    external_object_pk_url_kwarg = 'document_file_driver_id'
    view_icon = icon_file_metadata_driver_attribute_list

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_file_metadata,
            'no_results_main_link': link_document_file_metadata_single_submit.resolve(
                context=RequestContext(
                    dict_={
                        'resolved_object': self.external_object.document_file
                    }, request=self.request
                )
            ),
            'no_results_text': _(
                'This could mean that the file metadata detection has not '
                'completed or that the driver does not support '
                'any metadata field for the file type of this document.'
            ),
            'no_results_title': _(
                'No file metadata available for this driver.'
            ),
            'object': self.external_object.document_file,
            'title': _(
                'File metadata attributes for: %(document_file)s with driver: %(driver)s'
            ) % {
                'document_file': self.external_object.document_file,
                'driver': self.external_object.driver
            }
        }

    def get_external_object_queryset(self):
        queryset_document_files = DocumentFile.valid.all()
        return DocumentFileDriverEntry.objects.filter(
            document_file_id__in=queryset_document_files.values('pk')
        )

    def get_source_queryset(self):
        return self.external_object.entries.all()


class DocumentFileMetadataSubmitView(MultipleObjectConfirmActionView):
    object_permission = permission_file_metadata_submit
    pk_url_kwarg = 'document_file_id'
    source_queryset = DocumentFile.valid.all()
    success_message_plural = _(
        '%(count)d documents files submitted to the file metadata queue.'
    )
    success_message_singular = _(
        '%(count)d document file submitted to the file metadata queue.'
    )
    view_icon = icon_document_file_metadata_single_submit

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'title': ngettext(
                singular='Submit the selected document file to the file metadata queue?',
                plural='Submit the selected documents files to the file metadata queue?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result['object'] = queryset.first()

        return result

    def object_action(self, form, instance):
        instance.submit_for_file_metadata_processing(user=self.request.user)


class DocumentTypeFileMetadataSettingsEditView(
    ExternalObjectViewMixin, SingleObjectEditView
):
    external_object_class = DocumentType
    external_object_permission = permission_document_type_file_metadata_setup
    external_object_pk_url_kwarg = 'document_type_id'
    fields = ('auto_process',)
    post_action_redirect = reverse_lazy(
        viewname='documents:document_type_list'
    )
    view_icon = icon_document_type_file_metadata_settings

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _(
                'Edit file metadata settings for document type: %s'
            ) % self.external_object
        }

    def get_object(self, queryset=None):
        return self.external_object.file_metadata_settings


class DocumentTypeFileMetadataSubmitView(FormView):
    extra_context = {
        'title': _(
            'Submit all documents of a type for file metadata processing.'
        )
    }
    form_class = DocumentTypeFilteredSelectForm
    post_action_redirect = reverse_lazy(viewname='common:tools_list')
    view_icon = icon_document_type_file_metadata_submit

    def get_form_extra_kwargs(self):
        return {
            'allow_multiple': True,
            'permission': permission_file_metadata_submit,
            'user': self.request.user
        }

    def form_valid(self, form):
        queryset_documents = Document.valid.all()

        count = 0
        for document_type in form.cleaned_data['document_type']:
            for document in document_type.documents.filter(pk__in=queryset_documents.values('pk')):
                document.submit_for_file_metadata_processing(
                    user=self.request.user
                )
                count += 1

        messages.success(
            message=_(
                '%(count)d documents added to the file metadata processing '
                'queue.'
            ) % {
                'count': count
            }, request=self.request
        )

        return HttpResponseRedirect(
            redirect_to=self.get_success_url()
        )


class FileMetadataDriverListView(SingleObjectListView):
    view_icon = icon_file_metadata_driver_list
    view_permission = permission_file_metadata_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_file_metadata,
            'no_results_text': _(
                'File metadata drivers extract embedded information '
                'from document files. File metadata drivers are configure '
                'in code only.'
            ),
            'no_results_title': _(
                'No file metadata drivers available.'
            ),
            'title': _(
                'File metadata drivers'
            )
        }

    def get_source_queryset(self):
        return FileMetadataDriver.collection.get_all(sorted=True)
