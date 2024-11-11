from django.db import models
from datetime import datetime
import csv
import os

class Voter(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=10)
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'newton_voters.csv')

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            first_name = row['First Name']
            last_name = row['Last Name']
            street_number = row['Residential Address - Street Number']
            street_name = row['Residential Address - Street Name']
            apartment_number = row.get('Residential Address - Apartment Number', '')
            zip_code = row['Residential Address - Zip Code']
            date_of_birth = datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date()
            date_of_registration = datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date()
            party_affiliation = row['Party Affiliation']
            precinct_number = row['Precinct Number']
            v20state = row['v20state'] == 'TRUE'
            v21town = row['v21town'] == 'TRUE'
            v21primary = row['v21primary'] == 'TRUE'
            v22general = row['v22general'] == 'TRUE'
            v23town = row['v23town'] == 'TRUE'
            voter_score = int(row['voter_score'])

            Voter.objects.create(
                first_name=first_name,
                last_name=last_name,
                street_number=street_number,
                street_name=street_name,
                apartment_number=apartment_number,
                zip_code=zip_code,
                date_of_birth=date_of_birth,
                date_of_registration=date_of_registration,
                party_affiliation=party_affiliation,
                precinct_number=precinct_number,
                v20state=v20state,
                v21town=v21town,
                v21primary=v21primary,
                v22general=v22general,
                v23town=v23town,
                voter_score=voter_score,
            )