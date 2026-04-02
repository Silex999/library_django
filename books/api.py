from typing_extensions import Annotated, List, Optional
from ninja import FilterLookup, NinjaAPI, Query, Schema, FilterSchema, File
from django.shortcuts import get_object_or_404
from .models import Genre, Author, Book, Rating
from datetime import datetime
from django.db.models import Q
from ninja.files import UploadedFile

class BookFilterSchema(FilterSchema):
    title: Annotated[Optional[str], FilterLookup("title__icontains")] = None

    published_year_from: Annotated[Optional[int], FilterLookup("published_year__gte")] = None
    published_year_to: Annotated[Optional[int], FilterLookup("published_year__lte")] = None

    author_name: Annotated[
        Optional[str],
        FilterLookup([
            "author__first_name__icontains",
            "author__last_name__icontains",
            "author__patronymic__icontains",
        ])
    ] = None

    author_id: Annotated[Optional[int], FilterLookup("author__id")] = None

    page_count_from: Annotated[Optional[int], FilterLookup("page_count__gte")] = None
    page_count_to: Annotated[Optional[int], FilterLookup("page_count__lte")] = None

    genre: Annotated[Optional[str], FilterLookup("genre")] = None

api = NinjaAPI()

class GenreIn(Schema):
    name: str

class GenreOut(Schema):
    id: int
    name: str

class AuthorIn(Schema):
    first_name: str
    last_name: str
    patronymic: str

class AuthorOut(Schema):
    id: int
    first_name: str
    last_name: str
    patronymic: str

class BookIn(Schema):
    title: str
    author_id: int
    genre: Genre
    published_year: Optional[int] = None
    rating: Rating
    page_count: Optional[int] = None

class BookOut(Schema):
    id: int
    title: str
    author_id: int
    genre: Genre
    published_year: Optional[int] = None
    rating: Rating
    image: Optional[str] = None
    page_count: Optional[int] = None

@staticmethod
def resolve_image(obj):
    if obj.image:
        return obj.image.url
    return None

@api.post("/authors", response=AuthorOut, tags=["Authors"])
def create_author(request, payload: AuthorIn):
    author = Author.objects.create(**payload.dict())
    return author

@api.get("/authors/{author_id}", response=AuthorOut, tags=["Authors"])
def get_author(request, author_id: int):
    return get_object_or_404(Author, id=author_id)

@api.get("/authors", response=List[AuthorOut], tags=["Authors"])
def list_authors(request):
    return Author.objects.all()

@api.put("/authors/{author_id}", tags=["Authors"])
def update_author(request, author_id: int, payload: AuthorIn):
    author = get_object_or_404(Author, id=author_id)
    for attr, value in payload.dict().items():
        setattr(author, attr, value)
    author.save()
    return {"success": True}

@api.delete("/authors/{author_id}", tags=["Authors"])
def delete_author(request, author_id: int):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return {"success": True}

@api.post("/books", response=BookOut, tags=["Books"])
def create_book(request, payload: BookIn, image: UploadedFile = File(None)):
    book = Book.objects.create(**payload.dict())
    if image:
        book.image = image
    return book

@api.get("/books/{book_id}", response=BookOut, tags=["Books"])
def get_book(request, book_id: int):
    return get_object_or_404(Book, id=book_id)

@api.get("/books", response=List[BookOut], tags=["Books"])
def list_books(request, filters: Query[BookFilterSchema]):
    books = Book.objects.all()
    books = filters.filter(books)
    return books

@api.put("/books/{book_id}", tags=["Books"])
def update_book(request, book_id: int, payload: BookIn, image: UploadedFile = File(None)):
    book = get_object_or_404(Book, id=book_id)
    for attr, value in payload.dict().items():
        setattr(book, attr, value)
    if image:
        if book.image:
            book.image.delete(save=False)
        book.image = image
    book.save()
    return {"success": True}

@api.delete("/books/{book_id}", tags=["Books"])
def delete_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return {"success": True}