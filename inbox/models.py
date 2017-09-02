from django.db import models
from profiles.models import Profile, File
from things.models import Notice


class Conversation(models.Model):
    modified = models.DateTimeField(auto_now_add=True)
    contestant = models.ManyToManyField(Profile)
    notice = models.ManyToManyField(Notice)

    def __str__(self):
        return str(self.modified)

    def create(profiles, notice):
        conversation = Conversation()
        conversation.save()
        for p in profiles:
            conversation.contestant.add(p)
        conversation.notice.add(notice)
        return conversation

    def search(profile):
        return Conversation.objects.filter(contestant=profile).order_by('modified')


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=File.generatePath, blank=True, null=True)
    review = models.BooleanField(default=False)
    sender = models.ForeignKey(Profile)
    conversation = models.ForeignKey(Conversation)

    def __str__(self):
        return self.text

    def create(text, image, profile, conversation):
        message = Message(text=text, image=image, sender=profile, conversation=conversation)
        message.save()
        return message

    def search(conversation):
        return Message.objects.filter(conversation=conversation).order_by('timestamp')
