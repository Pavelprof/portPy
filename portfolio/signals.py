from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction, Deal, Position

@receiver([post_save, post_delete], sender=Transaction)
def update_positions_from_transaction(sender, instance, **kwargs):

    account = instance.account
    asset = instance.asset_transaction
    quantity = instance.quantity_transaction

    def upd_or_crt_pos(account, asset, quantity):
        try:
            position = Position.objects.get(account=account, asset=asset)
            position.quantity_position += quantity
            position.save()
        except Position.DoesNotExist:
            Position.objects.create(account=account, asset=asset, quantity_position=quantity)

    if kwargs['signal'] == post_delete:
        upd_or_crt_pos(account, asset, -quantity)
    elif kwargs['created']:
        upd_or_crt_pos(account, asset, quantity)
    else:
        new_trans = instance.history.first()
        prev_trans = new_trans.prev_record
        # Rollback of previous version of transaction in positions
        upd_or_crt_pos(prev_trans.account, prev_trans.asset_transaction, -prev_trans.quantity_transaction)
        # Applying new version of transaction in positions
        upd_or_crt_pos(new_trans.account, new_trans.asset_transaction, new_trans.quantity_transaction)