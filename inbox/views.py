from rest_framework import viewsets, status
from .models import Conversation, Message, Notice
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.decorators import list_route
from rest_framework.response import Response
from redzza import utils


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    http_method_names = ['get', 'head', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.notice.profile.user:
            return Response({'success': False, 'err': 'user-unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        self.perform_destroy(instance)
        return Response({'success': True})

    def list(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        try:
            conversation = Conversation.getConversation(pk)
            if utils.getProfile(request.user) not in conversation.contestant.all():
                return Response({'success': False, 'err': 'user-unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            conversations = [conversation]
            context = []
            for conversation in conversations:
                listContestants = utils.getProfileSimple(conversation.contestant.all())
                listReviews = utils.getProfileSimple(conversation.review.all())
                listNotices = utils.getDataNotice(conversation.notice.all(), fullData=False)
                listMessages = utils.getDataMessages(Message.search(conversation))
                context.append({'id': conversation.id, 'modified': conversation.modified, 'contestants': listContestants, 'notices': listNotices, 'reviews': listReviews, 'messages': listMessages})
            return Response({'success': True, 'data': context})
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ApiServicesViewSet(viewsets.ViewSet):

    # Inicio de conversacion
    @list_route(methods=['post'])
    def startConversation(self, request):
        try:
            user = request.user
            profileSender = utils.getProfile(user)
            idNotice = request.data.get('notice', None)
            notice = None if idNotice is None else Notice.getNotice(idNotice)
            idUserReceiver = request.data.get('user', None)
            profileReceiver = utils.getProfile(utils.getUser(idUserReceiver)) if notice is None else notice.profile
            profiles = []
            profiles.append(profileReceiver)
            profiles.append(profileSender)
            text = request.data.get('text', None)
            image = request.data.get('image', None)
            if profiles[0] == profiles[1]:
                return Response({'success': False, 'err': 'Message to myself not allowed'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if (text or image) and len(profiles) > 0:
                conversation = Conversation.create(profiles, notice)[0][0]
                Message.create(text, image, profileSender, conversation)
                return Response({'success': True, 'msg': 'conversation-created'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'err': 'Incomplete data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Agrega mensaje a una conversacion
    @list_route(methods=['post'])
    def addMessage(self, request):
        try:
            user = request.user
            profileSender = utils.getProfile(user)
            idConversation = request.data.get('conversation', None)
            conversation = Conversation.getConversation(idConversation)
            text = request.data.get('text', None)
            image = request.data.get('image', None)

            if (text or image) and conversation and profileSender:
                Message.create(text, image, profileSender, conversation)
                return Response({'success': True, 'msg': 'message-created'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'err': 'Incomplete data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Obtiene inbox de un usuario
    @list_route(methods=['get'])
    def getInbox(self, request):
        try:
            user = request.user
            profile = utils.getProfile(user)
            context = []
            conversations = Conversation.search(profile)
            for conversation in conversations:
                listContestants = utils.getProfileSimple(conversation.contestant.all())
                listReviews = utils.getProfileSimple(conversation.review.all())
                listNotices = utils.getDataNotice(conversation.notice.all(), fullData=False)
                listMessages = utils.getDataMessages(Message.search(conversation))
                context.append({'id': conversation.id, 'modified': conversation.modified, 'contestants': listContestants, 'notices': listNotices, 'reviews': listReviews, 'messages': listMessages})
            return Response({'success': True, 'data': context})
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Obtiene numero de notificaciones de un usuario
    @list_route(methods=['get'])
    def getCountNotifications(self, request):
        try:
            user = request.user
            profile = utils.getProfile(user)
            count = Conversation.countNotifications(profile)
            return Response({'success': True, 'count': count})
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Leido de conversacion
    @list_route(methods=['post'])
    def reviewConversation(self, request):
        try:
            user = request.user
            idProfile = utils.getProfile(user).id
            idConversation = request.data.get('conversation', None)
            Conversation.addReview(idProfile, idConversation)
            return Response({'success': True, 'msg': 'conversation-review'})
        except Exception as e:
            if hasattr(e, 'message'):
                err = e.message
            else:
                err = e
            return Response({'success': False, 'err': str(err)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
