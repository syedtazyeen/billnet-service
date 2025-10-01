"""
Custom pagination class for the API.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that returns:
    - count: Total number of items
    - page: Current page number
    - results: Array of items for current page
    """
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'results': data
        })
