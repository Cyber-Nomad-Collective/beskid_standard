# Core.Json

`Core.Json` parses, builds, inspects, and serializes RFC 8259 JSON in plain Beskid.

## Values

```beskid
pub enum JsonValue {
    Null,
    Bool(bool value),
    Number(f64 value),
    Text(string value),
    List(JsonValue[] items),
    Object(string[] keys, JsonValue[] values),
}
```

Objects keep members in document order as parallel arrays. Duplicate keys survive parsing; lookups return the first match.

## Parsing

`Json.Parse(text) -> Result<JsonValue, JsonError>` accepts exactly one value with optional surrounding whitespace. Every `JsonError` variant carries the byte offset where parsing stopped:

| Variant | Cause |
|---------|-------|
| `UnexpectedEnd` | Input ended inside a value. |
| `UnexpectedCharacter` | Byte not valid here (missing comma or colon, bad literal). |
| `InvalidNumber` | Leading `+`, missing digits after `-`, `.`, or exponent. |
| `InvalidEscape` | Unknown `\x` or malformed `\uXXXX`. |
| `InvalidUnicode` | Lone or mismatched UTF-16 surrogate. |
| `ControlCharacter` | Raw byte below U+0020 inside a string. |
| `TrailingCharacters` | Anything after the top-level value. |
| `TooDeep` | More than `Json.MaxDepth()` (128) nested arrays/objects. |

Numbers are stored as f64 (see [Number](./Text/Number.md) for precision). Escapes, including surrogate pairs, decode to UTF-8.

## Reading

| Function | Returns |
|----------|---------|
| `Get(object, key)` | `Option<JsonValue>` for the first member named `key`. |
| `At(list, index)` | `Option<JsonValue>`; `None` when out of range. |
| `Length(value)` | Element or member count, else `0`. |
| `Keys(object)` | Member names in order. |
| `IsNull`, `AsBool`, `AsNumber`, `AsText` | Typed payload access returning `Option`. |

## Building and writing

```beskid
use Core.Json;
use Core.Json.JsonValue;

mut JsonValue doc = Json.EmptyObject();
doc = Json.With(doc, "name", JsonValue::Text("beskid"));
doc = Json.With(doc, "tags", Json.Push(Json.EmptyList(), JsonValue::Text("lang")));
string compact = Json.Stringify(doc); // {"name":"beskid","tags":["lang"]}
string indented = Json.Pretty(doc);   // two-space indentation
```

`With` replaces the first existing member in place or appends a new one. `Quote(text)` returns a single escaped JSON string literal. Non-finite numbers serialize as `null`.
