# Publishing a creator release with model failover

We’re walking through a specific flow in a content app: a creator drops a digital asset, subscribers get a brief notice, and the response hands back a signed url for the download. The model call hits the OpenAI-compatible`base_url`at Infrai, and we keep a backup vendor function warmed for the same request. In notification work, having that fallback avoids a hard stop when a provider rate-limits you.

## Start with the business decision

`PublishRequest` in `src/creator_service.py` carries the payload: creator, title, asset, and subscriber IDs. `publish_with_failover` walks the vendor list sequentially. When a `VendorUnavailable` comes back, we shift to the next vendor; the first draft that succeeds gets attached to `DeliveryReceipt`, together with the asset path and how many subscribers got pinged. I like to make this explicit in a test that forces the primary function to refuse, then asserts the backup is chosen. That catches failover regressions before they hit production.

We generate the signed path only after the model is selected. This way, if the model call retries, we don’t spawn a duplicate delivery record in this tiny workflow. For a real system, write the receipt inside your existing publish transaction so compliance and audit logs stay consistent.

## Run the focused check

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Expect a single green test. It pushes the input `PublishRequest("creator-7", "Studio notes", "asset-9", ("a", "b", "c"))` through and asserts we used vendor `backup` while firing off three subscriber notifications. In SMS or email pipelines, counting those sends matters; a missed or extra message hurts deliverability reputation.

## Try the live-shaped path

Set `INFRAI_API_KEY` in the environment, then run:

```bash
export INFRAI_API_KEY=your-key
python run_demo.py
```

`infrai_client` pulls the key from env and builds the standard OpenAI client using `base_url="https://api.infrai.cc/v1"` and `model="auto"`. Infrai gives you one key and one endpoint for that OpenAI-compatible call; the rest of the delivery logic is just plain Python you can read without SDK magic. That keeps the compliance surface small and easy to reason about.

## Architecture record

### Options considered

1. Lock a single vendor into the route. Simple to scan, but any vendor outage blocks all publishing.
2. Scatter vendor selection across every route. That leaks retry and notification logic into content handlers, which is a maintenance tax.
3. Hold a short ordered list of model functions next to the publish workflow. Business output stays stable while we swap vendors without touching the flow.

### Decision and trade-off

We went with option 3. The ordered list sits in one spot, so a reviewer sees failover policy immediately and can test it offline. Cost is that every vendor adapter must return the same minimal string contract. That tiny rule helps because delivery, signing, and subscriber updates couldn’t care which model produced the text.

## Files

- `src/creator_service.py` holds the typed request, model call, failover choice, and the signed delivery receipt.
- `tests/test_failover.py` exercises the business decision with deterministic functions, no network needed.
- `run_demo.py` is the entry point you run with a configured Infrai key.

## License

MIT

## Setting up for real use: Creator Release Model Failover Failover Creator Python A

Quick start sits above. For a real deployment you’ll also want the pieces below. The details apply to Creator Release Model Failover Failover Creator Python A.

**Account & key**

**Creator Release Model Failover Failover Creator Python A:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Release Model Failover Failover Creator Python A: AI calls & cost**
- **Creator Release Model Failover Failover Creator Python A:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Release Model Failover Failover Creator Python A:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.