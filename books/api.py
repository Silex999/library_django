from typing import List, Optional
from typing_extensions import Annotated
from ninja import FilterLookup, NinjaAPI, Query, Schema, FilterSchema, File
from ninja import Router
from ninja.files import UploadedFile
from ninja.pagination import LimitOffsetPagination, paginate, PageNumberPagination, CursorPagination
from django.shortcuts import get_object_or_404
from .models import Genre, Author, Book, Rating

router = Router()

api = NinjaAPI()
api.add_router("", router)

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
    image: str = None
    page_count: Optional[int] = None

    @staticmethod
    def resolve_image(obj):
        if obj.image:
            return obj.image.url
        return None

@router.post("/authors", response=AuthorOut, tags=["Authors"])
def create_author(request, payload: AuthorIn):
    return Author.objects.create(**payload.dict())

@router.get("/authors/{author_id}", response=AuthorOut, tags=["Authors"])
def get_author(request, author_id: int):
    return get_object_or_404(Author, id=author_id)

@router.get("/authors", response=List[AuthorOut], tags=["Authors"])
def list_authors(request):
    return Author.objects.all()

@router.put("/authors/{author_id}", tags=["Authors"])
def update_author(request, author_id: int, payload: AuthorIn):
    author = get_object_or_404(Author, id=author_id)
    for attr, value in payload.dict().items():
        setattr(author, attr, value)
    author.save()
    return {"success": True}

@router.delete("/authors/{author_id}", tags=["Authors"])
def delete_author(request, author_id: int):
    get_object_or_404(Author, id=author_id).delete()
    return {"success": True}

@router.post("/books", response=BookOut, tags=["Books"])
def create_book(request, payload: BookIn, image: File[UploadedFile] = None):
    book = Book.objects.create(**payload.dict())
    if image:
        book.image.save(image.name, image)
    return book

@router.get("/books/{book_id}", response=BookOut, tags=["Books"])
def get_book(request, book_id: int):
    return get_object_or_404(Book, id=book_id)

@router.get("/books", response=List[BookOut], tags=["Books"])
@paginate()
def list_books(request, filters: Query[BookFilterSchema]):
    return filters.filter(Book.objects.all())

@router.get("/booksOP", response=List[BookOut], auth=None)
@paginate(LimitOffsetPagination)
def list_books_op(request, filters: BookFilterSchema = Query(...)):
    return filters.filter(Book.objects.all())

@router.get("/booksPNP", response=List[BookOut], auth=None)
@paginate(PageNumberPagination)
def list_books_pnp(request, filters: BookFilterSchema = Query(...)):
    return filters.filter(Book.objects.all())

@router.get("/booksCurs", response=List[BookOut])
@paginate(CursorPagination)
def list_books_curs(request, filters: BookFilterSchema = Query(...)):
    return filters.filter(Book.objects.all())

@router.put("/books/{book_id}", tags=["Books"])
def update_book(request, book_id: int, payload: BookIn):
    book = get_object_or_404(Book, id=book_id)
    for attr, value in payload.dict().items():
        setattr(book, attr, value)
    book.save()
    return {"success": True}

@router.delete("/books/{book_id}", tags=["Books"])
def delete_book(request, book_id: int):
    get_object_or_404(Book, id=book_id).delete()
    return {"success": True}