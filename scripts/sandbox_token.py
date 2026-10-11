from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)

from roundup.sources import plaid_client

client = plaid_client()
created = client.sandbox_public_token_create(
    SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products("transactions")],
    )
)
exchanged = client.item_public_token_exchange(
    ItemPublicTokenExchangeRequest(public_token=created.public_token)
)
print(exchanged.access_token)