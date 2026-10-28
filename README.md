# SignalHouse Python SDK

Python SDK for the SignalHouse API. Manage SMS/MMS messaging, phone numbers, 10DLC brands & campaigns, billing, and more.

Full API reference and guides: https://app2.signalhouse.io/docs

## Installation

```bash
pip install signalhouse-sms
```

## Agent skills

The package bundles the Signal House agent skills, which teach a coding agent the order the
platform enforces, what carriers require, and what a send cannot do before a campaign is approved.

A Python wheel cannot run anything at install time, so place them with one command:

```bash
signalhouse-skills            # install into this project
signalhouse-skills --list     # show what is bundled and which release it came from
signalhouse-skills --force    # create the agent directory if the project has none yet
```

It only ever writes inside the project, never your home directory, and never overwrites a skill you
have edited.

Or install from source:

```bash
pip install -e .
```

## Quick Start

```python
from signalhouse_sms import SignalHouseSDK

# Initialize the SDK
sdk = SignalHouseSDK(
    api_key="your-api-key",
    base_url="https://v2.signalhouse.io",
)

# Send an SMS
response = sdk.messages.send_sms(
    sender_phone_number="15551234567",
    recipient_phone_numbers="15559876543",
    message_body="Hello from SignalHouse!",
)

if response["success"]:
    print("Message sent!", response["data"])
else:
    print("Error:", response["error"])
```

## Authentication

All methods accept an optional `token` parameter to override the default API key per-request:

```python
response = sdk.billing.get_wallet("G12345678", token="user-jwt-token")
```

Pass `idempotency_key` to make a create, update or delete safe to retry: the SDK sends it as the `Idempotency-Key` header, and a retry with the same key and request replays the first response instead of running it again. Keys are scoped to the authenticated user and kept for 24 hours.

```python
import uuid

response = sdk.subgroups.create_subgroup({"groupId": "G0000001", "subgroupName": "Support"}, idempotency_key=str(uuid.uuid4()))
```

## Domains

The SDK is organized into domain modules matching the SignalHouse API:

| Domain | Description |
|--------|-------------|
| `sdk.auth` | Login, password reset, auth history |
| `sdk.billing` | Wallets, payment methods, funds, invoices, fees |
| `sdk.brands` | 10DLC brand registration and management, toll-free business verification |
| `sdk.campaigns` | 10DLC campaign management |
| `sdk.groups` | Group management |
| `sdk.landings` | Landing page management (with file uploads) |
| `sdk.templates` | Versioned message templates: drafts, publish, archive, validate, capabilities, media upload |
| `sdk.messages` | Send SMS/MMS/Group MMS, message logs, analytics |
| `sdk.notifications` | Notification management |
| `sdk.numbers` | Phone number purchase, assignment, transfer, lookup |
| `sdk.shortlinks` | URL shortlink operations |
| `sdk.subgroups` | Subgroup management |
| `sdk.subscriptions` | Subscription management |
| `sdk.users` | User and service user management |
| `sdk.webhooks` | Webhook management |

## Admin Methods

Some domains have admin-only methods accessible via the `.admin` sub-object. Enable them by passing `enable_admin=True`:

```python
sdk = SignalHouseSDK(
    api_key="your-api-key",
    base_url="https://v2.signalhouse.io",
    enable_admin=True,
)

# Admin-only: approve a campaign
response = sdk.campaigns.admin.approve_campaign("campaign-id", token="admin-token")

# Admin-only: list all groups
response = sdk.groups.admin.get_groups(page=1, limit=20, token="admin-token")
```

Domains with admin sub-objects: `campaigns`, `groups`, `subscriptions`, `users`.

## Response Format

All methods return a standardized dictionary:

**Success:**
```python
{"success": True, "data": {...}, "status": 200}
```

**Error:**
```python
{"success": False, "error": "Error message", "status": 400}
```

## File Uploads

The `landings` and `messages` domains support multipart file uploads:

```python
# Create a landing page with a logo
with open("logo.png", "rb") as f:
    response = sdk.landings.create_landing(
        landing_data={
            "brandId": "brand-id",
            "description": "My landing page",
            "primaryBackgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F0F0F0",
            "primaryTextColor": "#000000",
            "secondaryTextColor": "#333333",
        },
        file=("logo.png", f, "image/png"),
    )

# Send an MMS with images
with open("photo.jpg", "rb") as img:
    response = sdk.messages.send_mms(
        sender_phone_number="15551234567",
        recipient_phone_numbers=["15559876543"],
        message_body="Check this out!",
        images=[("photo.jpg", img, "image/jpeg")],
    )
```

## Error Handling

```python
from signalhouse_sms import SignalHouseSDK, SignalHouseValidationError

sdk = SignalHouseSDK(api_key="your-key", base_url="https://v2.signalhouse.io")

try:
    # This will raise SignalHouseValidationError because group_id is required
    sdk.billing.get_wallet("")
except SignalHouseValidationError as e:
    print(f"Validation error: {e.message}")  # "Missing required parameter: groupId"
```

## Requirements

- Python 3.10+
- `requests` >= 2.28.0
