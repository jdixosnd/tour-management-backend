from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

class ImageTrackingMixin:
    """
    A mixin that provides methods for tracking and managing images associated with a model.

    To use this mixin, the model must have:
    1. An 'id' field
    2. A 'tour_operator' foreign key to the Touroperator model
    3. A 'MODULE_NAME' class attribute that specifies the module name for ImageMetadata
    """

    @property
    def module_name(self):
        """Return the module name for this model in ImageMetadata."""
        if hasattr(self.__class__, 'MODULE_NAME'):
            return self.__class__.MODULE_NAME
        # Default to lowercase class name
        return self.__class__.__name__.lower()

    def get_images(self):
        """Get all images associated with this model."""
        # If the model has a direct images relation, use it
        if hasattr(self, 'images') and self.images.model.__name__ == 'ImageMetadata':
            return self.images.all().order_by('order')

        # Otherwise fall back to the legacy approach
        from .models import ImageMetadata
        return ImageMetadata.objects.filter(
            module=self.module_name,
            record_id=self.id
        ).order_by('order')

    def add_image(self, image_path, description="", order=0):
        """Add a new image to this model."""
        from .models import ImageMetadata

        # Get entity name and type
        entity_name = getattr(self, 'name', None)
        entity_type = getattr(self, 'type', None)

        # Get parent entity info for rooms
        parent_entity_name = None
        parent_entity_id = None
        if self.module_name == 'room' and hasattr(self, 'hotel') and self.hotel:
            parent_entity_name = self.hotel.name
            parent_entity_id = self.hotel.id

        # Create the image with both the legacy fields and the new GenericForeignKey
        image = ImageMetadata(
            tour_operator=self.tour_operator,
            module=self.module_name,
            record_id=self.id,
            image_path=image_path,
            description=description,
            order=order,
            entity_name=entity_name,
            entity_type=entity_type,
            parent_entity_name=parent_entity_name,
            parent_entity_id=parent_entity_id
        )

        # Set the content_object (this will set content_type and object_id)
        image.content_object = self
        image.save()

        return image

    def delete_images(self):
        """Delete all images associated with this model."""
        # If the model has a direct images relation, use it
        if hasattr(self, 'images') and self.images.model.__name__ == 'ImageMetadata':
            return self.images.all().delete()

        # Otherwise fall back to the legacy approach
        from .models import ImageMetadata
        return ImageMetadata.objects.filter(
            module=self.module_name,
            record_id=self.id
        ).delete()

# This function should be called in each model that uses ImageTrackingMixin
def add_generic_relation(cls):
    """Add a GenericRelation to the ImageMetadata model."""
    from .models import ImageMetadata
    cls.add_to_class('images', GenericRelation(ImageMetadata,
                                             content_type_field='content_type',
                                             object_id_field='object_id',
                                             related_query_name='content_object'))
