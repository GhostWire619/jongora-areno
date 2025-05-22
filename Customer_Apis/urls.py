from django.urls import path
from . import views


urlpatterns = [
    path('shop_products', views.ProductsView.as_view(), name="shop_products"),
    path('product_detail/<int:id>', views.ShopProductDetail.as_view(), name="product_detail"),
    path('relatedproducts/<int:product_id>', views.GetRelatedProducts.as_view(), name="relatedproducts"),
    path('product_sellers', views.ProductSellers.as_view(), name="product_sellers"),
    path('product_seller_page/<int:user_id>', views.ProductSellerPage.as_view(), name="product_seller_page"),
    path('seller_products/<int:user_id>', views.SellerProducts.as_view(), name="seller_products"),
    path('shoppingbrands', views.ShoppingBrands.as_view(), name="shoppingbrands"),
    path('shoppingcategories', views.ShoppingCategories.as_view(), name="shoppingcategories"),
    path('homeads', views.HomeAds.as_view(), name="homeads"),
    path('shoppingads', views.ShoppingAds.as_view(), name="shoppingads"),
    path('restaurantads', views.RestaurantAds.as_view(), name="restaurantads"),
    path('bookingads', views.BookingAds.as_view(), name="bookingads"),
]
