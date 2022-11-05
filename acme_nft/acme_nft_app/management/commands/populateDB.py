from django.core.management.base import BaseCommand, CommandError
import csv
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Populates the database with some initial data'

    def handle(self, *args, **options):
        print("Starting Acme NFT population script...")

        path = Path(__file__).parent / "../../static/dataset/dataset.csv"
        lines = []

        with path.open() as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    lines.append(row)
                    line_count += 1
                else:
                    lines.append(row)
                    img_path = "~/Desktop/" + row[14].replace("./", "")
                    print(img_path)
                    
                    if os.path.exists(img_path):
                        print("YES")

                    line_count += 1
        
        print(f'Processed {line_count} lines.')