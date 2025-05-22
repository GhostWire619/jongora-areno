

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination



# classes here

class CustomProductsPagination(PageNumberPagination):
    page_size= 10
    max_page_size = 20

class CustomSellersPagination(PageNumberPagination):
    page_size= 10
    max_page_size = 20

class CustomSellerProductsPagination(PageNumberPagination):
    page_size= 10
    max_page_size = 20