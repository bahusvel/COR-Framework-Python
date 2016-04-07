# COR-Framework-Python

New COR-Framework editition, with simplified messages, and standard for serialization, the messages will be serialized using Google Protocol Buffers, where permited serialization will not occur (sending objects within a runtime).

The new edition uses the concept of multiple communication drivers including but not limited to:
- Callback (within runtime) - no serialization
- Domain Socket (within system) - communication protocol is defined
- TCP/IP Socket (inter system) - communication protocol is defined

