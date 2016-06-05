# Warning
This is the development version of COR-Framework !!! Do not use this for production, this is version 5.0, you should switch to 4.0 branch for production release.


# COR-Framework-Python

New COR-Framework editition, with simplified messages, and standard for serialization, the messages will be serialized using Google Protocol Buffers, where permited serialization will not occur (sending objects within a runtime).

The new edition uses the concept of multiple communication drivers including but not limited to:
- Callback (within runtime) - no serialization
- Domain Socket (within system) - communication protocol is defined
- TCP/IP Socket (inter system) - communication protocol is defined

