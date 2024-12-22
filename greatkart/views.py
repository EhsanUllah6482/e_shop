import csv
import os
from django.conf import settings
from django.shortcuts import render
from store.models import Product

def load_ratings():
    ratings_file_path = os.path.join(settings.BASE_DIR, 'data', 'ratings.csv')
    ratings = []
    with open(ratings_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ratings.append({
                'user_id': int(row['user_id']),
                'product_id': int(row['product_id']),
                'rating': float(row['rating']),
            })
    
    return ratings

def home(request):
    # Load ratings for product recommendations
    ratings = load_ratings()
    product_ratings = {}
    for rating in ratings:
        product_id = rating['product_id']
        if product_id not in product_ratings:
            product_ratings[product_id] = []
        product_ratings[product_id].append(rating['rating'])
    for product_id, ratings_list in product_ratings.items():
        average_rating = sum(ratings_list) / len(ratings_list)
        product_ratings[product_id] = average_rating

    products = Product.objects.filter(is_available=True).order_by('created_date')

    # Attach average ratings to products
    for product in products:
        product.average_rating = product_ratings.get(product.id, 0)
        product.discounted_price = product.price

    products = sorted(products, key=lambda p: p.average_rating, reverse=True)
    context = {
        'products': products,
        'is_black_friday_sale': products and products[0].is_black_friday_sale,  # Check if sale is active
    }
    return render(request, 'home.html', context)

