from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from django.views.generic import TemplateView
from datetime import datetime
from django.shortcuts import render
from django.views import View
from .serializers import AddToCartSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.models import User
from .models import Product, Cart
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
from django.db import IntegrityError





def year_context(request):
    return {'year': datetime.now().year}


from .models import (
    Product, Cart, Order, OrderItem,Wishlist, Address, Notification, PasswordResetOTP
)

from django.views.generic import TemplateView
from .models import Product

class HomeView(TemplateView):
    template_name = "e-com/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_products"] = Product.objects.all()[:4]
        return context

# ─────────────────────────────
# Auth
# ─────────────────────────────

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if not all([username, email, password, password2]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        if password != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User registered successfully!", "user_id": user.id}, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    authentication_classes = []  # Disable session and token checks
    permission_classes = []      # Allow anyone to call this API

    def post(self, request):
        username_or_email = request.data.get("username")
        password = request.data.get("password")

        if not username_or_email or not password:
            return Response({"error": "Username/Email and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Allow login using either email or username
        if "@" in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                return Response({"error": "No account found with this email."},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            username = username_or_email

        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials."},
                            status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return redirect("/ui/login/") # Redirect to home page after logout

    

# ─────────────────────────────
# Password reset via OTP
# ─────────────────────────────

class ForgetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

        import random
        otp = f"{random.randint(100000, 999999)}"

        PasswordResetOTP.objects.update_or_create(user=user, defaults={"otp": otp})

        send_mail(
            subject="Password Reset OTP",
            message=f"Your OTP for password reset is: {otp}. It is valid for 15 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"message": "OTP has been sent to your email."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not all([email, otp]):
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            otp_obj = PasswordResetOTP.objects.get(user=user)  # OneToOne
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "No OTP found for this user."}, status=status.HTTP_404_NOT_FOUND)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)
        if otp_obj.otp != str(otp):
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)


# from django.contrib.auth.models import User
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        new_password2 = request.data.get("new_password2")

        # Step 1: Validate email field
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Find user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

        # Step 3: Confirm password fields match
        if new_password != new_password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Step


# ─────────────────────────────
# Profile & User delete
# ─────────────────────────────

class UserProfileView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined,
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if username:
            user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)



class Deleteuserview(APIView):
    def delete(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)

# ─────────────────────────────
# Products
# ─────────────────────────────
# class AddProductView(APIView):
#     def post(self, request):
#         name = request.data.get('name')
#         price = request.data.get('price')
#         description = request.data.get('description', "")
#         category = request.data.get('category', "")
#         stock = request.data.get('stock', 0)
#         image = request.data.get('image', "")  # ✅ Accept image URL

#         if not all([name, price]):
#             return Response({"error": "name and price are required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             price = Decimal(str(price))
#             stock = int(stock)
#         except (ValueError, TypeError):
#             return Response({"error": "Invalid price or stock."}, status=status.HTTP_400_BAD_REQUEST)

#         product = Product.objects.create(
#             name=name,
#             price=price,
#             description=description,
#             category=category,
#             stock=stock,
#             image=image,  # ✅ Save image URL
#             created_by=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
#         )

#         return Response({
#             "message": "Product added successfully!",
#             "product": {
#                 "id": product.id,
#                 "name": product.name,
#                 "price": float(product.price),
#                 "description": product.description,
#                 "category": product.category,
#                 "stock": product.stock,
#                 "image": product.image,
#             }
#         }, status=status.HTTP_201_CREATED)
class AddProductPageView(APIView):
    def post(self, request):
        name = request.data.get("name")
        price = request.data.get("price")
        description = request.data.get("description", "")
        category = request.data.get("category", "")
        image_url = request.data.get("image", "")

        if not all([name, price, image_url]):
            return Response({"error": "Name, price, and image URL are required."}, status=400)

        product = Product.objects.create(
            name=name,
            price=price,
            description=description,
            category=category,
            image=image_url,  # <–– store URL here
            created_by=request.user if request.user.is_authenticated else None
        )

        return Response({"message": f"{product.name} added successfully!"}, status=201)


class ProductDetailView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
            data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "category": product.category,
                "image": product.image.url if product.image else None,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


