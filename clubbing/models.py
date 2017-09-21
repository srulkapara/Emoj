from django.db import models

import base64

def decode_uuid(uuid):
    return int(base64.b64decode(uuid))

def encode_uuid(the_id):
    return base64.b64encode(bytes(str(the_id), 'utf-8'))

class User(models.Model):
    cookie_id = models.CharField(max_length=200)
    auth_token = models.CharField(max_length=200)
    auth_identifier = models.CharField(max_length=200)
    auth_type= models.CharField(max_length=20)
    first_seen = models.DateTimeField('first time seen')
    last_seen = models.DateTimeField('last time seen')
    page_count = models.IntegerField(default=0)
    campaign_id = models.CharField(max_length=200)
    campaign_source = models.CharField(max_length=20)
    referrer = models.ForeignKey('self', on_delete=models.CASCADE, null=True)


class Title(models.Model):
    text = models.CharField(max_length=50)
    # TODO: Move all to tables / enum
    category = models.CharField(max_length=30)
    source = models.CharField(max_length=30)
    language = models.CharField(max_length=20, default="English")

class Riddle(models.Model):
    riddler = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    seconds_spent = models.IntegerField() # seconds, when phrasing the riddle
    # TODO: Decide how to store unicode (json of ints?)
    unicode_chars = models.TextField()
    more_chars_considered = models.TextField()
    reshared = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    @classmethod
    def loadFromUUID(cls, uuid):
        return cls.objects.get(id=decode_uuid(uuid))

    def getUUID(self):
        return encode_uuid(self.id)

class ShownRiddle(models.Model):
    solver = models.ForeignKey(User, on_delete=models.CASCADE)
    riddle_shown = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    time_shown = models.DateTimeField('time shown')
    hints_used = models.TextField() # json of details?

class ShownTitle(models.Model):
    riddler = models.ForeignKey(User, on_delete=models.CASCADE)
    title_shown = models.ForeignKey(Title, on_delete=models.CASCADE)
    time_shown = models.DateTimeField('time shown')

class Solve(models.Model):
    riddle_show = models.ForeignKey(ShownRiddle, on_delete=models.CASCADE)
    time_spent = models.IntegerField() # seconds
    solve_time = models.DateTimeField('time solved')
    attempts_count = models.IntegerField(default=0)
    difficult_feedback = models.IntegerField(null=True)

class Emoji(models.Model):
    char_coded = models.TextField()
    image_url = models.TextField()
    image_source = models.CharField(max_length=30)
