from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import random
from pathlib import Path
from ...models import Product, Author, RarityType

class Command(BaseCommand):
    help = 'Populates the database with some initial data'

    def handle(self, *args, **options):
        choice = input("Please confirm by typing 'yes', press any other key to exit: ").lower()
        
        if choice == "yes":
            print("Starting Acme NFT population script...")
            
            # ----------------------------- Load NFTs -----------------------------
            
            def get_rarity(price, stock, mean):
                
                index = price/stock
                
                normaliced_index = index / mean
                
                if normaliced_index < 0.5:
                    return RarityType.common
                elif normaliced_index < 1:
                    return RarityType.rare
                elif normaliced_index < 1.5:
                    return RarityType.epic
                elif normaliced_index < 2:
                    return RarityType.legendary
                elif normaliced_index >= 2:
                    return RarityType.mythic
        
            path = Path(__file__).parent / "../../static/dataset/dataset.csv"

            datos = pd.read_csv(path, sep=",", header=0, names=["title", "name", "creator", "art_series", "price", "symbol", "type", "likes", "nsfw", "tokens", "year" , "rights", "royalty", "cid", "path"])
            
            mean_price_per_stock = (datos["price"]/datos["tokens"]).mean()
            
            for index, row in datos.iterrows():

                # Find or create the author
                try:
                    author = Author.objects.get(name=row["creator"])
                except Author.DoesNotExist:
                    author = Author(name=row["creator"])
                    author.save()
                
                rarity = get_rarity(float(row["price"]), int(row["tokens"]), mean_price_per_stock)
                showcase = rarity == RarityType.mythic or rarity == RarityType.legendary
                # Create and save the product
                product = Product(name=row["name"], collection=row["title"], price=float(row["price"]), stock=int(row["tokens"]), image_url=row["path"].replace("./", ""), offer_price=None, rarity=rarity, author=author, showcase=showcase)
                product.save()
        
            print("Done! Your product database is now populated with some initial data.")
        else:
            print("Exiting...")
    