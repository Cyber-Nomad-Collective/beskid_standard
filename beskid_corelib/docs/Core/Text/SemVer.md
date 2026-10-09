# Core.Text.SemVer

Semantic Versioning 2.0.0. Types live in the module: import `Core.Text.SemVer` and write `SemVer.Version`, `SemVer.SemVerError`.

| Function | Behavior |
|----------|----------|
| `Parse(text)` | `MAJOR.MINOR.PATCH[-prerelease][+build]`; rejects leading zeros, empty identifiers, and a leading `v`. |
| `Format(version)`, `Of(major, minor, patch)` | Canonical text; release constructor. |
| `Compare(a, b)` | Specification precedence (`-1`/`0`/`1`); build metadata ignored. |
| `IsPrerelease`, `BumpMajor`, `BumpMinor`, `BumpPatch` | `BumpPatch` of a prerelease releases it (`1.4.2-rc.1` gives `1.4.2`). |
| `Satisfies(version, requirement)` | `Result<bool, SemVerError>`. |

Requirement syntax: `=`, `>`, `>=`, `<`, `<=`, caret (`^1.2.3` allows `<2.0.0`; `^0.2.3` allows `<0.3.0`; `^0.0.3` allows `<0.0.4`), tilde (`~1.2.3` allows `<1.3.0`), partial versions as ranges (`1.2` means `>=1.2.0 <1.3.0`), wildcards (`1.x`, `*`), spaces for AND, and `||` for OR. A prerelease version satisfies only a comparator set that names a prerelease of the same `MAJOR.MINOR.PATCH` (npm semantics), so `^1.2.3` never selects `2.0.0-rc.1`.

```beskid
bool ok = match SemVer.Satisfies(version, ">=0.5.2 <0.6.0") {
    Result::Ok(v) => v,
    Result::Error(_) => false,
};
```
