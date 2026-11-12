# 03 MQTT

Spec: [MQTT 3.1.1 (OASIS)](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html). The packet example comes from `examples/mqtt_walkthrough.py`.

## The model

Clients connect to a broker. They publish messages to topics and subscribe to topics. Publisher and subscriber never talk to each other directly. For gateways this suits cellular links well: the gateway opens one outbound connection, so there is nothing to open inbound on the site firewall.

## Topics

Topics are slash-separated strings: `plant/line1/temp`.

| Wildcard | Meaning | Example |
|---|---|---|
| `+` | exactly one level | `plant/+/temp` matches `plant/line1/temp` |
| `#` | everything below, must be last | `plant/#` |

Wildcards are for subscribing only. You cannot publish to one.

## QoS

| QoS | Delivery | Cost |
|---|---|---|
| 0 | at most once, no acknowledgement | cheapest, can lose a message |
| 1 | at least once | duplicates are possible, so the consumer has to cope with them |
| 2 | exactly once | four-step handshake, slowest |

For periodic sensor values QoS 0 or 1 is usual. If you use QoS 1, include a timestamp or sequence number in the payload so that a duplicate can be recognised.

## Features worth knowing

- **Retained message.** The broker keeps the last retained message on a topic and gives it to every new subscriber. Good for "current status".
- **Last will.** A message the broker publishes for the client if the connection drops without a proper DISCONNECT. Combined with a retained "online" message it gives you a cheap online/offline indicator.
- **Keep alive.** If the broker hears nothing from the client for 1.5 times the keep-alive interval, it closes the connection. Pings keep an idle link alive.
- **Clean session.** In 3.1.1, `true` means the broker forgets the client's subscriptions and queued messages when it disconnects.
- **Client ID.** It must be unique per broker. If a second client connects with an ID that is already connected, the broker disconnects the first one (spec section 3.1.4). Two clients with the same ID will keep kicking each other off. On a weak link a client can also reconnect while the broker still thinks the old connection is alive, and then collides with itself. There is a write-up in [iiot-field-notes](https://github.com/pratik-kadam-automation/iiot-field-notes).

## One packet, by hand

A PUBLISH at QoS 0 of `23.5` to `plant/line1/temp`:

```
30 16 00 10 70 6C 61 6E 74 2F 6C 69 6E 65 31 2F 74 65 6D 70 32 33 2E 35
```

| Bytes | Meaning |
|---|---|
| `30` | PUBLISH, QoS 0, not retained |
| `16` | Remaining length = 22 |
| `00 10` | Topic length = 16 |
| `70 6C ... 70` | `plant/line1/temp` |
| `32 33 2E 35` | Payload `23.5` |

24 bytes for a 4 byte payload. A small JSON payload such as `{"v":23.5,"q":"good"}` brings the same message to 41 bytes. That is still small, but across many tags and many gateways on a metered SIM, payload design matters.

The remaining length uses 7 bits per byte, and the top bit means "another byte follows". The value 321 is encoded as `C1 02`.

## Habits

- Keep the topic hierarchy predictable (site / machine / kind), so subscriptions can use wildcards.
- Put a timestamp and a quality flag in the payload, not only the value.
- Do not put secrets or customer names in topics. They show up in logs.
- Use TLS 1.2 or newer. Some brokers and cloud services reject older versions, and the failure can look like random disconnects.
