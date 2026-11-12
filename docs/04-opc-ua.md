# 04 OPC UA

Spec: [OPC Foundation reference](https://reference.opcfoundation.org/). Part 4 covers services, Part 6 covers encodings and data type IDs.

## How it differs from Modbus

Modbus gives you numbered registers and you have to know what they mean. OPC UA gives you a tree of named, typed nodes that you can browse, so a client can discover what the server offers. The data type is part of the answer, so there is no word-order guessing.

The default port for `opc.tcp://` is 4840, though many servers use something else.

## Nodes

Every node has a NodeId: a namespace index plus an identifier.

| Form | Example |
|---|---|
| Numeric | `ns=2;i=1234` |
| String | `ns=2;s=Boiler.Temperature` |

Two well-known nodes in namespace 0: the Root folder is `i=84` and the Objects folder is `i=85`. Browsing from Objects is how you find what a server offers. A variable node has a Value attribute (attribute ID 13), plus a status code and timestamps.

Check the **status code**, not only the value. A Good status code is 0. A value can be present and still be Bad or Uncertain.

## Reading versus subscribing

- **Read**: ask once, get the current value.
- **Subscription**: create a subscription with a publishing interval, add monitored items, and the server pushes changes. For each item you set a sampling interval and, for analog values, an optional deadband so noise does not generate traffic.

For anything you watch continuously, subscriptions are the point of using OPC UA. Polling it like Modbus throws that away.

## Security

| Setting | Options |
|---|---|
| Message security mode | None, Sign, SignAndEncrypt |
| Security policy | Basic256Sha256, Aes128_Sha256_RsaOaep, Aes256_Sha256_RsaPss. Older ones (Basic128Rsa15, Basic256) are deprecated |
| User authentication | Anonymous, username and password, X.509 certificate |

With security on, each side has an application certificate, and each side has to **trust the other's**. In practice:

1. Client connects. The server rejects the unknown client certificate and stores it in a "rejected" folder.
2. An engineer moves that certificate to the server's "trusted" folder.
3. Client connects again, and now the client must also trust the server's certificate.

Self-signed certificates are common on the plant floor. The application URI inside the certificate must match the application's own URI, otherwise the connection fails even though the certificate is trusted.

None / None is fine for a bench test and a poor idea on a production network.

## Built-in data types

IDs in namespace 0. Binary encoding is little-endian.

| ID | Type | ID | Type |
|---|---|---|---|
| 1 | Boolean | 8 | Int64 |
| 2 | SByte | 9 | UInt64 |
| 3 | Byte | 10 | Float |
| 4 | Int16 | 11 | Double |
| 5 | UInt16 | 12 | String |
| 6 | Int32 | 13 | DateTime |
| 7 | UInt32 | | |

## When I would pick it

Good fit: the machine already has an OPC UA server (many injection moulding machines and newer PLCs do), you need discovery, or you need subscriptions. Poor fit: a small device that only speaks Modbus, where adding a layer gains nothing.

Tools: UaExpert is the usual client for browsing and checking a server before writing any code.
