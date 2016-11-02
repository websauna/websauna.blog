
from pyramid.security import Deny, Allow, Everyone
from websauna.system.admin.modeladmin import ModelAdmin, model_admin
from websauna.system.crud import Base64UUIDMapper
from websauna.wallet.ethereum.utils import eth_address_to_bin
from websauna.wallet.models import CryptoAddressAccount

from .models import UserOwnedAccount, Post
from .models import Asset
from .models import CryptoAddress
from .models import Account
from .models import     AssetNetwork


@model_admin(traverse_id="blog-posts")
class PostAdmin(ModelAdmin):
    """Manage user owned accounts and their balances."""

    title = "Blog posts"

    model = Post

    # UserOwnedAccount.id attribute is uuid type
    mapper = Base64UUIDMapper(mapping_attribute="id")

    class Resource(ModelAdmin.Resource):

        # Get something human readable about this object to the breadcrumbs bar
        def get_title(self):
            return self.get_object().title
