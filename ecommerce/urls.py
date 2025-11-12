from django.contrib import admin
from django.urls import path, include
from ecommerce_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Panel
    path("admin/", admin.site.urls),

    # API ROUTES
    path("api/", include("ecommerce_app.urls")),

    # UI ROUTES
    path("", views.HomeView.as_view(), name="home"),
    path("ui/register/", views.RegisterPageView.as_view(), name="ui_register"),
    path("ui/login/", views.LoginPageView.as_view(), name="ui_login"),
    path("ui/logout/", views.LogoutView.as_view(), name="ui_logout"),
    path("ui/add_product/", views.AddProductPageView.as_view(), name="ui_add_product"),
    path("ui/product_list/", views.ProductListView.as_view(), name="ui_product_list"),
    path("ui/cart/", views.CartPageView.as_view(), name="ui_cart"),
    path("ui/cart/", views.CartDataView.as_view(), name="ui_cart"),
    path("ui/add_product_to_cart/", views.Addproducttocartview.as_view(), name="ui_add_product_to_cart"),

    path("ui/orders/", views.OrdersPageView.as_view(), name="ui_orders"),
    path("ui/order_detail/", views.OrderDetailPageView.as_view(), name="order_detail"),
    path("ui/forget_password/", views.ForgetPasswordPageView.as_view(), name="ui_forget_password"),
    path("ui/reset_password/", views.ResetPasswordPageView.as_view(), name="ui_reset_password"),
    path("ui/verify_otp/", views.VerifyOTPPageView.as_view(), name="ui_verify_otp"),
    path("ui/add_to_cart/", views.Addproducttocartview.as_view(), name="ui_add_to_cart"),

]


# Static and Media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
