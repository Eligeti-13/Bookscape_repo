import mysql.connector
import streamlit as st
import pandas as pd
import requests

# DATABASE CONNECTION

connection = mysql.connector.connect(

            host = 'localhost',
            user = 'root',
            password = 'Connection@123',
            database = 'book_shelf',
            autocommit = True)

curr = connection.cursor()

# CREATING BOOKS TABLE
curr.execute('''
CREATE TABLE IF NOT EXISTS books 
            (
            book_id varchar(255) PRIMARY KEY,
            book_title VARCHAR(255),
            book_subtitle TEXT,
            book_authors TEXT,
            book_description TEXT,
            industryIdentifiers TEXT,
            text_readingModes BOOLEAN,
            image_readingMode BOOLEAN,
            page_count int,
            categories TEXT,
            language VARCHAR(50),
            image_links TEXT,
            ratings_count INT,
            average_rating DECIMAL(3, 2),
            country VARCHAR(10),
            saleability VARCHAR(10),
            is_ebook BOOLEAN,
            amount_listPrice FLOAT,
            currencyCode_listPrice  VARCHAR(30),
            amount_retailPrice FLOAT,
            currencyCode_retailPrice VARCHAR(30),
            buyLink TEXT,
            year TEXT,
            publisher TEXT)''')

# TITLE FOR THE PROJECT
st.title("BOOKSCAPE EXPLORER")

# NAVIGATING TO THE TABS
r = st.sidebar.radio('Navigation',['Home','Harvest Hub','Insight Explorer'])

# SAYS WHAT ATUALLY THIS PROJECTS DO
if r == "Home":
    st.write(""" **Bookscape Explorer** is a digital have for book lovers, designed to be more than just a simple online library. 
             It's a curated gateway to literary worlds, a personalized guide through the vast expanse of published works. 
             At its core, the Explorer aims to connect readers with books that resonate with their unique tastes and interests. 
             Bookscape Explorer provides a wealth of information, including detailed book summaries, author and insightful reviews. 
             It's a one-stop shop for book lovers, offering a seamless blend of discovery, communit and personalized guidance. """)