class EditProductView(APIView):
    def patch(self, request):
        product_id = request.data.get('id')
        if not product_id:
            return Response({"error": "id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=int(product_id))
        except (Product.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Optional updates
        for key, attr in [
            ("name", "name"),
            ("description", "description"),
            ("category", "category"),
            ("image", "image"),
        ]:
            val = request.data.get(key)
            if val is not None:
                setattr(product, attr, val)

        if "price" in request.data:
            try:
                product.price = Decimal(str(request.data.get("price")))
                if product.price < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({"error": "Invalid price."}, status=status.HTTP_400_BAD_REQUEST)

        if "stock" in request.data:
            try:
                product.stock = int(request.data.get("stock"))
                if product.stock < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({"error": "Invalid stock."}, status=status.HTTP_400_BAD_REQUEST)

        product.save()
        return Response({
            "message": "Product edited successfully!",
            "product": {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "description": product.description,
                "category": product.category,
                "stock": product.stock
            }
        }, status=status.HTTP_200_OK)


class DeleteProductView(APIView):
    def delete(self, request):
        product_id = request.data.get('id')
        if not product_id:
            return Response({"error": "id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=int(product_id))
        except (Product.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({"message": "Product deleted successfully!"}, status=status.HTTP_200_OK)


class ViewAllProducts(APIView):
    def get(self, request):
        products = Product.objects.all().order_by("-created_at")
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "stock": p.stock,
                "category": p.category,
                "image": p.image or "",  # ✅ Include image field
            }
            for p in products
        ]
        return Response({"products": product_list}, status=status.HTTP_200_OK)




class ProductSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        products = Product.objects.filter(name__icontains=query).order_by("-created_at")
        data = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "category": p.category,
                "stock": p.stock,
                "image": getattr(p, "image", ""),
            }
            for p in products
        ]
        return Response({"products": data}, status=status.HTTP_200_OK)
    
class ProductListView(View):
    def get(self, request):
        products = Product.objects.all().order_by("-id")
        print("🧩 Products count:", products.count())  # Debug line — check console
        return render(request, "e-com/product_list.html", {"products": products})    
  

# ─────────────────────────────
# Cart
# ─────────────────────────────
# class UpdateCartView(APIView):
#     def post(self, request):
#         cart_id = request.data.get("cart_id")
#         quantity = int(request.data.get("quantity", 1))
#         try:
#             cart_item = Cart.objects.get(id=cart_id)
#             cart_item.quantity = quantity
#             cart_item.save()
#             return Response({"message": "Cart updated successfully"})
#         except Cart.DoesNotExist:
#             return Response({"error": "Cart item not found"}, status=404)

# class RemoveCartItemView(APIView):
#     def post(self, request):
#         cart_id = request.data.get("cart_id")
#         try:
#             Cart.objects.get(id=cart_id).delete()
#             return Response({"message": "Item removed successfully"})
#         except Cart.DoesNotExist:
#             return Response({"error": "Item not found"}, status=404)

class ClearCartView(APIView):
    def post(self, request):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response({"message": "Cart cleared successfully"})




@method_decorator(csrf_exempt, name="dispatch")
class Addproducttocartview(APIView):
    def post(self, request):
        print("🚀 Add to Cart called")

        if not request.user.is_authenticated:
            return Response(
                {"error": "Please login before adding to cart."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ✅ FIXED JSON parsing
        try:
            # Handle both DRF and raw Django requests safely
            if hasattr(request, "data") and request.data:
                data = request.data
            else:
                raw_body = request.body.decode("utf-8").strip()
                print("📦 Raw body:", raw_body)
                data = json.loads(raw_body) if raw_body else {}

            product_id = data.get("product_id")
            print("🆔 Product ID received:", product_id)

            if not product_id:
                return Response({"error": "Product ID is missing."}, status=400)
        except json.JSONDecodeError:
            print("❌ JSON decode error")
            return Response({"error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            print("❌ Unknown parsing error:", e)
            return Response({"error": "Invalid request format."}, status=400)

        # ✅ Fetch product
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({"error": "Product not found."}, status=404)

        try:
            # ✅ Create or update cart
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={"quantity": 1, "name": product.name},
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            print(f"✅ Added {product.name} (x{cart_item.quantity}) to {request.user.username}'s cart")

            return Response(
                {"message": f"{product.name} added to cart successfully!"},
                status=200
            )

        except IntegrityError:
            cart_item = Cart.objects.get(user=request.user, product=product)
            cart_item.quantity += 1
            cart_item.save()
            return Response({"message": "Cart updated successfully."}, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)



@method_decorator(login_required, name="dispatch")
class CartDataView(View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user).select_related('product')
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context = {
            "cart_items": cart_items,
            "total_price": total_price,
        }
        return render(request, "e-com/cart.html", context)


@method_decorator(login_required, name="dispatch")
class CartPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Make sure to select_related to avoid N+1 queries
            cart_items = Cart.objects.filter(user=request.user).select_related('product')
            total_price = sum(item.product.price * item.quantity for item in cart_items)
        else:
            # Handle session-based cart for anonymous users
            cart_items = []
            total_price = 0
        
        context = {
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, 'e-com/cart.html', context)




@method_decorator(login_required, name="dispatch")
class UpdateCartView(APIView):
    def post(self, request):
        try:
            cart_id = request.data.get("cart_id")
            action = request.data.get("action")

            cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()
            if not cart_item:
                return Response({"error": "Cart item not found."}, status=404)

            if action == "increase":
                cart_item.quantity += 1
            elif action == "decrease" and cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                return Response({"error": "Invalid action."}, status=400)

            cart_item.save()
            return Response({"message": "Quantity updated.", "new_quantity": cart_item.quantity})

        except Exception as e:
            print("Update Cart Error:", e)
            return Response({"error": "Internal server error."}, status=500)


# -----------------------
# Remove Item from Cart
# -----------------------
@method_decorator(login_required, name="dispatch")
class RemoveCartItemView(APIView):
    def post(self, request):
        try:
            cart_id = request.data.get("cart_id")
            cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()
            if not cart_item:
                return Response({"error": "Cart item not found."}, status=404)

            cart_item.delete()
            return Response({"message": "Item removed from cart."}, status=200)
        except Exception as e:
            print("Remove Item Error:", e)
            return Response({"error": "Internal server error."}, status=500)


# -----------------------
# Checkout (Create Order)
# -----------------------
@method_decorator(login_required, name="dispatch")
class CheckoutView(APIView):
    def post(self, request):
        try:
            user = request.user
            cart_items = Cart.objects.filter(user=user)
            if not cart_items.exists():
                return Response({"error": "Your cart is empty."}, status=400)

            total_price = sum(item.subtotal for item in cart_items)

            # Create Order
            order = Order.objects.create(user=user, total_price=total_price, status="Paid")

            # Clear the cart after checkout
            cart_items.delete()

            return Response({"message": "Order placed successfully!", "order_id": order.id}, status=200)
        except Exception as e:
            print("Checkout Error:", e)
            return Response({"error": "Internal server error."}, status=500)
        


@method_decorator(login_required, name="dispatch")
class ViewOrdersAPI(View):
    def get(self, request):
        try:
            user = request.user
            print("📦 Fetching orders for:", user.username)

            orders = Order.objects.filter(user=user).order_by("-created_at")
            order_list = [
                {
                    "id": o.id,
                    "created_at": o.created_at.strftime("%Y-%m-%d %H:%M"),
                    "status": o.status,
                    "total_price": float(o.total_price),
                }
                for o in orders
            ]
            return JsonResponse({"orders": order_list}, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)  



# class CheckoutView(APIView):
#     def post(self, request):
#         try:
#             user = request.user if request.user.is_authenticated else None
#             if not user:
#                 return Response(
#                     {"error": "User not authenticated"},
#                     status=status.HTTP_401_UNAUTHORIZED
#                 )

#             cart_items = Cart.objects.filter(user=user)
#             if not cart_items.exists():
#                 return Response(
#                     {"error": "Your cart is empty."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             total_price = sum(item.subtotal for item in cart_items)

#             # ✅ Create an order record
#             order = Order.objects.create(
#                 user=user,
#                 total_price=total_price,
#                 status="Pending"
#             )

#             # Optionally clear the cart
#             cart_items.delete()

#             return Response(
#                 {
#                     "message": "Checkout successful!",
#                     "order_id": order.id,
#                     "total_price": total_price
#                 },
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             print("Checkout Error:", str(e))
#             return Response(
#                 {"error": "Something went wrong. Please try again."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )



class OrderDetailPageView(View):
    def get(self, request):
        return render(request, "e-com/order_detail.html")



@method_decorator(login_required, name="dispatch")
class ViewOrderDetailAPI(View):
    def get(self, request, order_id):
        try:
            order = (
                Order.objects.filter(id=order_id, user=request.user)
                .select_related("user")
                .prefetch_related("items__product")
                .first()
            )

            if not order:
                return JsonResponse({"error": "Order not found"}, status=404)

            items = [
                {
                    "name": item.product.name,
                    "price": float(item.product.price),
                    "quantity": item.quantity,
                    "subtotal": float(item.product.price * item.quantity),
                }
                for item in order.items.all()
            ]

            data = {
                "id": order.id,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": order.status,
                "total_price": float(order.total_price),
                "items": items,
            }

            return JsonResponse(data, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)



# ─────────────────────────────
# Addresses (user address book)
# ─────────────────────────────

class AddressCreateView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        street = request.data.get('street')
        city = request.data.get('city')
        state = request.data.get('state')
        zip_code = request.data.get('zip_code')

        if not all([user_id, street, city, state, zip_code]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        address = Address.objects.create(
            user=user, street=street, city=city, state=state, zip_code=zip_code
        )
        return Response({
            "message": "Address created successfully.",
            "address_id": address.id,
            "street": address.street, "city": address.city, "state": address.state, "zip_code": address.zip_code
        }, status=status.HTTP_201_CREATED)


class AddressUpdateView(APIView):
    def patch(self, request):
        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"error": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            address = Address.objects.get(id=int(address_id))
        except (Address.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

        for f in ["street", "city", "state", "zip_code"]:
            val = request.data.get(f)
            if val:
                setattr(address, f, val)
        address.save()
        return Response({
            "message": "Address updated successfully.",
            "address_id": address.id,
            "street": address.street, "city": address.city, "state": address.state, "zip_code": address.zip_code
        }, status=status.HTTP_200_OK)


class AddressDeleteView(APIView):
    def delete(self, request):
        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"error": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            address = Address.objects.get(id=int(address_id))
        except (Address.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        address.delete()
        return Response({"message": "Address deleted successfully."}, status=status.HTTP_200_OK)


class AddressListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        addresses = Address.objects.filter(user=user)
        data = [{
            "address_id": a.id,
            "street": a.street, "city": a.city, "state": a.state, "zip_code": a.zip_code
        } for a in addresses]
        return Response({"addresses": data}, status=status.HTTP_200_OK)

# ─────────────────────────────
# Notifications
# ─────────────────────────────

class NotificationListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        data = [{
            "notification_id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at,
        } for n in notifications]
        return Response({"notifications": data}, status=status.HTTP_200_OK)
    


# ─────────────────────────────
# UI Template Views (for /ui/... routes)
# ─────────────────────────────
class HomeView(TemplateView):
    template_name = "e-com/home.html"


class RegisterPageView(TemplateView):
    template_name = "e-com/register.html"

class LoginPageView(TemplateView):
    template_name = "e-com/login.html"

class AddProductPageView(TemplateView):
    template_name = "e-com/add_product.html"

class ProductListPageView(TemplateView):
    template_name = "e-com/product_list.html"

# class CartPageView(TemplateView):
#     template_name = "e-com/cart.html"

class OrdersPageView(TemplateView):
    template_name = "e-com/orders.html"

class OrderDetailPageView(TemplateView):
    template_name = "e-com/order_detail.html"

class ForgetPasswordPageView(TemplateView):
    template_name = "e-com/forget_password.html"

class ResetPasswordPageView(TemplateView):
    template_name = "e-com/reset_password.html"

class VerifyOTPPageView(TemplateView):
    template_name = "e-com/verify_otp.html"

