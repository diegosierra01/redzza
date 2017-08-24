from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import list_route, detail_route
from rest_framework.authtoken.models import Token
from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from categories.models import WantedCategory, SuggestedCategory
from tags.models import TagProfile
from things.models import Notice, Image
from .models import Profile, Place, Follow, Icon
from .serializers import ProfileSerializer, UserSerializer, PlaceSerializer, FollowSerializer
from string import ascii_lowercase, digits
from random import choice
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_expiring_authtoken.models import ExpiringToken
from django.shortcuts import get_object_or_404
from rest_framework_expiring_authtoken.settings import token_settings
from django.utils import timezone
from django.core import serializers
from redzza.settings import MEDIA_ROOT
import json


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().filter(is_staff=False)
    serializer_class = UserSerializer

    # Obtencion de informacion de un usuario
    @detail_route(methods=['get'])
    def getData(self, request, pk=None):
        try:
            user = getUser(pk)
            context = {}
            context['user'] = json.loads(serializers.serialize('json', [user], fields=('username', 'first_name', 'last_name', 'email', 'is_active', 'last_login', 'date_joined')))
            profile = getProfile(user)
            context['profile'] = json.loads(serializers.serialize('json', [profile]))
            context['profile'][0]['fields']['location_name'] = str(profile.location)
            context['duration'] = getDurationUser(user)
            context['numberFollowers'] = getNumberFollowersUser(user)
            haveCategories = getHaveCategoriesUser(user)
            context['haveCategories'] = json.loads(serializers.serialize('json', haveCategories))
            for i, category in enumerate(context['haveCategories']):
                context['haveCategories'][i]['fields']['name'] = str(haveCategories[i])
            searchCategories = getSearchCategoriesUser(user)
            context['searchCategories'] = json.loads(serializers.serialize('json', searchCategories))
            for i, category in enumerate(context['searchCategories']):
                context['searchCategories'][i]['fields']['name'] = str(searchCategories[i])
            context['tags'] = json.loads(serializers.serialize('json', getTagsUser(user)))
            return Response({'success': True, 'data': context})
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Obtencion de publicacion de un usuario
    # id - imagen - titulo - kind
    @detail_route(methods=['get'])
    def getNotices(self, request, pk=None):
        try:
            user = getUser(pk)
            context = []
            for i, notice in enumerate(getNoticesHaveUser(user)):
                image = getImageNotice(notice)
                if len(image) > 0:
                    context.append({'id': notice.id, 'title': notice.title, 'image': MEDIA_ROOT + '/' + image[0]['image'], 'kind': "%s" % ("i_have" if notice.kind == 1 else "i_search")})
                else:
                    context.append({'id': notice.id, 'title': notice.title, 'image': MEDIA_ROOT + '/' + 'no_image.jpg', 'kind': "%s" % ("i_have" if notice.kind == 1 else "i_search")})
            for i, notice in enumerate(getNoticesSearchUser(user)):
                image = getImageNotice(notice)
                if len(image) > 0:
                    context.append({'id': notice.id, 'title': notice.title, 'image': MEDIA_ROOT + '/' + image[0]['image'], 'kind': "%s" % ("i_have" if notice.kind == 1 else "i_search")})
                else:
                    context.append({'id': notice.id, 'title': notice.title, 'image': MEDIA_ROOT + '/' + 'no_image.jpg', 'kind': "%s" % ("i_have" if notice.kind == 1 else "i_search")})
            # context['noticesSearch'] = json.loads(serializers.serialize('json', getNoticesSearchUser(user)))
            return Response({'success': True, 'data': context})
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class ApiServicesViewSet(viewsets.ViewSet):

    # Validacion del correo que se intenta registrar
    @list_route(methods=['post'], permission_classes=[AllowAny])
    def validateEmail(self, request):
        try:
            email = request.data.get('email', None)
            if email:
                return Response({'success': True, 'exists': Profile.searchEmail(email), 'data': email})
            else:
                return Response({'success': False, 'err': 'Incomplete data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Creacion de un usuario
    @list_route(methods=['post'], permission_classes=[AllowAny])
    def createUser(self, request):
        try:
            email = request.data.get('email', None)
            username = generateRandomUsername(request.data.get('first_name', None))
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)
            password = request.data.get('password', None)
            place = request.data.get('place', None)
            i_search = request.data.get('i_search', None)
            i_have = request.data.get('i_have', None)
            suggesting = request.data.get('suggesting', None)

            if email and username and first_name and last_name and password and place and i_search and i_have:
                if Profile.searchEmail(email) is False:
                    if validateStructureEmail(email):
                        user, created = Profile.createUser(email, username, first_name, last_name, password)
                        if created:
                            profile = Profile.create(place, user)
                            # i_have(Ofrezco) --> 1 ; i_search(Busco) --> 2
                            for element in i_have:
                                WantedCategory.create(element['pk'], profile, 1)
                            for element in i_search:
                                WantedCategory.create(element['pk'], profile, 2)
                            if suggesting:
                                SuggestedCategory.create(suggesting, profile)
                            login(request, user)
                            token = Token.objects.create(user=user)
                            userSerialized = json.loads(serializers.serialize('json', [user], fields=('username', 'first_name', 'last_name', 'email', 'is_active', 'last_login', 'date_joined')))
                            complete_signup(request._request, user, allauth_settings.EMAIL_VERIFICATION, None)
                            userSerialized[0]['fields']['is_verified'] = EmailAddress.objects.get(user=user).verified
                            return Response({'success': True, 'msg': 'user-created', 'token': token.key, 'user': userSerialized}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({'success': False, 'err': 'User not created'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    else:
                        return Response({'success': False, 'err': 'Invalid Email'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                else:
                    return Response({'success': False, 'err': 'email-exists'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                return Response({'success': False, 'err': 'Incomplete data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Login por correo electronico o usuario y contraseña
    @list_route(methods=['post'], permission_classes=[AllowAny])
    def loginUser(self, request):
        try:
            user = request.data.get('user', None)
            password = request.data.get('password', None)
            if validateStructureEmail(user):
                userEmail = getUserEmail(user)
                if userEmail is not None:
                    user = userEmail.username
            userAuthenticate = authenticate(request, username=user, password=password)
            if userAuthenticate is not None:
                login(request, userAuthenticate)
                token = getToken(userAuthenticate)
                timeToken = getTimeToken(token)
                userSerialized = json.loads(serializers.serialize('json', [userAuthenticate], fields=('username', 'first_name', 'last_name', 'email', 'is_active', 'last_login', 'date_joined')))
                userSerialized[0]['fields']['is_verified'] = EmailAddress.objects.get(user=userAuthenticate).verified
                if userAuthenticate.is_staff:
                    return Response({'success': True, 'msg': 'user-admin', 'user': userSerialized, 'token': token.key, 'timeToken': timeToken})
                else:
                    return Response({'success': True, 'msg': 'user-normal', 'user': userSerialized, 'token': token.key, 'timeToken': timeToken})
            else:
                return Response({'success': False, 'err': 'invalid-login'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Edicion de informacion del usuario
    @list_route(methods=['put'])
    def updateUser(self, request):
        try:
            user = request.user
            profile = getProfile(user)
            username = request.data.get('username', None)
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)
            email = request.data.get('email', None)
            avatar = request.data.get('avatar', None)
            icono = request.data.get('icono', None)
            birth_date = request.data.get('birth_date', None)
            gender = request.data.get('gender', None)
            phone = request.data.get('phone', None)
            biography = request.data.get('biography', None)
            location = request.data.get('location', None)
            company = request.data.get('company', None)
            profession = request.data.get('profession', None)
            address = request.data.get('address', None)
            avialability = request.data.get('avialability', None)
            i_search = request.data.get('i_search', None)
            i_have = request.data.get('i_have', None)
            tags = request.data.get('tags', None)

            if username:
                if Profile.searchUsername(username) is False:
                    user.username = username
                    user.save()
                    return Response({'success': True, 'msg': 'username-update'})
                else:
                    return Response({'success': False, 'err': 'username-exists'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            elif first_name:
                user.first_name = first_name
                user.save()
                return Response({'success': True, 'msg': 'first_name-update'})
            elif last_name:
                user.last_name = last_name
                user.save()
                return Response({'success': True, 'msg': 'last_name-update'})
            elif email:
                if Profile.searchEmail(email) is False:
                    if validateStructureEmail(email) is True:
                        user.email = email
                        user.save()
                        return Response({'success': True, 'msg': 'email-update'})
                    else:
                        return Response({'success': False, 'err': 'email-invalid'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'success': False, 'err': 'email-exists'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            elif avatar:
                Profile.updateAvatar(profile, avatar)
                return Response({'success': True, 'msg': 'avatar-update'})
            elif icono:
                Profile.updateIcono(profile, icono)
                return Response({'success': True, 'msg': 'icono-update'})
            elif birth_date:
                Profile.updateBirthdate(profile, birth_date)
                return Response({'success': True, 'msg': 'birth_date-update'})
            elif gender:
                Profile.updateGender(profile, gender)
                return Response({'success': True, 'msg': 'gender-update'})
            elif phone:
                Profile.updatePhone(profile, phone)
                return Response({'success': True, 'msg': 'phone-update'})
            elif biography:
                Profile.updateBiography(profile, biography)
                return Response({'success': True, 'msg': 'biography-update'})
            elif location:
                Profile.updateLocation(profile, location)
                return Response({'success': True, 'msg': 'location-update'})
            elif company:
                Profile.updateCompany(profile, company)
                return Response({'success': True, 'msg': 'company-update'})
            elif profession:
                Profile.updateProfession(profile, profession)
                return Response({'success': True, 'msg': 'profession-update'})
            elif address:
                Profile.updateAddress(profile, address)
                return Response({'success': True, 'msg': 'address-update'})
            elif avialability:
                Profile.updateAvialability(profile, avialability)
                return Response({'success': True, 'msg': 'avialability-update'})
            elif i_search:
                WantedCategory.deleteAllSearch(profile)
                for element in i_search:
                    WantedCategory.create(element['pk'], profile, 2)
                return Response({'success': True, 'msg': 'i_search-update'})
            elif i_have:
                WantedCategory.deleteAllHave(profile)
                for element in i_have:
                    WantedCategory.create(element['pk'], profile, 1)
                return Response({'success': True, 'msg': 'i_have-update'})
            elif tags:
                TagProfile.deleteAll(profile)
                for element in tags:
                    TagProfile.create(element['pk'], profile)
                return Response({'success': True, 'msg': 'tags-update'})
            else:
                return Response({'success': False, 'err': 'field-undefined'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# ---------------------------------METODOS LOGICOS----------------------------------------


# Metodo de verificacion de estructura del email
def validateStructureEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


# Metodo para la generacion del username unico para un nuevo usuario
def generateRandomUsername(name, length=8, chars=ascii_lowercase + digits, split=4, delimiter='-'):
    username = ''.join([choice(chars) for i in range(length)])
    if split:
        username = delimiter.join([username[start:start + split] for start in range(0, len(username), split)])
    username = name + '-' + username
    try:
        User.objects.get(username=username)
        return Profile.generateRandomUsername(name=name, length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username


# ---------------------------------METODOS OBTENCION DE DATOS---------------------------------

# Metodo de obtencion de perfil de usuario
def getProfile(user):
    return get_object_or_404(Profile, user=user)


# Metodo de obtencion de token de usuario
def getToken(user):
    token, _ = ExpiringToken.objects.get_or_create(user=user)
    if token.expired():
        token.delete()
        token = ExpiringToken.objects.create(user=user)
    return token


# Metodo de obtencion de usuario
def getUser(id):
    return Profile.getUser(id)


# Metodo de obtencion de usuario
def getUserEmail(email):
    return Profile.getUserEmail(email)


# Metodo que retorna el tiempo inscrito en redzza del usuario ingresado por parametro
def getDurationUser(user):
    return (timezone.now() - user.date_joined)


# Metodo que retorna el numero de seguidores del usuario ingresado por parametro
def getNumberFollowersUser(user):
    return len(Follow.searchFollowers(getProfile(user)))


# Metodo que retorna las categorias que ofrece el usuario ingresado por parametro
# i_have(Ofrezco) --> 1
def getHaveCategoriesUser(user):
    return WantedCategory.searchHave(getProfile(user))


# Metodo que retorna las categorias que busca el usuario ingresado por parametro
# i_search(Busco) --> 2
def getSearchCategoriesUser(user):
    return WantedCategory.searchOffer(getProfile(user))


# Metodo que retorna las publicaciones del usuario tiene
def getNoticesHaveUser(user):
    return Notice.getNoticeHave(getProfile(user))


# Metodo que retorna las publicaciones del usuario busca
def getNoticesSearchUser(user):
    return Notice.getNoticeSearch(getProfile(user))


# Metodo que retorna los tags del usuario
def getTagsUser(user):
    return TagProfile.searchTags(getProfile(user))


# Metodo que retorna el icono del usuario
def getIconUser(user):
    return Icon.searchIcono(getProfile(user).icono)


# Metodo que retorna el icono del usuario
def getImageNotice(notice):
    return Image.search(notice)


# Metodo de obtencion de tiempo restante del token de usuario
def getTimeToken(token):
    return token_settings.EXPIRING_TOKEN_LIFESPAN - (timezone.now() - token.created)