# EXTRACTING THE DATA FROM BOOKS API
if r == "Harvest Hub":
    
    search_term = st.text_input("Search for a book title:")
    max_results = 40

    api_key = "AIzaSyCWs0Kf3jAZ8AEofCA_C5MhYkJcmSrEdKg"
    url = f"https://www.googleapis.com/books/v1/volumes?q={search_term}&maxResults={max_results}&key={api_key}"

    
    if search_term:
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json().get('items', [])
            
            # ITERATING THROUGH FOR LOOP TO FETCH THE DATA FROM APIS
            all_data=[]
            for i in items:
                    data = {'book_id' : i['id'],
                    'book_title': i['volumeInfo'].get('title', 'NA'),
                    'book_subtitle': i['volumeInfo'].get('subtitle','NA'),
                    'book_authors' : i['volumeInfo'].get('authors', []),
                    'book_description' : i['volumeInfo'].get('description', 'NA'),
                    'industryIdentifiers': i['volumeInfo'].get('industryIdentifiers', []),
                    'readingModes' : i['volumeInfo']['readingModes'].get('text', True),
                    'image_readingModes' : i['volumeInfo']['readingModes'].get('text', True),
                    'pageCount' : i['volumeInfo'].get('pageCount', 0),
                    'categories' : i['volumeInfo'].get('categories', ['NA']),
                    'language' : i['volumeInfo'].get('language', 'NA'),
                    'imageLinks' : i['volumeInfo'].get('imageLinks', {}),
                    'ratingsCount' : i['volumeInfo'].get('ratingsCount', 1),
                    'averageRating' : round(float(i['volumeInfo'].get('averageRating', 0)), 2) 
                    if i['volumeInfo'].get('averageRating') is not None else 0.00,
                    'country' : i['accessInfo'].get('country', 'NA'),
                    'saleability' : i['saleInfo'].get('saleability', 'NA'),
                    'isEbook' : i['saleInfo'].get('isEbook', False),
                    'amount_listPrice': i['saleInfo'].get('listPrice', {}).get('amount', 0),
                    'currencyCode_listPrice': i['saleInfo'].get('listPrice', {}).get('currencyCode', 'NA'),
                    'amount_retailPrice': i['saleInfo'].get('retailPrice', {}).get('amount', 0),
                    'currencyCode_retailPrice': i['saleInfo'].get('retailPrice', {}).get('currencyCode', 'NA'),
                    'buyLink' : i['saleInfo'].get('buyLink', 'NA'),
                    'year': i['volumeInfo'].get('publishedDate', 'NA'),
                    'publisher': i['volumeInfo'].get('publisher', 'NA')}
                    all_data.append(data)
            df = pd.DataFrame(all_data)
            st.write(df)

            # INSERTING INTO THE DATABASE
            insert_query = """
                        INSERT IGNORE INTO books(book_id, book_title, book_subtitle, book_authors, book_description, industryIdentifiers,
                        text_readingModes, image_readingMode, page_count, categories, language, image_links, ratings_count, average_rating,
                        country, saleability, is_ebook, amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice,
                        buyLink, year, publisher)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""

            for index, row in df.iterrows():
                                        
                        curr.execute(insert_query, (
                        row['book_id'], row['book_title'], row['book_subtitle'],', '.join(row['book_authors']) if isinstance(row['book_authors'], list) 
                        else row['book_authors'], row['book_description'],
                        ', '.join([f"{identifier.get('type', 'NA')}: {identifier.get('identifier', 'NA')}" 
                        for identifier in row['industryIdentifiers']] 
                        if isinstance(row['industryIdentifiers'], list) else [row['industryIdentifiers']]),
                        row['readingModes'],  row['image_readingModes'],  row['pageCount'],
                        ', '.join(row['categories']) if isinstance(row['categories'], list) else row['categories'],
                        row['language'],
                        ', '.join(row['imageLinks'].values()) if isinstance(row['imageLinks'], dict) else row['imageLinks'],
                        row['ratingsCount'], row['averageRating'], row['country'], row['saleability'], row['isEbook'], row['amount_listPrice'],
                        row['currencyCode_listPrice'], row['amount_retailPrice'], row['currencyCode_retailPrice'], row['buyLink'], 
                        row['year'], row['publisher']
                        ))
            connection.commit()

# EXPLORING THE ANSWERS TO THE BELOW 20 QUESTIONS           
if r == "Insight Explorer":
    questions = [
    "Check Availability of eBooks vs Physical Books",
    "Find the Publisher with the Most Books Published",
    "Identify the Publisher with the Highest Average Rating",
    "Get the Top 5 Most Expensive Books by Retail Price",
    "Find Books Published After 2010 with at Least 500 Pages",
    "List Books with Discounts Greater than 20%",
    "Find the Average Page Count for eBooks vs Physical Books",
    "Find the Top 3 Authors with the Most Books",
    "List Publishers with More than 10 Books",
    "Find the Average Page Count for Each Category",
    "Retrieve Books with More than 3 Authors",
    "Books with Ratings Count Greater Than the Average",
    "Books with the Same Author Published in the Same Year",
    "Books with a Specific Keyword in the Title",
    "Year with the Highest Average Book Price",
    "Count Authors Who Published 3 Consecutive Years",
    "Authors who have published books in the same year but under different publishers.",
    "Average amount_retailPrice of eBooks and physical books.",
    "Books that have an averageRating that is more than two standard deviations away from the average rating of all books.",
    "Publisher with the highest average rating among its books, but only for publishers that have published more than 10 books."
]
    
#Create a dropdown menu using selectbox
    selected_question = st.selectbox("Select a question to explore:", [""] + questions) 
       
    # 1. "Check Availability of eBooks vs Physical Books"

    if selected_question == questions[0]:
        query_1 = 'SELECT book_id, book_title, is_ebook FROM books'
        curr.execute(query_1)
        results = curr.fetchall()
        df_1 = pd.DataFrame(results, columns=['book_id', 'book_title', 'is_ebook'])
        st.write(df_1)

    # 2. "Find the Publisher with the Most Books Published"

    elif selected_question == questions[1]:
        query_2 = """SELECT  publisher, COUNT(book_id) AS book_count
                    FROM books
                    GROUP BY publisher
                    ORDER BY book_count DESC LIMIT 1;
            """
        curr.execute(query_2)
        results = curr.fetchall()
        df_2 = pd.DataFrame(results, columns=['publisher', 'book_count'])
        st.write(df_2)

    # 3. "Identify the Publisher with the Highest Average Rating"

    elif selected_question == questions[2]:
        query_3 = """SELECT publisher, AVG(average_rating) AS avg_rating
                    FROM books
                    GROUP BY  publisher
                    ORDER BY avg_rating DESC LIMIT 1;
            """
        curr.execute(query_3)
        results = curr.fetchall()
        df_3 = pd.DataFrame(results, columns=['publisher', 'average_rating'])
        st.write(df_3)

    # 4. "Get the Top 5 Most Expensive Books by Retail Price"

    elif selected_question == questions[3]:
        query_4 = """SELECT book_id, book_title, amount_retailPrice
                FROM books
                ORDER BY amount_retailPrice DESC LIMIT 5;
            """
        curr.execute(query_4)
        results = curr.fetchall()
        df_4 = pd.DataFrame(results, columns=['book_id', 'book_title','amount_retailPrice'])
        st.write(df_4)

    # 5.  "Find Books Published After 2010 with at Least 500 Pages"

    elif selected_question == questions[4]:
        query_5 = """SELECT book_id,  book_title, year, page_count
                    FROM books
                    WHERE (STR_TO_DATE(year, '%Y/%m/%d') > '2010-12-31' OR year >= '2011') 
                    AND page_count >= 500;
            """
        curr.execute(query_5)
        results = curr.fetchall()
        df_5 = pd.DataFrame(results, columns=['book_id', 'book_title','year', 'page_count'])
        st.write(df_5)

    # 6.  "List Books with Discounts Greater than 20%"

    elif selected_question == questions[5]:
        query_6 = """SELECT book_id,  book_title, (amount_listPrice - amount_retailPrice) AS discount_amount
                    FROM books
                    WHERE (amount_listPrice - amount_retailPrice) / amount_listPrice > 0.20;  -- Discount greater than 20%
            """
        curr.execute(query_6)
        results = curr.fetchall()
        df_6 = pd.DataFrame(results, columns=['book_id', 'book_title', 'discount_amount'])
        st.write(df_6)

    # 7.  "Find the Average Page Count for eBooks vs Physical Books"

    elif selected_question == questions[6]:
        query_7 = '''SELECT is_ebook, AVG(page_count) AS average_page_count
                    FROM books
                    GROUP BY is_ebook;'''
        curr.execute(query_7)
        results = curr.fetchall()
        df_7 = pd.DataFrame(results, columns=['is_ebook', 'average_page_count'])
        st.write(df_7)

    # 8.   "Find the Top 3 Authors with the Most Books"

    elif selected_question == questions[7]:
        query_8 = '''SELECT book_id,  book_title, book_authors, COUNT(books.book_id) AS book_count
                    FROM books
                    GROUP BY book_id, book_title, book_authors
                    ORDER BY book_count DESC
                    LIMIT 3;'''
        curr.execute(query_8)
        results = curr.fetchall()
        df_8 = pd.DataFrame(results, columns=['book_id', 'book_title', 'book_authors', 'book_count'])
        st.write(df_8)

    # 9. "List Publishers with More than 10 Books"

    elif selected_question == questions[8]:
        query_9 = '''SELECT publisher, count(*) as book_count
                    FROM books
                    GROUP BY publisher
                    HAVING count(*) > 10'''
        curr.execute(query_9)
        results = curr.fetchall()
        df_9 = pd.DataFrame(results, columns=['publisher', 'book_count'])
        st.write(df_9)

    # 10. "Find the Average Page Count for Each Category"

    elif selected_question == questions[9]:
        query_10 = '''SELECT categories, AVG(page_count) as average_page_count
                    FROM books
                    WHERE categories IS NOT NULL
                    GROUP BY categories'''
        curr.execute(query_10)
        results = curr.fetchall()
        df_10 = pd.DataFrame(results, columns=['categories', 'average_page_count'])
        st.write(df_10)

    # 11.  "Retrieve Books with More than 3 Authors"

    elif selected_question == questions[10]:
        query_11 = '''SELECT book_id, book_title, book_authors
                    FROM books
                    WHERE TRIM(book_authors) <> '' AND 
                    LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;'''

        curr.execute(query_11)
        results = curr.fetchall()
        df_11 = pd.DataFrame(results, columns=['book_id', 'book_title', 'book_authors'])
        st.write(df_11)

    # 12.  "Books with Ratings Count Greater Than the Average"

    elif selected_question == questions[11]:
        query_12 = '''SELECT book_id, book_title, ratings_count
                    FROM books
                    WHERE ratings_count > (SELECT AVG(ratings_count) FROM books); '''
        curr.execute(query_12)
        results = curr.fetchall()
        df_12 = pd.DataFrame(results, columns=['book_id', 'book_title', 'ratings_count'])
        st.write(df_12)

    ## 13.  "Books with the Same Author Published in the Same Year"

    elif selected_question == questions[12]:
        query_13 = '''SELECT book_id, book_title, book_authors, year
                    FROM books
                    WHERE (book_authors, year) IN (SELECT book_authors, year
                    FROM books
                    GROUP BY book_authors, year
                    HAVING COUNT(*) > 1); '''
        curr.execute(query_13)
        results = curr.fetchall()
        df_13 = pd.DataFrame(results, columns=['book_id', 'book_title', 'book_authors', 'year'])
        st.write(df_13)


    # 14. "Books with a Specific Keyword in the Title"

    elif selected_question == questions[13]:
        keyword = "Programming" 
        query_14 = '''SELECT book_id, book_title 
                    FROM books 
                    WHERE book_title LIKE %s;'''
        curr.execute(query_14, (f'%{keyword}%',))
        results = curr.fetchall()
        df_14 = pd.DataFrame(results, columns=['book_id', 'book_title'])
        st.write(df_14)

    # 15. "Year with the Highest Average Book Price"

    elif selected_question == questions[14]:
        query_15 = '''SELECT year, AVG(amount_listPrice) as Avg_Book_Price
                    FROM books 
                    WHERE amount_listPrice IS NOT NULL
                    GROUP BY year
                    ORDER BY Avg_Book_Price DESC
                    LIMIT 1'''
        curr.execute(query_15)
        results = curr.fetchall()
        df_15 = pd.DataFrame(results, columns=['year', 'Avg_Book_Price'])
        st.write(df_15)

    ## 16. "Count Authors Who Published 3 Consecutive Years"

    elif selected_question == questions[15]:
        query_16 = '''SELECT author, COUNT(DISTINCT year) AS count_years
                  FROM (
                      SELECT book_authors AS author, year 
                      FROM books
                      WHERE year IS NOT NULL
                  ) AS subquery
                  GROUP BY author
                  HAVING COUNT(DISTINCT year) = 3;'''
                  
        curr.execute(query_16)
        results = curr.fetchall()
        df_16 = pd.DataFrame(results, columns=['author','count_authors'])
        st.write(df_16)


    ## 17. "Authors who have published books in the same year but under different publishers."

    elif selected_question == questions[16]:
        query_17 = '''SELECT book_authors, year, COUNT(DISTINCT publisher) as publisher_count
                    FROM books
                    GROUP BY book_authors, year
                    HAVING  COUNT(DISTINCT publisher) > 1'''
                  
        curr.execute(query_17)
        results = curr.fetchall()
        df_17 = pd.DataFrame(results, columns=['book_authors', 'year', 'publisher_count'])
        st.write(df_17)

    # 18. "Average amount_retailPrice of eBooks and physical books."

    elif selected_question == questions[17]:
        query_18 = '''SELECT is_ebook, AVG(amount_retailPrice) as average_retail_price
                    FROM books
                    GROUP BY is_ebook'''
                  
        curr.execute(query_18)
        results = curr.fetchall()
        df_18 = pd.DataFrame(results, columns=['is_ebook', 'average_retail_price'])
        st.write(df_18)

    # 19. "Books that have an averageRating that is more than two standard deviations away from the average rating of all books."

    elif selected_question == questions[18]:
        query_19 = '''WITH RatingStats AS (
                    SELECT AVG(ratings_count) AS avg_rating, STDDEV(ratings_count) AS stddev_rating
                    FROM books),
                    
                    FilteredBooks AS (SELECT * FROM books
                    JOIN RatingStats ON 1=1  # Cross join to access stats
                    WHERE ratings_count > avg_rating + 2 * stddev_rating 
                    OR ratings_count < avg_rating - 2 * stddev_rating)

                    SELECT book_id, book_title, ratings_count, avg_rating, stddev_rating
                    FROM FilteredBooks;'''                  
        curr.execute(query_19)
        results = curr.fetchall()
        df_19 = pd.DataFrame(results, columns=['book_id', 'book_title', 'ratings_count', 'avg_rating', 'stddev_rating'])
        st.write(df_19)

    # 20. "Publisher with the highest average rating among its books, but only for publishers that have published more than 10 books."

    elif selected_question == questions[19]:
        query_20 = '''WITH PublisherRatings AS ( SELECT  publisher,  AVG(ratings_count) AS avg_rating, COUNT(book_id) AS book_count
                    FROM books
                    GROUP BY publisher)
                    SELECT  publisher,  avg_rating,  book_count
                    FROM PublisherRatings
                    WHERE book_count > 10  
                    ORDER BY avg_rating DESC
                    LIMIT 1;'''  
       
        curr.execute(query_20)
        results = curr.fetchall()
        df_20 = pd.DataFrame(results, columns=['publisher', 'avg_rating', 'book_count'])
        st.write(df_20)

























































