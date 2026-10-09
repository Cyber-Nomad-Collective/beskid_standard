# Core.Text.Csv

RFC 4180 records. Import `Core.Text.Csv`; types are `Csv.CsvRow` (`fields`) and `Csv.CsvError`.

| Function | Behavior |
|----------|----------|
| `Parse(text)`, `ParseWith(text, delimiter)` | Quoted fields with `""` escapes and embedded line breaks; LF or CRLF record ends; optional final line break; empty input gives no records. |
| `Format(rows)` | Commas and CRLF line endings. |
| `FormatWith(rows, delimiter, lineEnding)` | Custom delimiter byte and line ending. |
| `FormatField(field, delimiter)`, `Row(fields)` | Quote a single field only when needed; build a record. |

Errors carry byte offsets: `UnterminatedQuote` (where the field began) and `UnexpectedQuote` (a quote inside an unquoted field, or text after a closing quote).
