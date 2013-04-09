==========
djangogcontact
==========

A Django application allowing developers to synchronise instances of their models with Google Contacts. Using Django's signals mechanism and generic relations, no changes to the model being synchronised are required, and synchronisation occurs without user intervention over the models lifecycle.

Usage
=====

In a typical scenario, the following steps are required to use django-gcontact:

Add djangogcontact to the list of installed applications in your settings.py.
Define a djangogcontact.adapter.ContactAdapter for each model you want synchronised.
Instantiate a djangogcontact.observer.ContactObserver for each Google Contact feed.
Call the ContactObserver.observe(model, adapter) method to link models with the Google Contact feed.
See GettingStarted for more information, and RelatedModels for information about sending updates when related objects are changed.

Example
=======

The code in this example is sufficient to bind a model to Google Contact::

    from django.conf import settings

    from djangogcontact.adapter import ContactAdapter, ContactData
    from djangogcontact.observer import ContactObserver

    from models import Client

    class ClientAdapter(ContactAdapter):
        """
        A contact adapter for the Client model.
        """
    
        def get_contact_data(self, instance):
            """
            Returns a ContactData object filled with data from the adaptee.
            """

            email = instance.email
            first_name = instance.first
            last_name = instance.last
            address = instance.address
            city = instance.city
            state = instance.state
            zipcode = instance.zipcode
            cell_phone = instance.cellphone
            home_phone = instance.homephone
            work_phone = instance.busphone
            fax = instance.faxphone
            primary_phone = instance.bestphone
            return ContactData(email, first_name, last_name, address, city, state, zipcode, home_phone, cell_phone, work_phone, fax, primary_phone=primary_phone)

        def get_feed_url(self, instance):
            """
            This method may be implemented by users, and should return a string to 
            be used to specify the feed for the contact.
            """
            return 'https://www.google.com/m8/feeds/contacts/default/full'
    
    contact_observer = ContactObserver(email=settings.CONTACT_EMAIL,
                                       password=settings.CONTACT_PASSWORD)
    
    contact_observer.observe(Client, ClientAdapter())
