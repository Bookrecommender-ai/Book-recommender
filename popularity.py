# -*- coding: utf-8 -*-
"""Popularity-Based Recommender System"""

# Import libraries
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# File paths (update these paths as per your local environment)
books_path = r'D:\python\Bookrecommender\data\Books.csv'
users_path = r'D:\python\Bookrecommender\data\Users.csv'
ratings_path = r'D:\python\Bookrecommender\data\Ratings.csv'

# Load datasets
try:
    books = pd.read_csv(books_path)
    users = pd.read_csv(users_path)
    ratings = pd.read_csv(ratings_path)
except FileNotFoundError as e:
    print(f"Error: {e}. Please check the file paths.")
    exit()

# Display initial dataset information
print("Books Data:")
print(books.head())
print("\nUsers Data:")
print(users.head())
print("\nRatings Data:")
print(ratings.head())

# Check for null values and handle them
print("\nChecking for null values...")
print("Books:", books.isnull().sum().sum())
print("Users:", users.isnull().sum().sum())
print("Ratings:", ratings.isnull().sum().sum())

books = books.dropna()
users = users.dropna()
ratings = ratings.dropna()

# Remove duplicates
books = books.drop_duplicates()
users = users.drop_duplicates()
ratings = ratings.drop_duplicates()

# Data dimensions after cleaning
print("\nData Dimensions:")
print("Books:", books.shape)
print("Users:", users.shape)
print("Ratings:", ratings.shape)

# Joining books and ratings data
books_with_ratings = ratings.merge(books, on='ISBN')
print("\nMerged Data (Books with Ratings):")
print(books_with_ratings.head())

# Group by Book-Title for popularity metrics
popular_df = books_with_ratings.groupby('Book-Title').agg(
    num_ratings=('Book-Rating', 'count'),
    avg_rating=('Book-Rating', 'mean')
)

# Filter books with more than 300 ratings
popular_df = popular_df[popular_df['num_ratings'] > 300]
popular_df = popular_df.sort_values('avg_rating', ascending=False)

# Limit to top 50 popular books
popular_df = popular_df.head(50)

# Merge with book details for final output
popular_df = popular_df.merge(books, on='Book-Title').drop_duplicates('Book-Title')[[
    'Book-Title', 'Book-Author', 'Image-URL-M', 'num_ratings', 'avg_rating'
]]

# Display the final popularity-based dataframe
print("\nTop 50 Popular Books:")
for i in popular_df:
    print(i,)