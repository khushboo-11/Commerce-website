from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _


class User(AbstractUser):
    pass

class Listings(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_listings")
    title = models.CharField(max_length=64, help_text="The title to be displayed for the listing")
    description = models.CharField(max_length=2048, help_text="Description about the product")
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2, help_text="The starting price you want for the "
                                                                                 "product All prices are in USD!")                                                                                 
    image_url = models.CharField(max_length=2048, blank=True, help_text="This is not necessary but if you want to "
                                                                        "please include an online url for it here!")
    category = models.CharField(max_length=64, blank=True, help_text="This is also not necessary but if you want to"
                                                                     "Examples of categories include Fashion, Toys etc")                                                                     
    watchlist_users = models.ManyToManyField(User, blank=True, related_name="watchlist_items")

    closed = models.BooleanField(default=False)

    def current_price(self):
        return max([bid.value_offer for bid in self.bids.all()]+[self.starting_bid])

    def no_of_bids(self):
        return len(self.bids.all())

    def current_winning_bidder(self):
        return self.bids.get(value_offer=self.current_price()).user if self.no_of_bids() > 0 else None

    def __str__(self):
        return f'{self.title} by {self.owner}: {self.description}'

class Bids(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    value_offer = models.DecimalField(max_digits=8, decimal_places=2, help_text="How much are you willing to pay for"
                                                                                "this item?")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_made")

    def clean(self):
        # Don't allow value offer to be lower than current price of listing
        print(self.value_offer)
        print(self.listing.current_price())
        if self.value_offer and self.listing.current_price():
            if self.value_offer <= self.listing.current_price():
                raise ValidationError({'value_offer': _('Please make sure your bid value is higher than the current'
                                                        'price of the item!')})

    def __str__(self):
        return f"{self.user} offers to pay ${self.value_offer} for the listing: {self.listing}"

class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=2048)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.author} says {self.content} for listing: {self.listing}"
