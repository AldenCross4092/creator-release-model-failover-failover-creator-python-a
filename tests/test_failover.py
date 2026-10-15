from src.creator_service import PublishRequest, VendorUnavailable, publish_with_failover


def test_publish_uses_backup_vendor_and_notifies_subscribers():
    request = PublishRequest("creator-7", "Studio notes", "asset-9", ("a", "b", "c"))
    calls = []

    def primary(_):
        calls.append("primary")
        raise VendorUnavailable("primary unavailable")

    def backup(item):
        calls.append("backup")
        return f"{item.title} is live."

    receipt = publish_with_failover(request, (("primary", primary), ("backup", backup)), "secret")
    assert calls == ["primary", "backup"]
    assert receipt.vendor == "backup"
    assert receipt.subscribers_notified == 3
    assert receipt.download_path.startswith("/downloads/asset-9?")
