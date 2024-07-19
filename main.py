from flask import Flask, request, jsonify
from logging_config import request_logger, books_logger
from logging import getLevelName
import time

app = Flask(__name__)
app.json.sort_keys = False

books = []
next_id = 1
valid_genres = {'SCI_FI', 'NOVEL', 'HISTORY', 'MANGA', 'ROMANCE', 'PROFESSIONAL'}
request_counter = 1
convert_seconds_to_ms = 1000

def log_request_start(resource_name, http_verb_name):
    global request_counter
    request_logger.info(f"Incoming request | #{request_counter} | resource: {resource_name} | HTTP Verb {http_verb_name.upper()}", extra={'request_number': request_counter})

def log_request_end(duration_in_ms):
    global request_counter
    request_logger.debug(f"request #{request_counter} duration: {duration_in_ms}ms", extra={'request_number': request_counter})
    request_counter += 1


@app.route('/books/health', methods=['GET'])
def health():
    start_time = time.time()
    log_request_start('/books/health', 'GET')
    response = "OK", 200
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response


@app.route('/book', methods=['POST'])
def create_book():
    global next_id
    global books

    start_time = time.time()
    log_request_start('/book', 'POST')

    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')
    price = data.get('price')
    genres = data.get('genres')

    # Check if book title already exists (case-insensitive)
    for book in books:
        if book['title'].lower() == title.lower():
            error_message = f"Error: Book with the title [{title}] already exists in the system"
            books_logger.error(error_message, extra={'request_number': request_counter})
            response = jsonify(errorMessage=error_message), 409
            log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
            return response

    # Check year range
    if year < 1940 or year > 2100:
        error_message = f"Error: Can't create new Book that its year [{year}] is not in the accepted range [1940 -> 2100]"
        books_logger.error(error_message, extra={'request_number': request_counter})
        response = jsonify(errorMessage=error_message), 409
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    # Check if price is positive
    if price < 0:
        error_message = "Error: Can't create new Book with negative price"
        books_logger.error(error_message, extra={'request_number': request_counter})
        response = jsonify(errorMessage=error_message), 409
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    # Create new book
    new_book = {
        'id': next_id,
        'title': title,
        'author': author,
        'year': year,
        'price': price,
        'genres': genres
    }

    books_logger.info(f"Creating new Book with Title [{title}]", extra={'request_number': request_counter})
    books_logger.debug(f"Currently there are {len(books)} Books in the system. New Book will be assigned with id {next_id}"
                       , extra={'request_number': request_counter})

    books.append(new_book)
    next_id += 1

    response = jsonify(result=new_book['id']), 200
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response


def filter_books_list(author, price_bigger_than, price_less_than, year_bigger_than, year_less_than, genres):

    books_after_filter = list(books)

    if author is not None:
        for book in books_after_filter:
            if book['author'].lower() != author.lower():
                books_after_filter.remove(book)

    if price_bigger_than is not None:
        for book in books_after_filter:
            if book['price'] < price_bigger_than:
                books_after_filter.remove(book)

    if price_less_than is not None:
        for book in books_after_filter:
            if book['price'] > price_less_than:
                books_after_filter.remove(book)

    if year_bigger_than is not None:
        for book in books_after_filter:
            if book['year'] < year_bigger_than:
                books_after_filter.remove(book)

    if year_less_than is not None:
        for book in books_after_filter:
            if book['price'] > year_less_than:
                books_after_filter.remove(book)

    if genres is not None:
        genres_list = genres.split(',')
        # if any() return false, the book doesn't have a genre from genres_list.
        for book in books_after_filter:
            if not any(genre in book['genres'] for genre in genres_list):
                books_after_filter.remove(book)

    return books_after_filter


@app.route('/books/total', methods=['GET'])
def get_total_books_number():

    start_time = time.time()
    log_request_start('/books/total', 'GET')

    author = request.args.get('author')
    price_bigger_than = request.args.get('price-bigger-than', type=int)
    price_less_than = request.args.get('price-less-than', type=int)
    year_bigger_than = request.args.get('year-bigger-than', type=int)
    year_less_than = request.args.get('year-less-than', type=int)
    genres = request.args.get('genres')

    if genres is not None:
        genres_list = genres.split(',')
        for genre in genres_list:
            if genre not in valid_genres:
                error_message = f"Invalid genre value: {genre}"
                books_logger.error(error_message, extra={'request_number': request_counter})
                response = jsonify(errorMessage=error_message), 400
                log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
                return response

    filtered_books_list = filter_books_list(author, price_bigger_than, price_less_than, year_bigger_than, year_less_than, genres)
    len_of_filtered_books = len(filtered_books_list)
    response = jsonify(result=len_of_filtered_books), 200

    books_logger.info(f"Total Books found for requested filters is {len_of_filtered_books}", extra={'request_number': request_counter})
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response


