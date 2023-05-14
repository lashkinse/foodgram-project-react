from rest_framework import mixins, viewsets


class ListRetrieveModelMixin(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass
