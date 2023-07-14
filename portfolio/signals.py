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

        if kwargs['signal'] == post_delete:
            position.quantity_position -= quantity
            position.save()
        elif kwargs['created']:
            position.quantity_position += quantity
            position.save()
        else:
            new_trans = instance.history.first()
            prev_inst = new_trans.prev_record
            prev_pos = Position.objects.filter(account = prev_inst.account, asset = prev_inst.asset_transaction)
            prev_pos.update(quantity_position = prev_pos.first().quantity_position - prev_inst.quantity_transaction)
            new_pos = Position.objects.filter(id = position.id)
            new_pos.update(quantity_position = new_pos.first().quantity_position + new_trans.quantity_transaction)

    except Position.DoesNotExist:
        Position.objects.create(account=account, asset=asset, quantity_position=quantity)
