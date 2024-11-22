from flask import Flask, render_template, request
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Initialize Flask app
app = Flask(__name__)

# Load dataset
df = pd.read_csv('animal.csv')


# Scraping function to fetch image URL
def fetch_image(animal_name):
    # Replace spaces with underscores for URL compatibility
    animal_query = animal_name.replace(' ', '_').lower()

    # Try Pixabay
    pixabay_url = f"https://pixabay.com/images/search/{animal_query}/"
    response = requests.get(pixabay_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', class_='lazy')
        if img_tag and img_tag['src']:
            return img_tag['src']

    # Try Unsplash
    unsplash_url = f"https://unsplash.com/s/photos/{animal_query}"
    response = requests.get(unsplash_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', class_='_2UpQX')
        if img_tag and img_tag['src']:
            return img_tag['src']

    # Try Wikipedia
    wiki_url = f"https://en.wikipedia.org/wiki/{animal_query.capitalize()}"
    response = requests.get(wiki_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and img_tag['src']:
            return f"https:{img_tag['src']}"

    # Default to placeholder image
    return "/static/images/placeholder.jpg"


@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.form.get('query', '').lower()  # Search query
    if query:
        filtered_df = df[df['species'].str.contains(query, case=False, na=False)]
    else:
        filtered_df = df

    # Add images to the dataset
    filtered_df['image_url'] = filtered_df['species'].apply(fetch_image)

    # Pass data to template
    animals = filtered_df.to_dict(orient='records')
    return render_template('index.html', animals=animals, query=query)


if __name__ == '__main__':
    app.run(debug=True)
