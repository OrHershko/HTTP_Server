import logging
import os

# Ensure the logs folder exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Loggers set up
request_logger = logging.getLogger('request-logger')
request_logger.setLevel(logging.INFO)
books_logger = logging.getLogger('books-logger')
books_logger.setLevel(logging.INFO)

# Create file handlers
request_file_handler = logging.FileHandler('logs/requests.log')
books_file_handler = logging.FileHandler('logs/books.log')

# Create console handlers
console_handler = logging.StreamHandler()

# create and set formatter for logs
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s | request #%(request_number)s', datefmt='%d-%m-%Y %H:%M:%S')
request_file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
books_file_handler.setFormatter(formatter)

# Add handlers to request-logger
request_logger.addHandler(request_file_handler)
request_logger.addHandler(console_handler)

# Add handler to books-logger
books_logger.addHandler(books_file_handler)
