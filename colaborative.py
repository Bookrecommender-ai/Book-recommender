# -*- coding: utf-8 -*-
"""Collaborative Recommender System"""

# Import libraries
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process  # For fuzzy matching
import os
import warnings

# To ignore warnings
warnings.filterwarnings('ignore')

# Import data
books_path = r'D:\python\Bookrecommender\data\Books.csv'
users_path = r'D:\python\Bookrecommender\data\Users.csv'
ratings_path = r'D:\python\Bookrecommender\data\Ratings.csv'

# Check if files exist
if not os.path.exists(books_path):
    raise FileNotFoundError(f"{books_path} file not found.")
if not os.path.exists(users_path):
    raise FileNotFoundError(f"{users_path} file not found.")
if not os.path.exists(ratings_path):
    raise FileNotFoundError(f"{ratings_path} file not found.")


books = pd.read_csv(r'D:\python\Bookrecommender\data\Books.csv')  # Books data
users = pd.read_csv(r'D:\python\Bookrecommender\data\Users.csv')  # Users location and age data
ratings = pd.read_csv(r'D:\python\Bookrecommender\data\Ratings.csv')  # Users rating data


# Preprocess books data
books = books.dropna()  # Drop null values
books['Year-Of-Publication'] = books['Year-Of-Publication'].astype('int32')  # Convert year to integer

# Preprocess users data
users = users.dropna()  # Drop null values

# Check for duplicates and clean data
books = books.drop_duplicates()
users = users.drop_duplicates()
ratings = ratings.drop_duplicates()

# Joining books and user ratings into one table
books_with_ratings = ratings.merge(books, on='ISBN')

# Select only users who rated at least 200 books (power users)
user_ratings_count = books_with_ratings.groupby('User-ID').count()['Book-Rating']
power_users = user_ratings_count[user_ratings_count > 200].index
filtered_ratings = books_with_ratings[books_with_ratings['User-ID'].isin(power_users)]

# Select only books rated by at least 50 users
book_ratings_count = filtered_ratings.groupby('Book-Title').count()['User-ID']
famous_books = book_ratings_count[book_ratings_count >= 50].index
final_ratings = filtered_ratings[filtered_ratings['Book-Title'].isin(famous_books)]

# Create a pivot table of book ratings
pt = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating').fillna(0)

# Calculate similarity scores
similarity_scores = cosine_similarity(pt)

# Define recommendation function
def recommend(book_name):
    """
    Recommends books based on a given book name, using collaborative filtering.
    Handles typographical errors using fuzzy matching.
    """
    # Fuzzy matching to find the closest book title
    closest_match = process.extractOne(book_name, pt.index)
    if closest_match is None or closest_match[1] < 70:  # Confidence threshold
        return f"No close match found for '{book_name}'. Please try again with a different book name."

    matched_book_name = closest_match[0]  # Get the matched book title
    print(f"Closest match found: {matched_book_name}")

    # Get the index of the matched book
    index = np.where(pt.index == matched_book_name)[0][0]

    # Find similar books based on cosine similarity
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    # Populate recommendations
    recommendations = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        title = temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0]
        author = temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0]
        recommendations.append(f"Title: {title}, Author: {author}")

    return recommendations

# Print recommendations one by one
def print_recommendations(book_name):
    recommendations = recommend(book_name)
    if isinstance(recommendations, str):  # If no match found, print the error message
        print(recommendations)
    else:
        print("Recommendations:")
        for idx, recommendation in enumerate(recommendations, start=1):
            print(f"{idx}. {recommendation}")

# Example usage
if __name__ == "__main__":
    print("Example Recommendation for 'Anumal Frm' (Typo for 'Animal Farm'):")
    print_recommendations('Anumal Frm')
    
    print("\nExample Recommendation for 'The Hours : A Novel':")
    print_recommendations('The Hours : A Novel')
