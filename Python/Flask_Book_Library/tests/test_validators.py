import pytest

from project import app
from project.books.models import Book
from project.customers.models import Customer
from project.loans.models import Loan
from project.validators import validate_text, validate_year, validate_age, validate_book_type


XSS_PAYLOADS = [
    '<script>alert(1)</script>',
    '<img src=x onerror=alert(document.cookie)>',
    '<svg/onload=alert(1)>',
    '"><script>alert(1)</script>',
    'javascript:alert(1)//',
    '<a href="javascript:alert(1)">x</a>',
    'Harry Potter<b>',
    'Tom & Jerry; DROP TABLE books',
]


# --- validate_text ---------------------------------------------------------

@pytest.mark.parametrize('value', [
    'Harry Potter',
    'Pan Tadeusz',
    'Łódź',
    'Gżegżółka Źdźbło',
    "O'Reilly",
    'Dr. Jekyll & Mr. Hyde',
    'Catch-22',
    'Who? What! (2nd ed.): Part 1',
    'a' * 64,
])
def test_validate_text_accepts_valid_input(value):
    assert validate_text('name', value) == value


def test_validate_text_strips_whitespace():
    assert validate_text('name', '  Dune  ') == 'Dune'


@pytest.mark.parametrize('value', XSS_PAYLOADS)
def test_validate_text_rejects_xss_payloads(value):
    with pytest.raises(ValueError, match='forbidden characters'):
        validate_text('name', value)


@pytest.mark.parametrize('value', ['', '   ', 'a' * 65, None, 123, ['Dune']])
def test_validate_text_rejects_empty_too_long_or_wrong_type(value):
    with pytest.raises(ValueError):
        validate_text('name', value)


# --- numeric and choice validators -----------------------------------------

@pytest.mark.parametrize('value, expected', [(1999, 1999), ('2001', 2001), (1, 1)])
def test_validate_year_accepts_valid_input(value, expected):
    assert validate_year('year_published', value) == expected


@pytest.mark.parametrize('value', [0, -5, 99999, '20x0', '<script>', 19.5, True, None])
def test_validate_year_rejects_invalid_input(value):
    with pytest.raises(ValueError):
        validate_year('year_published', value)


@pytest.mark.parametrize('value, expected', [(18, 18), ('42', 42), (120, 120)])
def test_validate_age_accepts_valid_input(value, expected):
    assert validate_age('age', value) == expected


@pytest.mark.parametrize('value', [0, 121, -1, 'abc', '<b>1</b>', None])
def test_validate_age_rejects_invalid_input(value):
    with pytest.raises(ValueError):
        validate_age('age', value)


@pytest.mark.parametrize('value', ['2days', '5days', '10days'])
def test_validate_book_type_accepts_valid_input(value):
    assert validate_book_type('book_type', value) == value


@pytest.mark.parametrize('value', ['1day', '', '<script>alert(1)</script>', None])
def test_validate_book_type_rejects_invalid_input(value):
    with pytest.raises(ValueError):
        validate_book_type('book_type', value)


# --- models ----------------------------------------------------------------

def test_book_created_with_valid_data():
    book = Book(name='Pan Tadeusz', author='Adam Mickiewicz', year_published='1834', book_type='5days')
    assert book.name == 'Pan Tadeusz'
    assert book.year_published == 1834


@pytest.mark.parametrize('field', ['name', 'author'])
@pytest.mark.parametrize('payload', XSS_PAYLOADS)
def test_book_rejects_xss_on_create(field, payload):
    data = {'name': 'Dune', 'author': 'Frank Herbert', 'year_published': 1965, 'book_type': '2days'}
    data[field] = payload
    with pytest.raises(ValueError):
        Book(**data)


@pytest.mark.parametrize('payload', XSS_PAYLOADS)
def test_book_rejects_xss_on_edit(payload):
    book = Book(name='Dune', author='Frank Herbert', year_published=1965, book_type='2days')
    with pytest.raises(ValueError):
        book.name = payload
    assert book.name == 'Dune'


def test_customer_created_with_valid_data():
    customer = Customer(name='Jan Kowalski', city='Kraków', age='30')
    assert customer.city == 'Kraków'
    assert customer.age == 30


@pytest.mark.parametrize('field', ['name', 'city'])
@pytest.mark.parametrize('payload', XSS_PAYLOADS)
def test_customer_rejects_xss(field, payload):
    data = {'name': 'Jan Kowalski', 'city': 'Warszawa', 'age': 30}
    data[field] = payload
    with pytest.raises(ValueError):
        Customer(**data)


@pytest.mark.parametrize('payload', XSS_PAYLOADS)
def test_loan_rejects_xss_in_customer_name(payload):
    with pytest.raises(ValueError):
        Loan(customer_name=payload, book_name='Dune', loan_date=None, return_date=None,
             original_author='Frank Herbert', original_year_published=1965, original_book_type='2days')


# --- endpoints (only rejected requests, so nothing is written to the database) ---

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize('payload', XSS_PAYLOADS)
def test_create_book_endpoint_returns_400_for_xss(client, payload):
    response = client.post('/books/create', json={
        'name': payload, 'author': 'Frank Herbert', 'year_published': 1965, 'book_type': '2days'
    })
    assert response.status_code == 400


@pytest.mark.parametrize('payload', XSS_PAYLOADS)
def test_create_customer_endpoint_returns_400_for_xss(client, payload):
    response = client.post('/customers/create', data={'name': 'Jan Kowalski', 'city': payload, 'age': '30'})
    assert response.status_code == 400
