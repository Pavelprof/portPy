from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from portfolio.models import Transaction, Deal, Position

@receiver([post_save, post_delete], sender=Transaction)
def update_positions_from_transaction(sender, instance, **kwargs):

    account = instance.account
    asset = instance.asset_transaction
    quantity = instance.quantity_transaction

    try:
        position = Position.objects.get(account=account, asset=asset)

        if instance.type_transaction == Transaction.Types_transaction.FUND:
            if kwargs.get('signal') == post_delete:
                position.quantity_position -= quantity
            else:
                position.quantity_position += quantity
        elif instance.type_transaction == Transaction.Types_transaction.PROFIT:
            pass

        position.save()
    except Position.DoesNotExist:
        Position.objects.create(account=account, asset=asset, quantity_position=quantity)
