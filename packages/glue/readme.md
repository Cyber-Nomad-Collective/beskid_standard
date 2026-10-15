# corelib_glue

The Glue package supplies the provisional stdio bridge protocol: the canonical binary envelope and value codec, an incremental nonblocking process pump, and a cooperative session with bounded pending requests and checked shutdown. It uses the existing process, IO, fiber, channel, and deadline services.

This package is not the delivered Rust Glue call path. Beskid 0.6 calls Rust owners in process through the checked C ABI: `[Extern]` contracts, `[GlueHandle]` types and `[RustOwner]` mappings, with admission records on the owner and consumer images. The stdio bridge is specified separately as a provisional capability and has no 0.6 delivery obligation.

Library names and wire digests describe a protocol connection; they do not authorize descriptors, callbacks, or opaque tokens.
