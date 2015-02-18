DZIENDOBRY
==========

_DZIENDOBRY_ is a simple but robust service discovery protocol. Service discovery is initiated by sending a specific UDP packet onto either port 5000, 6000 or 7000, and waiting for server's response. Particular services are identified by their UUID's. _DZIENDOBRY_ can also store a string associated with a given service, that will be included in the response.

The Protocol
------------

The protocol is very simple. Client initiates by sending a UDP broadcast packet to either port 5000, 6000 or 7000 (it's advisable to send on all three) with content (everything is in network byte order!):

```
byte[]  'DZIENDOBRY'
sequence of
        byte                  OptionType
        byte                  OptionLength
        byte[OptionLength]    OptionValue
```

Option 0 is "respond only if you have a service of particular UUID". OptionLength is 16, and OptionValue will be the binary representation of service's UUID. The server will respond only if it declares a service with this UUID.

Option 1 is "respond to another port". OptionValue (2 bytes) will code a network port that UDP response will arrive on.

Server, after deciding to respond, will respond with a UDP unicast response to IP address that send the request, and the same port from which it was send (barring Option 1 usage). It's format will be:

```
byte[] 'WITAMUPRZEJMIE'
sequence of
    byte    RecordLength
    byte[8] ServiceUUID
    byte[RecordLength-8] AdditionalServiceInfo
```

This will enumerate all services present on this server. Extra data can be specified by AdditionalServiceInfo field, but this is service-dependent.

See file COPYING for license information.
