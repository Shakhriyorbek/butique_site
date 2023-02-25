from .models import Product, OrderProduct, Order


class CartForAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None, quantity=None):
        self.user = request.user

        if product_id and action and quantity:
            self.add_or_delete(product_id, action, quantity)

    def get_cart_info(self):
        order, created = Order.objects.get_or_create(user=self.user)
        order_products = order.orderproduct_set.all()

        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price

        return {
            'cart_total_quantity' : cart_total_quantity,
            'cart_total_price': cart_total_price,
            'order': order,
            'products': order_products

        }

    def add_or_delete(self, product_id, action, quantity):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)

        if action == 'add' and product.quantity >= quantity:
            order_product.quantity += quantity  # + в заказ
            product.quantity -= quantity  # - со склада
        else:
            order_product.quantity -= quantity
            product.quantity += quantity
        order_product.save()
        product.save()

        if order_product.quantity <= 0:
            order_product.delete()

    def clear(self):
        order = self.get_cart_info()['order']
        order_products = order.orderproduct_set.all()
        for product in order_products:
            product.delete()
        order.save()






