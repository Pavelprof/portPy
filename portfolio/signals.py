from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction, Deal, Position
from simple_history.models import HistoricalRecords

@receiver([post_save, post_delete], sender=Transaction)
def update_positions_from_transaction(sender, instance, **kwargs):

    account = instance.account
    asset = instance.asset_transaction
    quantity = instance.quantity_transaction

    try:
        position = Position.objects.get(account=account, asset=asset)

        if kwargs['signal'] == post_delete:
            position.quantity_position -= quantity
            position.save()
        elif kwargs['created']:
            position.quantity_position += quantity
            position.save()
        else:
            previous_instance = Transaction.history.filter(id=instance.id).order_by('-history_date').first()
            Position.objects.filter(asset=previous_instance.asset_transaction, account=previous_instance.account).update(quantity_position=Position.F('quantity_position') - previous_instance.quantity_transaction)
            Position.objects.filter(asset=instance.asset_transaction, account=instance.account).update(quantity_position=Position.F('quantity_position') + instance.quantity_transaction)

    except Position.DoesNotExist:
        Position.objects.create(account=account, asset=asset, quantity_position=quantity)
