from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
from datetime import datetime

# Create an instance of the Flask application
app = Flask(__name__)

# Configure the database URI
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/lucas/OneDrive/Área de Trabalho/MasterSchool/ORM/Projeto ORM/BookAlchemy/data/library.sqlite'

# Initialize the SQLAlchemy instance
db.init_app(app)


# Define a home route
@app.route('/')
def home():
    # Get the sort parameter from the URL (default to sorting by title)
    sort_by = request.args.get('sort', 'title')

    # Get the search parameter from the URL
    search_term = request.args.get('search', '')

    # Query the Book table and join with Author to get author names
    books_query = db.session.query(Book, Author.author_name).join(Author)

    # Apply search filter if a search term is provided
    if search_term:
        # Use the "ilike" operator for case-insensitive search
        title_filter = Book.book_title.ilike(f"%{search_term}%")
        author_filter = Author.author_name.ilike(f"%{search_term}%")
        search_filter = title_filter | author_filter
        books_query = books_query.filter(search_filter)

    # Sort the query based on the selected option
    if sort_by == 'title':
        books_query = books_query.order_by(Book.book_title)
    elif sort_by == 'author':
        books_query = books_query.order_by(Author.author_name)

    # Execute the query
    books = books_query.all()
    authors = Author.query.all()

    # Organize the data in the expected format for Jinja
    formatted_books = [{'title': book.book_title, 'author': author_name, 'type': 'book', 'id': book.book_id} for book, author_name in books]
    formatted_authors = [{'name': author.author_name, 'type': 'author', 'id': author.author_id} for author in authors]

    # Render the home.html template with the formatted_books and formatted_authors data
    return render_template('home.html', books_list=formatted_books, authors_list=formatted_authors)


# Define a route to render the add_author form
@app.route('/add_author', methods=['GET'])
def render_add_author_form():
    return render_template('add_author.html')


# Define a route to handle form submission and add a new author to the database
@app.route('/add_author', methods=['POST'])
def add_author():
    # Get form data
    author_name = request.form['name']
    birthdate_str = request.form['birthdate']
    date_of_death_str = request.form['date_of_death']

    # Convert date strings to Python date objects
    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()

    # Check if date_of_death is provided
    date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

    # Create a new Author instance
    new_author = Author(author_name=author_name, author_birth_date=birthdate, author_date_of_death=date_of_death)

    # Add the new author to the database
    db.session.add(new_author)
    db.session.commit()

    # Display success message on the /add_author page
    success_message = f"Author '{author_name}' has been added successfully!"
    return render_template('add_author.html', success_message=success_message)


# Define a route to render the add_book form
@app.route('/add_book', methods=['GET'])
def render_add_book_form():
    # Get the list of authors from the database
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


# Define a route to handle form submission and add a new book to the database
@app.route('/add_book', methods=['POST'])
def add_book():
    # Get form data
    book_title = request.form['title']
    book_isbn = request.form['isbn']
    book_publication_year_str = request.form['publication_year']
    author_id = request.form['author']

    # Convert date strings to Python date objects
    book_publication_year = datetime.strptime(book_publication_year_str, '%Y-%m-%d').date()

    # Create a new Book instance
    new_book = Book(book_title=book_title, book_isbn=book_isbn, book_publication_year=book_publication_year,
                    author_id=author_id)

    # Add the new book to the database
    db.session.add(new_book)
    db.session.commit()

    # Display success message on the /add_book page
    success_message = f"Book '{book_title}' has been added successfully!"
    return render_template('add_book.html', success_message=success_message)

# Define a route to delete a book by ID
@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    # Retrieve the author from the database
    author = Author.query.get(author_id)

    if author:
        # Delete the author
        db.session.delete(author)
        db.session.commit()

        # Redirect to the home page with a success message
        success_message = f"Author '{author.author_name}' has been deleted successfully!"
        return redirect(url_for('home', success_message=success_message))

    # If the author doesn't exist, redirect to the home page
    return redirect(url_for('home'))

# Define a route to delete a book by ID
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    # Retrieve the book from the database
    book = Book.query.get(book_id)

    if book:
        # Get the author ID before deleting the book
        author_id = book.author_id

        # Delete the book
        db.session.delete(book)
        db.session.commit()

        # Check if the author has no other books, and delete the author if necessary
        if not Book.query.filter_by(author_id=author_id).first():
            author = Author.query.get(author_id)
            db.session.delete(author)
            db.session.commit()

        # Redirect to the home page with a success message
        success_message = f"Book '{book.book_title}' has been deleted successfully!"
        return redirect(url_for('home', success_message=success_message))

    # If the book doesn't exist, redirect to the home page
    return redirect(url_for('home'))

# Create tables before running the application
with app.app_context():
    db.create_all()

# Run the application if executed directly
if __name__ == '__main__':
    app.run(debug=True)
