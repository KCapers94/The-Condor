#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc
from datetime import date, time


# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, Category, Activity, Date

if __name__ == '__main__':
    fake = Faker()
    with app.app_context():
        print("Starting seed...")
        # Seed code goes here!

        Activity.query.delete()
        Date.query.delete()
        Category.query.delete()

        category = [
        Category(name='Breakfast Date'),
        Category(name='Lunch Date'),
        Category(name='Dinner Date'),
        Category(name='Movie Date')
        ]

        db.session.add_all(category)
        db.session.commit()


        dates = [
        Date(date=date(2025,1,24), time=time(10,00,00), description='Date with Loretta',user_id=1, category_id=1),
        Date(date=date(2025,1,31), time=time(8,00,00), description='Date with Karen', user_id=1, category_id=2),
        Date(date=date(2025,2,5), time=time(7,00,00), description='Date with Karen', user_id=1, category_id=3)]

        db.session.add_all(dates)
        db.session.commit()


        activities = [
        Activity(name='Tops Diner', date_id=1),
        Activity(name='Dancing', date_id=3),
        Activity(name='Paint Ball', date_id=2)
        ]

        

        db.session.add_all(activities)
        db.session.commit()