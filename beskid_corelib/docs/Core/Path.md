`Core.Path` provides POSIX-oriented path helpers using **`Core.String`** and **`__str_slice`**.

## Functions

| Function | Behavior |
|----------|----------|
| `Combine(string left, string right)` | If `left` is empty returns `right`; if `right` is empty returns `left`; otherwise **`left + "/" + right`**. |
| `FileName(string path)` | Returns the segment after the final **`/`**, or the whole path when no separator is present. |
| `Extension(string path)` | Returns the substring after the first **`.`** in the file name, or **`""`**. |
| `IsAbsolute(string path)` | **`true`** when the path begins with **`/`** (POSIX v1). |
| `IsEmpty(string path)` | **`true`** when `path == ""`**. |

## Usage examples

### Combine

```beskid
let config_dir = Path.Combine("/etc", "myapp");     // "/etc/myapp"
let relative   = Path.Combine("src", "lib");        // "src/lib"
let just_right = Path.Combine("", "fallback.txt");  // "fallback.txt"
let just_left  = Path.Combine("/root", "");         // "/root"
```

### FileName + Extension extraction

```beskid
let path = "/var/log/app.log";
let name = Path.FileName(path);       // "app.log"
let ext  = Path.Extension(path);      // "log"

let no_ext = Path.Extension("Makefile");   // ""
let dotfile = Path.FileName(".hidden");    // ".hidden"
let dotfile_ext = Path.Extension(".hidden"); // "hidden"
```

### IsAbsolute guard

```beskid
let path = get_user_input();
if Path.IsAbsolute(path) {
    // Reject for security: only relative paths allowed
    return Result.Err(FsError.AccessDenied);
};
let safe = Path.Combine("/srv/data", path);
```

## Gotchas

- **POSIX-only** — only forward-slash (`/`) is recognised as a separator. Windows-style backslash paths (`C:\foo`) are not split correctly and `IsAbsolute` returns `false` for them.
- **`Combine` does not normalise** — `Combine("/a", "../b")` produces `"/a/../b"`. Use `Core.Path.Lexical` below for normalization.

## Core.Path.Lexical

Purely textual operations on `/`-separated paths; nothing touches the filesystem, so `..` is resolved against the preceding text even when a symbolic link would resolve differently.

| Function | Behavior |
|----------|----------|
| `Normalize(path)` | Collapses `//`, drops `.`, resolves `..`. Rooted paths never climb above `/`; relative paths keep leading `..`. `a/..` gives `.`. |
| `JoinAll(parts)` | Joins and normalizes; a rooted part discards the parts before it. |
| `Segments(path)` | Non-empty components, without `.`. |
| `Relative(from, to)` | `Option<string>` path from directory `from` to `to`; `None` when only one is rooted. |
| `Parent(path)`, `Stem(path)` | `/a/b` gives `/a`; `archive.tar.gz` gives `archive.tar`. |
| `IsRooted(path)`, `ToForwardSlashes(path)` | Leading `/` test; `\` to `/` conversion for Windows-style input. |

```beskid
use Core.Path.Lexical;

string full = Lexical.JoinAll(["/srv/app", "static", "../uploads/./a.png"]); // /srv/app/uploads/a.png
```

