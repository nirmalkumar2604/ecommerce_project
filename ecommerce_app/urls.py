from django.urls import path
from . import views

urlpatterns = [
    # Authentication APIs
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("forget_password/", views.ForgetPasswordView.as_view(), name="forget_password"),
    path("reset_password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path("verify_otp/", views.VerifyOTPView.as_view(), name="verify_otp"),

    # Products
    path("add_product/", views.AddProductPageView.as_view(), name="add_product"),
    path("edit_product/<int:pk>/", views.EditProductView.as_view(), name="edit_product"),
    path("delete_product/<int:pk>/", views.DeleteProductView.as_view(), name="delete_product"),
    path("view_all_products/", views.ViewAllProducts.as_view(), name="view_all_products"),


    path("add_to_cart/", views.Addproducttocartview.as_view(), name="add_to_cart"),
    path("update_cart/", views.UpdateCartView.as_view(), name="update_cart"),
    path("remove_cart_item/", views.RemoveCartItemView.as_view(), name="remove_cart_item"),
    path("clear_cart/", views.ClearCartView.as_view(), name="clear_cart"),






    # Cart
    path("add_to_cart/", views.Addproducttocartview.as_view(), name="add_to_cart"),
    path("api/cart/", views.CartDataView.as_view(), name="cart"),
    path("update_cart/", views.UpdateCartView.as_view(), name="update_cart"),
    path("remove_cart_item/", views.RemoveCartItemView.as_view(), name="remove_cart_item"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),

    path("clear_cart/",views.ClearCartView.as_view(), name="clear_cart"),
    
    # path("update_cart_quantity/",views.UpdateCartQuantityView.as_view(), name="update_cart_quantity"),
    path("api/update_cart/", views.UpdateCartView.as_view(), name="update_cart"),
    path("api/remove_cart_item/", views.RemoveCartItemView.as_view(), name="remove_cart_item"),
    path("api/clear_cart/", views.ClearCartView.as_view(), name="clear_cart"),
    path("api/checkout/", views.CheckoutView.as_view(), name="checkout"),


    # Orders & Payments
    path("api/checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("view_orders/", views.ViewOrdersAPI.as_view(), name="view_orders"),

    # path("order_list/", views.Orderlistview.as_view(), name="order_list"),
    path("view_order_detail/<int:order_id>/", views.ViewOrderDetailAPI.as_view(), name="view_order_detail"),

    
    # Addresses
    path("add_address/", views.AddressCreateView.as_view(), name="add_address"),
    path("address_list/", views.AddressListView.as_view(), name="address_list"),
    path("address_delete/", views.AddressDeleteView.as_view(), name="address_delete"),


    # Misc
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("product_detail/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("user_profile/", views.UserProfileView.as_view(), name="user_profile"),
    path("search_products/", views.ProductSearchView.as_view(), name="search_products"),
]