@app.route('/books', methods=['GET'])
def get_books():

    start_time = time.time()
    log_request_start('/books', 'GET')

    author = request.args.get('author')
    price_bigger_than = request.args.get('price-bigger-than', type=int)
    price_less_than = request.args.get('price-less-than', type=int)
    year_bigger_than = request.args.get('year-bigger-than', type=int)
    year_less_than = request.args.get('year-less-than', type=int)
    genres = request.args.get('genres')

    if genres is not None:
        genres_list = genres.split(',')
        for genre in genres_list:
            if genre not in valid_genres:
                error_message = f"Invalid genre value: {genre}"
                books_logger.error(error_message, extra={'request_number': request_counter})
                response = jsonify(errorMessage=error_message), 400
                log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
                return response

    filtered_books_list = filter_books_list(author, price_bigger_than, price_less_than, year_bigger_than, year_less_than, genres)
    filtered_books_list.sort(key=lambda book: book['title'].lower())
    response = jsonify(result=filtered_books_list), 200

    len_of_filtered_books = len(filtered_books_list)
    books_logger.info(f"Total Books found for requested filters is {len_of_filtered_books}", extra={'request_number': request_counter})
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response


@app.route('/book', methods=['GET'])
def get_book():

    start_time = time.time()
    log_request_start('/book', 'GET')

    book_id = request.args.get('id', type=int)

    for book in books:
        if book['id'] == book_id:
            response = jsonify(result=book), 200
            log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
            return response

    error_message = f"Error: no such Book with id {book_id}"
    books_logger.error(error_message, extra={'request_number': request_counter})
    response = jsonify(errorMessage=error_message), 404

    books_logger.debug(f"Fetching book id {book_id} details", extra={'request_number': request_counter})
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response


@app.route('/book', methods=['PUT'])
def update_book():
    global books

    start_time = time.time()
    log_request_start('/book', 'PUT')

    book_id = request.args.get('id', type=int)
    new_price = request.args.get('price', type=int)

    if new_price <= 0:
        error_message = f"Error: price update for book {book_id} must be a positive integer"
        books_logger.error(error_message, extra={'request_number': request_counter})
        response = jsonify(errorMessage=error_message), 409
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    for book in books:
        if book['id'] == book_id:
            old_price = book['price']
            book['price'] = new_price
            response = jsonify(result=old_price), 200
            books_logger.info(f"Update Book id [{book_id}] price to {new_price}", extra={'request_number': request_counter})
            books_logger.debug(f"Book [{book['title']}] price change: {old_price} --> {new_price}", extra={'request_number': request_counter})
            log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
            return response

    error_message = f"Error: no such Book with id {book_id}"
    books_logger.error(error_message, extra={'request_number': request_counter})
    response = jsonify(errorMessage=error_message), 404
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response


@app.route('/book', methods=['DELETE'])
def delete_book():
    global books

    start_time = time.time()
    log_request_start('/book', 'DELETE')

    book_id = request.args.get('id', type=int)
    book = next((book for book in books if book['id'] == book_id), None)

    if book is None:
        error_message = f"Error: no such Book with id {book_id}"
        books_logger.error(error_message, extra={'request_number': request_counter})
        response = jsonify(errorMessage=error_message), 404
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    books.remove(book)

    response = jsonify(result=len(books)), 200

    books_logger.info(f"Removing book [{book['title']}]", extra={'request_number': request_counter})
    books_logger.debug(f"After removing book [{book['title']}] id: [{book_id}] there are {len(books)} books in the system"
                       , extra={'request_number': request_counter})
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response

@app.route('/logs/level', methods=['GET'])
def get_log_level():
    start_time = time.time()
    log_request_start('/logs/level', 'GET')

    logger_name = request.args.get('logger-name')
    if logger_name == 'request-logger':
        level = getLevelName(request_logger.getEffectiveLevel())
    elif logger_name == 'books-logger':
        level = getLevelName(books_logger.getEffectiveLevel())
    else:
        response = jsonify(errorMessage="Invalid logger name"), 400
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    response = jsonify(result=level), 200
    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return response

@app.route('/logs/level', methods=['PUT'])
def set_log_level():
    start_time = time.time()
    log_request_start('/logs/level', 'PUT')

    logger_name = request.args.get('logger-name')
    logger_level = request.args.get('logger-level').upper()
    if logger_level not in ['ERROR', 'INFO', 'DEBUG']:
        response = "Invalid logger level"
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    if logger_name == 'request-logger':
        request_logger.setLevel(logger_level)
    elif logger_name == 'books-logger':
        books_logger.setLevel(logger_level)
    else:
        response = "Invalid logger name"
        log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
        return response

    log_request_end(int((time.time() - start_time) * convert_seconds_to_ms))
    return logger_level


app.run(port=8574)
