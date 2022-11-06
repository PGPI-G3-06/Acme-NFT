from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import random
from pathlib import Path
from ...models import Product, Category, Author

class Command(BaseCommand):
    help = 'Populates the database with some initial data'

    def handle(self, *args, **options):
        choice = input("Please confirm by typing 'yes', press any other key to exit: ").lower()
        
        if choice == "yes":
            print("Starting Acme NFT population script...")

            path = Path(__file__).parent / "../../static/dataset/dataset.csv"

            datos = pd.read_csv(path, sep=",", header=0, names=["title", "name", "creator", "art_series", "price", "symbol", "type", "likes", "nsfw", "tokens", "year" , "rights", "royalty", "cid", "path"])
            
            for index, row in datos.iterrows():
                
                # Find or create the category
                try:
                    category = Category.objects.get(name=row["type"])
                except:
                    category = Category(name=row["type"])
                    category.save()

                # Find or create the author
                try:
                    author = Author.objects.get(name=row["creator"])
                except:
                    author = Author(name=row["creator"])
                    author.save()
                
                # Create and save the product
                product = Product(name=row["name"], collection=row["title"], price=float(row["price"]), stock=int(row["tokens"]), image_url=row["path"].replace("./", ""), offer_price=None)
                product.save()
                product.category.add(category)
                product.author.add(author)
        
            print("Done! Your product database is now populated with some initial data.")
        else:
            print("Exiting...")
            return