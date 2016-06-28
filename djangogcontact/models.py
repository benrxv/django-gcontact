"""
djangogcontact.models


"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class ContactManager(models.Manager):
    """
    A custom manager for Contact models, containing utility methods for
    dealing with content-types framework.
    """
    
    def get_contact_id(self, obj, feed_id):
        """
        Gets the Google Calendar contact-id for a model, or returns None.
        """
        ct = ContentType.objects.get_for_model(obj)
        try:
            contact = self.get(content_type=ct, object_id=obj.pk, feed_id=feed_id)
            contact_id = contact.contact_id
        except models.ObjectDoesNotExist:
            contact_id = None
        return contact_id
    
    def set_contact_id(self, obj, feed_id, contact_id):
        """
        Sets the Google Contact contact-id for a model.
        """
        ct = ContentType.objects.get_for_model(obj)
        try:
            contact = self.get(content_type=ct, object_id=obj.pk, feed_id=feed_id)
            contact.contact_id = contact_id
        except models.ObjectDoesNotExist:
            contact = Contact(content_type=ct, object_id=obj.pk,
                              feed_id=feed_id, contact_id=contact_id)
        contact.save()
    
    def delete_contact_id(self, obj, feed_id):
        """
        Deletes the record containing the contact-id for a model.
        """
        ct = ContentType.objects.get_for_model(obj)
        try:
            contact = self.get(content_type=ct, object_id=obj.pk, feed_id=feed_id)
            contact.delete()
        except models.ObjectDoesNotExist:
            pass

class Contact(models.Model):
    """
    
    """
    
    # django.contrib.contenttypes 'magic'
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey()
    
    # google calendar contact_id and feed_id
    contact_id = models.CharField(max_length=255)
    feed_id = models.CharField(max_length=255)
    
    # custom manager
    objects = ContactManager()
    
    def __unicode__(self):
        """ Returns the string representation of the Contact. """
        return u"%s: (%s, %s)" % (self.object, self.feed_id, self.contact_id)
