# coding: utf-8

from django.db import models
from profiles.models import Profile, Place
from categories.models import Category
from datetime import datetime
from django.core.validators import validate_comma_separated_integer_list
from django.core.files import File
# Create your models here.

class Notice(models.Model):
    # Aviso de publicacion de un nuevo producto o servicio
    date = models.DateField(default=datetime.now)
    profile = models.ForeignKey(Profile, default="")
    category = models.ForeignKey(Category, default="")
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    # si recibe u ofrece dinero a cambio
    money = models.BooleanField(default=True)
    # oferta preferente para el intercambio
    offer = models.ForeignKey("self", blank=True, null=True)
    # KIND: 1 --> propio | 2 --> deseado
    kind = models.IntegerField(default=1)
    visibility = models.BooleanField(default=True)
    # urgente un tiempo 24 horas
    urgency = models.BooleanField(default=False)
    # la categoria que se envia es la subcategoria, en caso de que no se haya seleccionado se envia la macro

    def create(profile, category, title, description, kind, urgency):
        notice = Notice(profile=profile, category=category, title=title, description=description, kind=kind, urgency=urgency)
        notice.save()
        return notice

    @staticmethod
    def getNotice(profile, kind):
        return Notice.objects.filter(profile=profile, kind=kind)

    # para unir cosnultas se usa |

    def searchTitle(title, city):
        return CityNotice.searchNotices(city).filter(notice__title__icontains=title).order_by('notice__date')

    def searchCategory(title, category, city):
        return CityNotice.searchNotices(city).filter(notice__title__icontains=title, notice__category=category).order_by('notice__date')

# clase debil


class CityNotice(models.Model):
    # ciudades donde se vera el aviso
    city = models.ForeignKey(Place)
    notice = models.ForeignKey(Notice)

    def create(city, notice):
        cityNotice = CityNotice(city=city, notice=notice)
        cityNotice.save()
        return cityNotice

    def __str__(self):
        return '%s %s' % (self.city, self.notice)

    def searchNotices(city):
        return CityNotice.objects.filter(city=city).order_by('date')

    def searchCities(notice):
        return CityNotice.objects.filter(notice=notice).order_by('date')


class CategoryTrade(models.Model):
    # categorias por las que se quiere intercambiar el bien o servicio, las propias del usuario. 
    category = models.ForeignKey(Category)
    notice = models.ForeignKey(Notice)

    def create(category, notice):
        category = CategoryTrade(category=category, notice=notice)
        category.save()
        return category


class Product(models.Model):
    notice = models.OneToOneField(Notice, on_delete=models.CASCADE)
    # quantity = models.PositiveIntegerField()
    STATE = (
        ('N', 'Nuevo'),
        ('U', 'Usado'),
        ('E', 'Por Encargo'),
        # bring back
        ('B', 'Restaurado'),
        ('R', 'Reparado'),
        ('M', 'Mejorado'),
        ('C', 'Cualquiera'),
    )
    state = models.CharField(max_length=1, choices=STATE, default='N')
    # tamaño - dimensiones
    DELIVERY = (
        ('E', 'Yo mismo lo entrego'),
        ('C', 'Convenio'),
        ('R', 'Redzza service'),
    )
    delivery = models.CharField(max_length=1, choices=DELIVERY, default='C')
    # size = models.PositiveIntegerField(blank=True)
    # measure = models.CharField(validators=[validate_comma_separated_integer_list], max_length=20, blank=True)
    # a pedido
    # order = models.BooleanField(default=False)

    def __str__(self):
        return self.notice

    def create(notice, quantity):
        product = Product(notice=notice, quantity=quantity)
        product.save()
        return product


class Color(models.Model):
    # hexadecimal -> #111111
    hexa = models.CharField(max_length=7)
    product = models.ForeignKey(Product, default="")

    def __str__(self):
        return self.name

    def create(hexa, product):
        color = Color(hexa=hexa, product=product)
        color.save()
        return color


class Service(models.Model):
    notice = models.OneToOneField(Notice, on_delete=models.CASCADE)
    # horas semanales
    time = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return self.notice

    def create(notice, time):
        service = Service(notice=notice, time=time)
        service.save()
        return service

# https://openwebinars.net/blog/tutorial-django-modelos-bbdd-donde-guardar-informacion/


class Image(models.Model):
    notice = models.ForeignKey(Notice)
    image = models.ImageField(upload_to='productos')

    def create(notice, pathimage):
        image = Image(notice=notice)
        # se abre el archivo local en binario
        f = open(pathimage, 'rb')
        # se guarda el archivo con extension
        image.image.save(notice.title + '.jpg', File(f))
        return image

    def createGoogle(notice, pathimage):
        image = Image(notice=notice, image=pathimage)
        image.save()
        return image


class Video(models.Model):
    # archivo o url
    notice = models.ForeignKey(Notice)
    video = models.FileField(upload_to='videos')
    url = models.CharField(max_length=100, default="")

    def create(notice, video):
        video = Video(notice=notice, video=video)
        video.save()
        return video

    def create(notice, url):
        video = Video(notice=notice, url=url)
        video.save()
        return video


class Commentary(models.Model):
    commentary = models.CharField(max_length=500)
    notice = models.ForeignKey(Notice)
    profile = models.ForeignKey(Profile)

    def create(commentary, notice, profile):
        commentary = Commentary(commentary=commentary, notice=notice, profile=profile)
        commentary.save()
        return commentary
