"""
djangogcontact.adapter


"""

from atom.data import Content, Title
from gdata.data import Email, Name, GivenName, FamilyName, WORK_REL, OTHER_REL, MOBILE_REL, HOME_REL, FAX_REL, PhoneNumber, StructuredPostalAddress, Street, City, Region, Postcode, Country

class ContactData(object):
    """
    A data-structure which converts Python data-types into Google Data API
    objects which can be transmitted to Google services.
    """
    
    def __init__(self, email, first_name, last_name, address, city, state, zipcode, home_phone, cell_phone, work_phone, fax, primary_phone=None):
        """
        Instantiates a new instance of ContactData.
        """
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.cell_phone = cell_phone
        self.home_phone = home_phone
        self.work_phone = work_phone
        self.fax = fax
        self.primary_phone = primary_phone
    
    def populate_contact(self, contact):
        """
        Populates the parameters of a Google Contacts entry object.
        """

        contact.email = [Email(address=self.email, primary='true', rel=HOME_REL)]
        contact.name = Name(given_name=GivenName(text=self.first_name), family_name=FamilyName(text=self.last_name))
        phone_list = []
        PHONE_RELS = [
            (self.cell_phone, MOBILE_REL),
            (self.home_phone, HOME_REL),
            (self.work_phone, WORK_REL),
            (self.fax, FAX_REL),
            (self.primary_phone, OTHER_REL)
        ]

        primary = 'false'
        for phone in PHONE_RELS:
            if phone[0]:
                if phone[0] == self.primary_phone and primary == 'false':
                    primary = 'true'
                    PHONE_RELS.pop()
                phone_list.append(PhoneNumber(text=phone[0], rel=phone[1],
                                              primary=primary))

        if phone_list:
            contact.phone_number = phone_list

        contact.structured_postal_address = [
            StructuredPostalAddress(
                rel = HOME_REL,
                primary = 'true',
                city = City(text=self.city),
                country = Country(text='USA'),
                postcode = Postcode(text=self.zipcode),
                street = Street(text=self.address),
                region = Region(text=self.state)
            )
        ]



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
    
