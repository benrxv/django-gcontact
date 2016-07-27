"""
djangogcontact.observer


"""

from dvm.celery import app
from celery.contrib.methods import task_method
from django.db.models import signals
from gdata.contacts.data import ContactEntry
from gdata.contacts.client import ContactsQuery
from oauth2client.client import AccessTokenCredentials
from httplib2 import Http
from apiclient.discovery import build
import requests
from gdata.contacts.service import ContactsService


class ContactObserver(object):
    """
    
    """
    
    DEFAULT_FEED = 'https://www.google.com/m8/feeds/contacts/default/full'
    
    def __init__(self, email, private_key, refresh_token=None,
                 feed=None, client=None):
        """
        Initialize an instance of the CalendarObserver class.
        """

        self.adapters = {}
        self.email = email
        self.refresh_token = refresh_token
        self.private_key = private_key
        self.feed = feed
        self.client = client
        self.model = None

    def get_model(self):
        if not self.model:
            from models import Contact
            self.model = Contact
        return self.model

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
        self.update.delay(kwargs['sender'], kwargs['instance'])
    
    def on_delete(self, **kwargs):
        """
        Called by Django's signal mechanism when an observed model is deleted.
        """
        self.delete.delay(kwargs['sender'], kwargs['instance'])
    
    def get_client(self):
        """
        Get an authenticated gdata.calendar.client.CalendarClient instance.
        """
        from gdata.gauth import OAuth2Token
        token = self.get_access_token()
        auth = OAuth2Token(
            client_id=self.email,
            client_secret=self.private_key,
            scope='https://www.google.com/m8/feeds',
            user_agent='app.testing',
            access_token=token)
        # client = ContactsService(source='vetware/1.0')
        from gdata.contacts.client import ContactsClient
        client = ContactsClient(source='vetware/1.0')
        # client.authorize(token)
        auth.authorize(client)
        # credentials = AccessTokenCredentials(token, 'vetware/1.0')
        # http = credentials.authorize(Http())
        # client = build('contacts', 'v3', http=http)
        return client
    
    def get_access_token(self):
        url = "https://accounts.google.com/o/oauth2/token"
        payload = {
            "client_id": self.email,
            "client_secret": self.private_key,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        resp = requests.post(url, data=payload)
        resp_data = resp.json()
        print resp_data
        self.access_token = resp_data['access_token']
        return self.access_token

    def get_contact(self, client, instance, feed=None):
        """
        Retrieves the specified contact from Google Contacts, or returns None
        if the retrieval fails.
        """
        if feed is None:
            feed = self.feed
        client = self.get_client()
        contact_id = self.get_model().objects.get_contact_id(instance, feed)
        try:
            contact = client.GetContact(contact_id)
        except Exception:
            # See if this email address is already in a Google Contact
            # that isn't already sync'd
            contact = None
            query = ContactsQuery()
            query.text_query = instance.email
            contact_list = client.GetContacts(q=query).entry
            # try:
            #     contact = client.getContact(instance.email)
            # except Exception:
            #     pass
            if len(contact_list) == 1:
                if any(True for email in contact_list[0].email if email.address == instance.email):
                    contact = contact_list[0]
                    self.get_model().objects.set_contact_id(instance, feed,
                                                   contact.get_edit_link().href)
        return contact
    
    @app.task(filter=task_method, ignore_result=True)
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
                self.get_model().objects.set_contact_id(instance, feed,
                                               new_contact.get_edit_link().href)
    
    @app.task(filter=task_method, ignore_result=True)
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
        self.get_model().objects.delete_contact_id(instance, feed)
