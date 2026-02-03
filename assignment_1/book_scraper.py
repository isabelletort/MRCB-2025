# Import required libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Initialize an empty list to store all book data
all_books = []

# Step 1: Scrape all pages from books.toscrape.com
print("Starting to scrape books.toscrape.com...")

# Start with page 1 and continue until no more pages are found
page_num = 1
while True:
    try:
        # Construct the URL for the current page
        if page_num == 1:
            url = "https://books.toscrape.com/index.html"
        else:
            url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
        
        print(f"Scraping page {page_num}...")
        
        # Step 2: Download the webpage with error handling
        response = requests.get(url, timeout=10)
        
        # If we get a 404, we've reached the end of available pages
        if response.status_code == 404:
            print(f"Reached the end at page {page_num - 1}")
            break
        
        # Raise an exception for other bad status codes
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Step 3: Find all book containers on the current page
        books = soup.find_all('article', class_='product_pod')
        
        # If no books found, we've reached the end
        if not books:
            print(f"No books found on page {page_num}. Stopping.")
            break
        
        # Step 4: Extract data from each book
        for book in books:
            try:
                # Extract the book title from the h3 > a element's title attribute
                title = book.h3.a['title']
                
                # Extract the price and clean it (remove £ symbol and convert to float)
                price_text = book.find('p', class_='price_color').text
                price = float(price_text.replace('£', '').strip())
                
                # Extract the star rating from the second class name (e.g., "Three")
                rating = book.p['class'][1]
                
                # Add the book data to our list
                all_books.append({'title': title, 'price': price, 'rating': rating})
                
            except (AttributeError, ValueError, KeyError) as e:
                # Handle errors for individual books (e.g., missing data)
                print(f"Error parsing book on page {page_num}: {e}")
                continue
        
        # Move to the next page
        page_num += 1
        
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        print(f"Error fetching page {page_num}: {e}")
        break
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error on page {page_num}: {e}")
        break

# Step 5: Save the data to a CSV file
if all_books:
    df = pd.DataFrame(all_books)
    df.to_csv('books.csv', index=False)
    print(f"\nSuccessfully saved {len(all_books)} books to books.csv")
    
    # Step 6: Print summary statistics
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    
    # Total number of books scraped
    print(f"Total books scraped: {len(all_books)}")
    
    # Average price
    avg_price = df['price'].mean()
    print(f"Average price: £{avg_price:.2f}")
    
    # Number of books per rating
    print("\nBooks per rating:")
    rating_counts = df['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        print(f"  {rating}: {count} books")
    
    print("="*50)
else:
    print("No books were scraped. Please check the website or your connection.")

