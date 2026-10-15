# Core.Time.Calendar

`Core.Time.Calendar` is constant-time proleptic Gregorian arithmetic over `Core.Time.Date`, plus RFC 3339 parsing and formatting of `Instant` values. Day numbers count days since 1970-01-01 and may be negative. Everything is UTC.

## Dates

| Function | Behavior |
|----------|----------|
| `DaysFromCivil(year, month, day)` / `CivilFromDays(days)` / `ToDays(date)` | Exact conversions for any year (Hinnant's algorithms). |
| `IsLeapYear(year)`, `DaysInMonth(year, month)`, `IsValidDate(y, m, d)` | `DaysInMonth` returns `0` for an invalid month. |
| `IsoWeekday(date)` | 1 = Monday through 7 = Sunday. |
| `DayOfYear(date)` | 1-based ordinal. |
| `AddDays`, `AddMonths`, `AddYears` | Month and year steps clamp to the end of the target month: January 31 + 1 month is February 28 or 29. |
| `DaysBetween(earlier, later)`, `CompareDates(a, b)` | Signed difference; `-1`/`0`/`1`. |
| `FormatDate(date)` | `YYYY-MM-DD`; years beyond 0-9999 use signed expanded form (`+12345-01-02`, `-0044-03-15`). |
| `ParseDate(text)` | Strict `YYYY-MM-DD`. |

## Instants

`FormatInstant(instant)` writes `2026-10-06T12:30:00Z`, adding `.250` for whole milliseconds or nine digits otherwise.

`ParseInstant(text)` accepts RFC 3339 date-times:

- date and time separated by `T`, `t`, or a space;
- optional 1-9 fraction digits;
- `Z`, `z`, or a numeric `+HH:MM` / `-HH:MM` offset, applied to produce UTC;
- a bare `YYYY-MM-DD`, meaning midnight UTC.

Failures use `Core.Time.TimeError`: `InvalidFormat(input)` for structure, `OutOfRange(field)` naming `month`, `day`, `hour`, `minute`, `second`, or `offset`. Leap seconds (`:60`) are rejected.

```beskid
use Core.Time.Calendar;

match Calendar.ParseInstant("2026-10-06T14:30:00+02:00") {
    Result::Ok(instant) => Output.WriteLine(Calendar.FormatInstant(instant)), // 2026-10-06T12:30:00Z
    Result::Error(_) => Output.WriteLine("invalid timestamp"),
};
```

Time zones beyond fixed offsets are out of scope until a time-zone database policy exists.
