import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order
from .cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

# Vista per la lista dei prodotti
def product_list(request):
    products = Product.objects.filter(available=True)
    return render(request, 'store/product_list.html', {'products': products})

# Vista per il dettaglio di un prodotto
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

# Vista per aggiungere un prodotto al carrello
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('product_list')

# Vista per rimuovere un prodotto dal carrello
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

# Vista per visualizzare il carrello
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

# Vista per il checkout con Stripe
def checkout(request):
    cart = Cart(request)
    total_amount = sum(item['total_price'] for item in cart)

    if request.method == 'POST':
        try:
            charge = stripe.Charge.create(
                amount=int(total_amount * 100),  # Convertiamo in centesimi
                currency='eur',
                description='Acquisto su Ecommerce',
                source=request.POST['stripeToken']  # Token fornito da Stripe
            )
            cart.clear()  # Svuotiamo il carrello dopo il pagamento
            return redirect('success')  # Reindirizziamo alla pagina di successo
        except stripe.error.StripeError:
            return redirect('checkout')

    return render(request, 'store/checkout.html', {'total_amount': total_amount, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})

# Vista per la pagina di conferma dell'ordine
def success(request):
    return render(request, 'store/success.html')
