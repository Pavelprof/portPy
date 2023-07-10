from django.db.models.signals import post_save
from django.dispatch import receiver
from portfolio.models import Transaction, Position

@receiver(post_save, sender=Transaction)
def update_positions(sender, instance, created, **kwargs):
    if created: