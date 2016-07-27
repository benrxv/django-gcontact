"""
djangogcontact.adapter


"""

from atom.data import Content, Title
from gdata.data import Email, Name, GivenName, FamilyName, WORK_REL, OTHER_REL, MOBILE_REL, HOME_REL, FAX_REL, PhoneNumber, StructuredPostalAddress, Street, City, Region, Postcode, Country
from gdata.contacts.data import GroupMembershipInfo

class ContactData(object):
    """
    A data-structure which converts Python data-types into Google Data API
    objects which can be transmitted to Google services.
    """
    
    def __init__(self, email, first_name, last_name, address, city, state, zipcode, home_phone, cell_phone, work_phone, fax, primary_phone=None, group_url=None):
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
        self.group_url = group_url

    def populate_contact(self, contact):
        """
        Populates the parameters of a Google Contacts entry object.
        """

        email_addresses = [e.address for e in contact.email]
        if self.email and self.email not in email_addresses:
            if not email_addresses:
                primary = 'true'
            else:
                primary = 'false'
            contact.email.append(Email(address=self.email, primary=primary, rel=OTHER_REL))

        contact.name = Name(given_name=GivenName(text=self.first_name), family_name=FamilyName(text=self.last_name))
        phone_list = []
        PHONE_RELS = [
            (self.cell_phone, MOBILE_REL, 'false'),
            (self.home_phone, HOME_REL, 'false'),
            (self.work_phone, WORK_REL, 'false'),
            (self.fax, FAX_REL, 'false'),
            (self.primary_phone, OTHER_REL, 'true')
        ]
        phones_added = []
        for phone in PHONE_RELS:
            if phone[0] and phone[0] not in phones_added:
                if phone[0] == self.primary_phone:
                    primary = 'true'
                    PHONE_RELS.pop()
                else:
                    primary = phone[2]
                phones_added.append(phone[0])
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

        if self.group_url and not any([g for g in contact.group_membership_info if g.href == self.group_url]):    
            contact.group_membership_info.append(GroupMembershipInfo(href=self.group_url))

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
    
