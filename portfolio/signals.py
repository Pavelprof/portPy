from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction, Position

@receiver([post_save, post_delete], sender=Transaction)
def update_positions_from_transaction(sender, instance, **kwargs):

    def upd_or_crt_pos(account, asset, quantity):
        try:
            position = Position.objects.get(account=account, asset=asset)
            position.quantity_position += quantity
            position.save()
        except Position.DoesNotExist:
            Position.objects.create(account=account, asset=asset, quantity_position=quantity)

    if kwargs['signal'] == post_delete:
        upd_or_crt_pos(instance.account, instance.asset_transaction, -instance.quantity_transaction)
    elif kwargs['created']:
        upd_or_crt_pos(instance.account, instance.asset_transaction, instance.quantity_transaction)
    else:
        new_trans = instance.history.first()
        prev_trans = new_trans.prev_record
        # Rollback of the previous version of the transaction in positions
        upd_or_crt_pos(prev_trans.account, prev_trans.asset_transaction, -prev_trans.quantity_transaction)
        # Applying the new version of the transaction in positions
        upd_or_crt_pos(new_trans.account, new_trans.asset_transaction, new_trans.quantity_transaction)