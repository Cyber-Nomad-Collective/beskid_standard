# corelib_http

Bounded strict HTTP/1.1 framing, serialization, client exchange, and listener-backed server operations over `corelib_network` and Foundation I/O.

## Host

Every parsed and every serialized request must carry exactly one `Host` field line.
`Codec.ParseRequest` and `Codec.SerializeRequest` return `HttpError::MissingHost` when the
line is absent and `HttpError::InvalidHost` when there is more than one line or the value is
not empty and not `uri-host [ ":" port ]` (a bracketed IPv6 literal or a run of unreserved,
sub-delims, and percent-encoded octets; a decimal port in 0..65535). The check runs before
body framing, so no body is read or allocated. The serializer never adds a `Host` field.

`HttpServer.Receive` returns these errors and does not answer them. The application must
answer with status 400 and close the stream:

```beskid
server.Respond(stream, Types.EmptyResponse(400_i64, "Bad Request"), limits)?;
stream.Close()?;
```

## Message roles

`Codec.MessageEnd`, `Codec.ParseResponse`, and `Wire.ReadMessage` take a
`MessageRole` (`Request`, `Response`, `HeadResponse`) that selects the RFC 9112
section 6.3 framing rules:

- A response to `HEAD` and any `1xx`, `204`, or `304` response ends at the empty line after
  the header section. A `Content-Length` or `Transfer-Encoding` field in such a response is
  validated but does not frame a body. Octets after that line are `TrailingBytes`.
- A request with neither framing field has an empty body.
- A response with neither framing field that is not bodiless is
  `HttpError::CloseDelimitedBody`. This bounded client does not read close-delimited bodies.
- A `1xx` response is `HttpError::InterimResponse`. This bounded client reads exactly one
  message and does not continue to the final response.

`Client.Send` uses `HeadResponse` when the request method is `HEAD`. For a `HEAD` request
the server application responds with an empty body; the serialized `content-length: 0` is
permitted by RFC 9110 section 8.6.

`Response.status` is a checked integer in 100..599. Parsing and serialization reject any
other value with `HttpError::InvalidStatus`.

## Transport failures

`HttpError::Transport(cause)` carries the Foundation `TransferFailure` cause from `Core.IO`
unchanged. `IoError::ReadFailed(cause)` and `WriteFailed(cause)` map to `Transport(cause)`,
`InvalidRange` and `NoProgress` map to `Transport(TransferFailure::Unspecified)`, and
`UnexpectedEof(_)` maps to `HttpError::UnexpectedEof`.
