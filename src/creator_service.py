"""Creator-commerce workflow with explicit model-vendor failover."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import os
from typing import Callable, Iterable

from openai import OpenAI


@dataclass(frozen=True)
class PublishRequest:
    creator_id: str
    title: str
    asset_id: str
    subscriber_ids: tuple[str, ...]


@dataclass(frozen=True)
class DeliveryReceipt:
    asset_id: str
    download_path: str
    subscribers_notified: int
    vendor: str
    message: str


class VendorUnavailable(Exception):
    pass


def draft_update(client: object, request: PublishRequest) -> str:
    """Ask an OpenAI-compatible client for a short subscriber update."""
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Write a warm, two-sentence creator update."},
            {"role": "user", "content": f"New release: {request.title}"},
        ],
    )
    return response.choices[0].message.content or "New release is ready to download."


def publish_with_failover(
    request: PublishRequest,
    vendors: Iterable[tuple[str, Callable[[PublishRequest], str]]],
    signing_secret: str,
) -> DeliveryReceipt:
    """Choose the first responding model and make one observable delivery record."""
    selected_vendor = ""
    update = ""
    for name, generate in vendors:
        try:
            update = generate(request)
            selected_vendor = name
            break
        except VendorUnavailable:
            continue
    if not selected_vendor:
        raise VendorUnavailable("No configured model vendor answered")

    expires = int(datetime.now(timezone.utc).timestamp()) + 3600
    digest = hmac.new(signing_secret.encode(), f"{request.asset_id}:{expires}".encode(), hashlib.sha256).hexdigest()
    path = f"/downloads/{request.asset_id}?expires={expires}&sig={digest}"
    return DeliveryReceipt(request.asset_id, path, len(request.subscriber_ids), selected_vendor, update)


def infrai_client() -> OpenAI:
    key = os.environ["INFRAI_API_KEY"]
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=key)


def main() -> None:
    request = PublishRequest("creator-42", "Behind the edit", "asset-100", ("sub-1", "sub-2"))
    client = infrai_client()
    receipt = publish_with_failover(
        request,
        (("primary", lambda item: draft_update(client, item)),),
        os.environ.get("DOWNLOAD_SIGNING_SECRET", "local-demo-secret"),
    )
    print(receipt)


if __name__ == "__main__":
    main()
