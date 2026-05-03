from rest_framework.pagination import PageNumberPagination


class OptionalPageNumberPagination(PageNumberPagination):
    """
    Only paginate when the request explicitly asks for it.

    This keeps old clients working as before, while letting lighter
    homepage/widget requests limit payload size on Render free instances.
    """

    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if "page" not in request.query_params and "page_size" not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view=view)
