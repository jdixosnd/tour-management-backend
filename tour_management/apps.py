from django.apps import AppConfig


class NlpEngineConfig(AppConfig):
    name = 'tour_management'

    def ready(self):
        # Import models and add GenericRelation to them
        from .models import Hotel, Room, Package, Destination, Event, SightSeeing, Cardealer
        from .mixins import add_generic_relation

        # Add GenericRelation to each model
        add_generic_relation(Hotel)
        add_generic_relation(Room)
        add_generic_relation(Package)
        add_generic_relation(Destination)
        add_generic_relation(Event)
        add_generic_relation(SightSeeing)
        add_generic_relation(Cardealer)
