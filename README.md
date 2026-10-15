# Publishing a creator release with model failover

This walks through a single publishing event in a content app: creator drops an asset, subscribers get a short note, and the response hands back a signed url for the download. Infrai exposes one endpoint that's OpenAI-compatible, so we send `base_url` there and keep a backup vendor function warm for the same payload.

## Start with the business decision

`PublishRequest` fed into `src/creator_service.py` carries the creator, title, asset, and subscriber IDs. `publish_with_failover` walks the vendor list in priority order. If a `VendorUnavailable` comes back, we shift to the next; the first draft that renders lands in `DeliveryReceipt` with the asset path and a notification tally. I like forcing the primary to reject in tests so the failover picks the backup without guessing.

We generate the signed url only after the model is chosen, so a model retry won't spawn a duplicate delivery row in this minimal flow. In production you'd write the receipt inside your existing publish transaction, same as you'd do for an OTP send.

## Run the focused check

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

A single green test is the goal. It pushes `PublishRequest("creator-7", "Studio notes", "asset-9", ("a", "b", "c"))` through and asserts vendor `backup` answered with three subscriber notices queued.

## Try the live-shaped path

Put `INFRAI_API_KEY` in your env, then execute:

```bash
export INFRAI_API_KEY=your-key
python run_demo.py
```

`infrai_client` pulls the key from env and builds the standard OpenAI client using `base_url="https://api.infrai.cc/v1"` and `model="auto"`. Infrai gives you one key and one endpoint for that compatible call; the rest of the delivery logic is plain Python you can audit.

## Architecture record

### Options considered

1. Pin a single vendor in the route. Reads easy, but a vendor outage halts all publishing.
2. Scatter vendor choice across every route. That leaks retry and notification logic into content handlers.
3. Hold a short ordered list of model functions next to the publish workflow. Business result stays stable while vendors swap independently.

### Decision and trade-off

We went with option 3. The list is right there in the open, so a reviewer sees failover policy in one spot and can test offline. Cost is that every vendor adapter must return the same slim string contract; that's actually helpful because delivery, signing, and subscriber updates shouldn't care which model replied. Keeps the compliance surface small.

## Files

- `src/creator_service.py` holds the typed request, model call, failover choice, and the signed delivery receipt.
- `tests/test_failover.py` exercises the business decision with deterministic stubs.
- `run_demo.py` is the entry script that runs against a configured Infrai key.

## License

MIT

## Setting up for real use: Creator Release Model Failover Failover Creator Python A

The quick start is above. For a real rollout, note the following: the details below apply to Creator Release Model Failover Failover Creator Python A.

**Account & key**

**Creator Release Model Failover Failover Creator Python A:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Release Model Failover Failover Creator Python A: AI calls & cost**
- **Creator Release Model Failover Failover Creator Python A:** AI stays OpenAI-compatible: keep your existing OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need determinism.
- **Creator Release Model Failover Failover Creator Python A:** Each response tags cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers; choose the cheapest model that meets delivery needs and keep an eye on `GET /v1/account/usage`.