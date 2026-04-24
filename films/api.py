from datetime import date
from typing import List, Optional
from ninja import Router, Schema, File, UploadedFile
from django.shortcuts import get_object_or_404
from .models import Person, Film, Studio, Media, Review

router = Router(tags=["Films"])

class PersonIn(Schema):
    first_name: str
    last_name: str
    birthdate: Optional[date] = None

class PersonOut(Schema):
    id: int
    first_name: str
    last_name: str
    birthdate: Optional[date] = None


class StudioIn(Schema):
    name: str

class StudioOut(Schema):
    id: int
    name: str


class MediaIn(Schema):
    film_id: int
    media_type: str

class MediaOut(Schema):
    id: int
    film_id: int
    media_type: str
    file: Optional[str] = None


class FilmIn(Schema):
    title: str
    release_date: Optional[date] = None
    studio_id: Optional[int] = None
    actors_id: List[int] = []
    directors_id: List[int] = []
    producers_id: List[int] = []

class FilmOut(Schema):
    id: int
    title: str
    release_date: Optional[date] = None
    studio: Optional[StudioOut] = None
    actors: List[PersonOut]
    directors: List[PersonOut]
    producers: List[PersonOut]
    media: List[MediaOut]

class ReviewIn(Schema):
    film_id: int
    author_id: int
    text: str

class ReviewOut(Schema):
    id: int
    film_id: int
    author: PersonOut
    text: str

@router.post("/persons", tags=["Persons"])
def create_person(request, payload: PersonIn):
    person = Person.objects.create(**payload.dict())
    return {"id": person.id}

@router.get("/persons", response=List[PersonOut], tags=["Persons"])
def list_persons(request):
    return Person.objects.all()

@router.get("/persons/{person_id}", response=PersonOut, tags=["Persons"])
def get_person(request, person_id: int):
    return get_object_or_404(Person, id=person_id)

@router.post("/studios", tags=["Studios"])
def create_studio(request, payload: StudioIn):
    studio = Studio.objects.create(**payload.dict())
    return {"id": studio.id}

@router.get("/studios", response=List[StudioOut], tags=["Studios"])
def list_studios(request):
    return Studio.objects.all()

@router.post("/films", tags=["Films"])
def create_film(request, payload: FilmIn):
    data = payload.dict()
    actors_id = data.pop("actors_id")
    directors_id = data.pop("directors_id")
    producers_id = data.pop("producers_id")

    film = Film.objects.create(**data)
    film.actors.set(actors_id)
    film.directors.set(directors_id)
    film.producers.set(producers_id)

    return {"id": film.id}

@router.get("/films", response=List[FilmOut], tags=["Films"])
def list_films(request):
    return Film.objects.prefetch_related(
        "actors", "directors", "producers", "media"
    ).select_related("studio").all()

@router.get("/films/{film_id}", response=FilmOut, tags=["Films"])
def get_film(request, film_id: int):
    return get_object_or_404(
        Film.objects.prefetch_related(
            "actors", "directors", "producers", "media"
        ).select_related("studio"),
        id=film_id
    )

@router.post("/media", tags=["Media"])
def create_media(request, payload: MediaIn, file: File[UploadedFile] = None):
    media = Media.objects.create(**payload.dict())
    if file:
        media.file.save(file.name, file)
    return {"id": media.id}

@router.get("/media", response=List[MediaOut], tags=["Media"])
def list_media(request):
    return Media.objects.all()

@router.post("/reviews", response=ReviewOut, tags=["Reviews"])
def create_review(request, payload: ReviewIn):
    review = Review.objects.create(
        film_id=payload.film_id,
        author_id=payload.author_id,
        text=payload.text
    )
    return review

@router.get("/reviews", response=List[ReviewOut], tags=["Reviews"])
def list_reviews(request):
    return Review.objects.select_related("author").all()

@router.get("/reviews/{review_id}", response=ReviewOut, tags=["Reviews"])
def get_review(request, review_id: int):
    return get_object_or_404(Review.objects.select_related("author"), id=review_id)