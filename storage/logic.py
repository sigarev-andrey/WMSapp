from django.db import transaction
from django.db.models import F
from .models import Storage, ItemInSupply, ItemInRelease

class CountError(Exception):
    '''Exception raised when haven't enought item count in storage'''
    pass

class SupplyService:
    '''
    Class for add or remove item in supply
    and syncronize count with item in storage
    '''

    @staticmethod
    @transaction.atomic
    def add_item(supply, item, count):
        '''
        Add item in supply and synchronize with storage
        '''

        # update or add item in current supply
        item_in_supply, exist_in_supply = ItemInSupply.objects.get_or_create(
            item=item,
            supply=supply,
            defaults={'count': count}
        )

        if not exist_in_supply:
            item_in_supply.count = F('count') + count
            item_in_supply.save(update_fields=['count'])

        # update ar add item in storage
        item_in_storage, exist_in_storage = Storage.objects.get_or_create(
            item=item,
            contract=supply.contract,
            defaults={'count': count}
        )

        if not exist_in_storage:
            item_in_storage.count = F('count') + count
            item_in_storage.save(update_fields=['count'])


    @staticmethod
    @transaction.atomic
    def delete_item(item_in_supply):
        """
        Remove item from supply and synchronize with storage
        """
        try:
            storage_item = Storage.objects.get(
                item=item_in_supply.item,
                contract=item_in_supply.supply.contract
            )
            
            # check available item count in storage
            if item_in_supply.count > storage_item.count:
                raise CountError(
                    f'Недостаточно товара на складе. '
                    f'Доступно: {storage_item.count}, требуется удалить: {item_in_supply.count}'
                )
            
            # reduce count in storage
            storage_item.count = F('count') - item_in_supply.count
            storage_item.save(update_fields=['count'])
            
            # delete from supply
            item_in_supply.delete()
            
        except Storage.DoesNotExist:
            raise Exception('Запись на складе не найдена')


class ReleaseService:
    '''
    Class for add or remove item in release
    and syncronize count with item in storage
    '''
    
    @staticmethod
    @transaction.atomic
    def add_item(release, storage_item, count):
        """
        Add item in release and synchronize with storage
        """
        from .models import ItemInRelease
        
        # check available item count in storage
        if count > storage_item.count:
            raise CountError(
                f'Недостаточно товара на складе. '
                f'Доступно: {storage_item.count}, требуется: {count}'
            )
        
        # update or add item in current release
        item_in_release, created = ItemInRelease.objects.get_or_create(
            release=release,
            item=storage_item,
            defaults={'count': count}
        )
        
        if not created:
            item_in_release.count = F('count') + count
            item_in_release.save(update_fields=['count'])
        
        # reduce item count in storage
        storage_item.count = F('count') - count
        storage_item.save(update_fields=['count'])
    
    @staticmethod
    @transaction.atomic
    def delete_item(item_in_release):
        """
        Remove item from release and return is's count to storage
        """
        storage_item = item_in_release.item
        
        # return count to storage
        storage_item.count = F('count') + item_in_release.count
        storage_item.save(update_fields=['count'])
        
        # remove from release
        item_in_release.delete()