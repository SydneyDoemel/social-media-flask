# from flask import Blueprint, request, redirect
# from ..apiauthhelper import token_required
# from app.models import User, Product, cart
# import stripe

# shop = Blueprint('shop', __name__)

# @shop.route('/api/products')
# def getAllProducts():
#     products = Product.query.all()

#     return {
#         'status': 'ok',
#         'products': [p.to_dict() for p in products] 
#     }

# @shop.route('/api/products/<int:product_id>')
# def getOneProduct(product_id):
#     product = Product.query.get(product_id)
#     return {
#         'status': 'ok',
#         'product': product.to_dict()
#     }

# @shop.route('/api/cart')
# @token_required
# def getCart(user):

#     return {
#         'status': 'ok',
#         'cart': [p.to_dict() for p in user.getCart()]
#         }

# @shop.route('/api/cart/add', methods=["POST"])
# @token_required
# def addToCart(user):
#     data = request.json
#     product_id = data['productId']
#     product = Product.query.get(product_id)
#     user.addToCart(product)
#     return {'status': 'ok','message': 'Succesfully added to cart.'}

# @shop.route('/api/cart/remove', methods=["POST"])
# @token_required
# def removeFromCart(user):
#     data = request.json
#     product_id = data['productId']
#     product = Product.query.get(product_id)
#     user.removeFromCart(product)
#     return {'status':'ok', 'message':'Successfully removed from cart.'}



# ####### STRIP CHECKOUT ROUTE #############
# stripe.api_key = 'sk_test_51LaSpGAOPmNTqh49ym0T8zsBS31YhIt9tXSPkODHp50B2iUSTYs98TOG59hQFGWZYg884LqQKhdhE9pnAQ75V0UF00hit063Z6'


# @shop.route('/stripe-checkout', methods=["POST"])
# def createCheckoutSession():
#     data = request.form
#     line_items = []
#     for entry in data:
#         line_items.append({
#             'price': entry,
#             'quantity': data[entry]
#         })
    
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=line_items,
#             mode='payment',
#             success_url='http://localhost:3000' + '?success=true',
#             cancel_url='http://localhost:3000' + '?canceled=true',
#         )
#     except Exception as e:
#         return str(e)

#     return redirect(checkout_session.url, code=303)