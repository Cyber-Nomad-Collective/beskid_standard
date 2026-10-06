# corelib_glue

The Glue package supplies the canonical binary envelope and value codec, an incremental nonblocking process pump, and a cooperative session with bounded pending requests and checked shutdown. It uses the existing process, IO, fiber, channel, and deadline services.

Native ownership is admitted separately by the actual compiled image and one canonical runtime provider. Library names and wire digests describe a protocol connection; they do not authorize descriptors, callbacks, or opaque tokens.

The package retains the Glue, GlueImport, and GlueExport annotations and the required TypeMapping, SymbolEmission, LinkArgs, SignatureReader, SignatureWriter, ToolchainProbe, and StdioBridge Mod contracts. Contract declaration alone is not generated backend delivery. Rust manual/generated parity and installed native qualification remain release gates; .NET is stretch scope.
