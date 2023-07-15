from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction, Deal, Position

@receiver([post_save, post_delete], sender=Transaction)
def update_positions_from_transaction(sender, instance, **kwargs):

    account = instance.account
    asset = instance.asset_transaction
    quantity = instance.quantity_transaction

    if kwargs['signal'] == post_delete:
        position = Position.objects.get(account=account, asset=asset)
        position.quantity_position -= quantity
        position.save()
    elif kwargs['created']:
        try:
            position = Position.objects.get(account=account, asset=asset)
            position.quantity_position += quantity
            position.save()
        except Position.DoesNotExist:
            Position.objects.create(account=account, asset=asset, quantity_position=quantity)
    else:
        new_trans = instance.history.first()
        prev_inst = new_trans.prev_record
        prev_pos = Position.objects.filter(account = prev_inst.account, asset = prev_inst.asset_transaction)
        prev_pos.update(quantity_position = prev_pos.first().quantity_position - prev_inst.quantity_transaction)

        try:
            position = Position.objects.get(account=new_trans.account, asset=new_trans.asset_transaction)
            position.quantity_position += new_trans.quantity_transaction
            position.save()
        except Position.DoesNotExist:
            Position.objects.create(account=new_trans.account, asset=new_trans.asset_transaction, quantity_position=new_trans.quantity_transaction)
