from django.db import models

class Genre(models.TextChoices):
    FANTASY = "Fantasy", ("Фантастика")
    DETECTIVE = "Detective", ("Детектива")
    ROMANTIC = "Romantic", ("Романтика")
    PROSE = "Prose", ("Проза")
    DRAMATURGY = "Dramaturgy", ("Драматургия")
    MISTYC = "Mysticisme", ("Мистика")

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Rating(models.TextChoices):
    PERFECT = "5", ("Отлично")
    GOOD = "4", ("Хорошо")
    NORMAL = "3", ("Нормально")
    BAD = "2", ("Плохо")
    TERRIBLE = "1", ("Ужасно")

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.CharField(max_length=10, choices=Genre.choices, null=True, blank=True)
    published_year = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='books/', verbose_name='Обложка', null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    rating = models.CharField(max_length=2, choices=Rating.choices, null=True, blank=True)
 
    def __str__(self):
        return self.title