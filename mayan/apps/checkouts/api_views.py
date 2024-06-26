from rest_framework.generics import get_object_or_404

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.rest_api import generics
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin

from .models import DocumentCheckout
from .permissions import (
    permission_document_check_in, permission_document_check_in_override,
    permission_document_check_out_detail_view
)
from .serializers import (
    DocumentCheckoutSerializer, NewDocumentCheckoutSerializer
)


class APICheckedoutDocumentListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the documents that are currently checked out.
    post: Checkout a document.
    """
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewDocumentCheckoutSerializer
        else:
            return DocumentCheckoutSerializer

    def get_source_queryset(self):
        queryset_valid_documents = Document.valid.all()

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_check_out_detail_view,
            queryset=DocumentCheckout.objects.all(),
            user=self.request.user
        )

        return queryset.filter(document_id__in=queryset_valid_documents)


class APICheckedoutDocumentView(generics.RetrieveDestroyAPIView):
    """
    get: Retrieve the details of the selected checked out document entry.
    delete: Check in a document.
    """
    lookup_url_kwarg = 'checkout_id'
    serializer_class = DocumentCheckoutSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            '_event_keep_attributes': ('_event_actor',)
        }

    def get_source_queryset(self):
        queryset_valid_documents = Document.valid.all()

        if self.request.method == 'GET':
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission_document_check_out_detail_view,
                queryset=DocumentCheckout.objects.all(),
                user=self.request.user
            )

            return queryset.filter(document_id__in=queryset_valid_documents)
        elif self.request.method == 'DELETE':
            queryset_check_ins = AccessControlList.objects.restrict_queryset(
                permission=permission_document_check_in,
                queryset=DocumentCheckout.objects.filter(
                    user_id=self.request.user.pk
                ), user=self.request.user
            )
            queryset_check_in_overrides = AccessControlList.objects.restrict_queryset(
                permission=permission_document_check_in_override,
                queryset=DocumentCheckout.objects.exclude(
                    user_id=self.request.user.pk
                ), user=self.request.user
            )

            return (queryset_check_ins | queryset_check_in_overrides).filter(
                document_id__in=queryset_valid_documents.values('pk')
            )


class APIDocumentCheckoutView(
    ExternalObjectAPIViewMixin, generics.RetrieveDestroyAPIView
):
    """
    get: Retrieve the checkout details of the selected document entry.
    delete: Check in the selected document.
    """
    external_object_queryset = Document.valid.all()
    external_object_pk_url_kwarg = 'document_id'
    mayan_external_object_permission_map = {
        'GET': permission_document_check_out_detail_view
    }
    serializer_class = DocumentCheckoutSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            '_event_keep_attributes': ('_event_actor',)
        }

    def get_mayan_object_permission_map(self):
        if self.request.method == 'DELETE':
            try:
                checkout = self.get_external_object().checkout
            except DocumentCheckout.DoesNotExist:
                return
            else:
                permission = permission_document_check_in

                if checkout.user != self.request.user:
                    permission = permission_document_check_in_override

                return permission

    def get_object(self):
        queryset = self.filter_queryset(
            queryset=self.get_source_queryset()
        )

        obj = queryset.first()

        # Trigger a 404 error if no results are found.
        if obj:
            pk = obj.pk
        else:
            pk = None

        return get_object_or_404(queryset, pk=pk)

    def get_source_queryset(self):
        return DocumentCheckout.objects.filter(
            document=self.get_external_object()
        )
