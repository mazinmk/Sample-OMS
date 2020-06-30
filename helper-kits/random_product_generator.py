import namegenerator
import random

list_products = []
route_type = [1,2]
product_categories = ["Grocery","Household Essentials","Women","Men","Young Adults","Kids","Baby","Shoes","Home","Furniture","Toys"]
for i in range(1000,1500):
    dict_products = {}
    random_product_name = namegenerator.gen()
    dict_products["product_id"] = i
    dict_products["product_name"] = random_product_name
    dict_products["route_id"] = random.choice(route_type)
    dict_products["category"] = random.choice(product_categories)
    print (dict_products)

