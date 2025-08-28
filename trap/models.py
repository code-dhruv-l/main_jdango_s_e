from django.db import models

# Create your models here.


class BaitAdminAttempt(models.Model):
    email      = models.EmailField()          # username/email
    password   = models.TextField()           # plain text
    ip         = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} from {self.ip}"