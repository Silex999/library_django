from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Studio(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField(null=True, blank=True)
    studio = models.ForeignKey(Studio, on_delete=models.SET_NULL, null=True, blank=True)
    actors = models.ManyToManyField(Person, related_name="actor_films", blank=True)
    directors = models.ManyToManyField(Person, related_name="director_films", blank=True)
    producers = models.ManyToManyField(Person, related_name="producer_films", blank=True)

    def __str__(self):
        return self.title


class Media(models.Model):
    class MediaType(models.TextChoices):
        TRAILER = "trailer", "Трейлер"
        FILM = "film", "Фильм"
        IMAGE = "image", "Изображение"

    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="films/")
    media_type = models.CharField(max_length=50, choices=MediaType.choices)

    def __str__(self):
        return f"{self.media_type} — {self.film.title}"


class Review(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()

    def __str__(self):
        return f"Рецензия от {self.author} на {self.film}"