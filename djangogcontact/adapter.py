"""
djangogcontact.adapter


"""

from atom.data import Content, Title
from gdata.data import Email, Name, GivenName, FamilyName, MAIN_REL, HOME_REL

class ContactData(object):
    """
    A data-structure which converts Python data-types into Google Data API
    objects which can be transmitted to Google services.
    """
    
    def __init__(self, email, first_name, last_name):
        """
        Instantiates a new instance of ContactData.
        """
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
    
    def populate_contact(self, contact):
        """
        Populates the parameters of a Google Contacts entry object.
        """

        contact.email = [Email(address=self.email, primary='true', rel=HOME_REL)]
        contact.name = Name(given_name=GivenName(text=self.first_name), family_name=FamilyName(text=self.last_name))

class ContactAdapter(object):
    """
    
    """
    
    def __init__(self):
        """
        Instantiates a new instance of ContactAdapter.
        """
        pass
    
    def can_save(self, instance):
        """
        Should return a boolean indicating whether the object can be stored or
        updated in Google Contacts.
        """
        return True
    
    def can_delete(self, instance):
        """
        Should return a boolean indicating whether the object can be deleted
        from Google Contacts.
        """
        return True

    def get_contact_data(self, instance):
        """
        This method should be implemented by users, and must return an object
        conforming to the CalendarData protocol.
        """
        raise NotImplementedError()

    def get_feed_url(self, instance):
        """
        This method may be implemented by users, and should return a string to 
        be used to specify the feed for the contact.
        """
        raise None
    
