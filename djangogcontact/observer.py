"""
djangogcontact.observer


"""

from django.db.models import signals
from gdata.contacts.data import ContactEntry
from gdata.contacts.client import ContactsClient, ContactsQuery

from models import Contact

class ContactObserver(object):
    """
    
    """
    
    DEFAULT_FEED = 'https://www.google.com/m8/feeds/contacts/default/full'
    
    def __init__(self, email, password, feed=DEFAULT_FEED, client=None):
        """
        Initialize an instance of the CalendarObserver class.
        """
        self.adapters = {}
        self.email = email
        self.password = password
        self.feed = feed
        self.client = client
    
    def observe(self, model, adapter):
        """
        Establishes a connection between the model and Google Calendar, using
        adapter to transform data.
        """
        self.adapters[model] = adapter
        signals.post_save.connect(self.on_update, sender=model,
                                  dispatch_uid="djangogcontact post-save signal")
        signals.post_delete.connect(self.on_delete, sender=model,
                                    dispatch_uid="djangogcontact post-delete signal")
    
    def observe_related(self, model, related, selector):
        """
        Updates the Google Calendar entry for model when the related model is
        changed or deleted.  Selector should be a function object which accepts
        an instance of related as a parameter and returns an instance of type
        model.
        """
        def on_related_update(**kwargs):
            self.update(model, selector(kwargs['instance']))
        signals.post_save.connect(on_related_update, sender=related, weak=False)
        signals.post_delete.connect(on_related_update, sender=related,
                                    weak=False)
    
    def on_update(self, **kwargs):
        """
        Called by Django's signal mechanism when an observed model is updated.
        """
        self.update(kwargs['sender'], kwargs['instance'])
    
    def on_delete(self, **kwargs):
        """
        Called by Django's signal mechanism when an observed model is deleted.
        """
        self.delete(kwargs['sender'], kwargs['instance'])
    
    def get_client(self):
        """
        Get an authenticated gdata.calendar.client.CalendarClient instance.
        """
        if self.client is None:
            self.client = ContactsClient(source='django-gcontact')
            self.client.ClientLogin(self.email, self.password, self.client.source)
        return self.client
    
    def get_contact(self, client, instance, feed=None):
        """
        Retrieves the specified contact from Google Contacts, or returns None
        if the retrieval fails.
        """
        if feed is None:
            feed = self.feed
        contact_id = Contact.objects.get_contact_id(instance, feed)
        try:
            contact = client.GetContact(contact_id)
        except Exception:
            # See if this email address is already in a Google Contact
            # that isn't already sync'd
            contact = None
            query = ContactsQuery()
            query.text_query = instance.email
            contact_list = client.GetContacts(q=query).entry
            if len(contact_list) == 1:
                if any(True for email in contact_list[0].email if email.address == instance.email):
                    contact = contact_list[0]
                    Contact.objects.set_contact_id(instance, feed,
                                                   contact.get_edit_link().href)
        return contact
    
    def update(self, sender, instance):
        """
        Update or create an entry in Google Calendar for the given instance
        of the sender model type.
        """
        adapter = self.adapters[sender]
        if adapter.can_save(instance):
            client = self.get_client()
            feed = adapter.get_feed_url(instance) or self.feed
            contact = self.get_contact(client, instance, feed) or ContactEntry()
            adapter.get_contact_data(instance).populate_contact(contact)
            if contact.GetEditLink():
                client.Update(contact)
            else:
                new_contact = client.CreateContact(contact, insert_uri=feed)
                Contact.objects.set_contact_id(instance, feed,
                                               new_contact.get_edit_link().href)
    
    def delete(self, sender, instance):
        """
        Delete the entry in Google Calendar corresponding to the given instance
        of the sender model type.
        """
        adapter = self.adapters[sender]
        feed = adapter.get_feed_url(instance) or self.feed
        if adapter.can_delete(instance):
            client = self.get_client()
            contact = self.get_contact(client, instance, feed)
            if contact:
                client.Delete(contact)
        Contact.objects.delete_contact_id(instance, feed)
