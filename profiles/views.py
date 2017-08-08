from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.contrib.auth.models import User
from categories.models import WantedCategory, SuggestedCategory
from tags.models import TagProfile
from .models import Profile, Place, Follow
from .serializers import ProfileSerializer, UserSerializer, PlaceSerializer, FollowSerializer
from string import ascii_lowercase, digits
from random import choice
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import EmailAuthenticationForm
from rest_framework_expiring_authtoken.models import ExpiringToken
from django.shortcuts import get_object_or_404


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().filter(is_staff=False)
    serializer_class = UserSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class ApiServicesViewSet(viewsets.ViewSet):

    # Validacion del correo que se intenta registrar
    @list_route(methods=['post'])
    def validateEmail(self, request):
        email = request.POST.get('email', None)
        if email:
            return Response({'exists': Profile.searchEmail(email), 'data': email})
        else:
            return Response({'err': 'Incomplete data'}, status=status.HTTP_400_BAD_REQUEST)

    # Creacion de un usuario
    @list_route(methods=['post'])
    def createUser(self, request):
        email = request.POST.get('email', None)
        username = generateRandomUsername(request.POST.get('first_name', None))
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        password = request.POST.get('password', None)
        place = request.POST.get('place', None)
        i_search = request.POST.get('i_search', None)
        i_have = request.POST.get('i_have', None)
        suggesting = request.POST.get('suggesting', None)

        if email and username and first_name and last_name and password and place and i_search and i_have:
            if Profile.searchEmail(email) is False:
                if validateStructureEmail(email):
                    user, created = Profile.createUser(email, username, first_name, last_name, password)
                    if created:
                        profile = Profile.create(place, user)
                        # i_have(Ofrezco) --> 1 ; i_search(Busco) --> 2
                        for element in json.loads(i_have):
                            WantedCategory.create(element['pk'], profile, 1)
                        for element in json.loads(i_search):
                            WantedCategory.create(element['pk'], profile, 2)
                        if suggesting:
                            SuggestedCategory.create(suggesting, profile)
                        login(request, user, 'profiles.backends.EmailBackend')
                        token = Token.objects.create(user=user)
                        return Response({'success': True, 'msg': 'user-created', 'token': token.key}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'success': False, 'err': 'User not created'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'success': False, 'err': 'Invalid Email'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'err': 'email-exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'err': 'Incomplete data'}, status=status.HTTP_400_BAD_REQUEST)

    # Login por correo electronico y contraseña
    @list_route(methods=['post'])
    def loginEmail(self, request):
        form = EmailAuthenticationForm(request.POST or None)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            token, _ = ExpiringToken.objects.get_or_create(user=user)
            if token.expired():
                token.delete()
                token = ExpiringToken.objects.create(user=user)
            if user.is_staff:
                return Response({'success': True, 'msg': 'user-admin', 'token': token.key})
            else:
                return Response({'success': True, 'msg': 'user-normal', 'token': token.key})
        else:
            return Response({'success': False, 'err': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Edicion de informacion del usuario
    @list_route(methods=['post'])
    def updateUser(self, request):
        user = request.user
        profile = getProfile(user)
        username = request.POST.get('username', None)
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        avatar = request.POST.get('avatar', None)
        icono = request.POST.get('icono', None)
        birth_date = request.POST.get('birth_date', None)
        gender = request.POST.get('gender', None)
        phone = request.POST.get('phone', None)
        biography = request.POST.get('biography', None)
        location = request.POST.get('location', None)
        company = request.POST.get('company', None)
        profession = request.POST.get('profession', None)
        address = request.POST.get('address', None)
        avialability = request.POST.get('avialability', None)
        i_search = request.POST.get('i_search', None)
        i_have = request.POST.get('i_have', None)
        tags = request.POST.get('tags', None)

        try:
            if username:
                if Profile.searchUsername(username) is False:
                    user.username = username
                    user.save()
                    return Response({'success': True, 'msg': 'username-update'})
                else:
                    return Response({'success': False, 'err': 'username-exists'}, status=status.HTTP_400_BAD_REQUEST)
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
                    return Response({'success': False, 'err': 'email-exists'}, status=status.HTTP_400_BAD_REQUEST)
            elif password:
                user.set_password(password)
                user.save()
                return Response({'success': True, 'msg': 'password-update'})
            elif avatar:
                Profile.updateAvatar(profile, avatar)
                return Response({'success': True, 'msg': 'avatar-update-pendiente'})
            elif icono:
                Profile.updateAvatar(profile, icono)
                return Response({'success': True, 'msg': 'icono-update-pendiente'})
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
                place = Place.searchCity(location)
                Profile.updateLocation(profile, place)
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
                for element in json.loads(i_search):
                    WantedCategory.create(element['pk'], profile, 2)
                return Response({'success': True, 'msg': 'i_search-update'})
            elif i_have:
                WantedCategory.deleteAllHave(profile)
                for element in json.loads(i_have):
                    WantedCategory.create(element['pk'], profile, 1)
                return Response({'success': True, 'msg': 'i_have-update'})
            elif tags:
                TagProfile.deleteAll(profile)
                for element in json.loads(tags):
                    TagProfile.create(element['pk'], profile)
                return Response({'success': True, 'msg': 'tags-update'})
            else:
                return Response({'success': False, 'err': 'field-undefined'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_400_BAD_REQUEST)


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
