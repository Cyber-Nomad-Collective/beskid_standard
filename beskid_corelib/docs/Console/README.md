# Console and ANSI (`corelib_console`)

`corelib_console` provides terminal capability detection, ANSI escape builders (`Ansi.*`), styled text, and simple controls (`Console.Controls.*`). This page covers display-width layout, color handling, capability policy, and terminal modes.

## Ansi.Text: measuring and laying out terminal text

Escape sequences take no columns. Code points are measured with `CodePointWidth`: wide East Asian characters and emoji take 2 columns; combining marks, zero-width joiners, variation selectors, and controls take 0.

| Function | Behavior |
|----------|----------|
| `Strip(text)` | Removes CSI (colors, cursor moves), OSC (titles, hyperlinks; BEL or ST terminated), DCS/APC/PM/SOS strings, and two-byte ESC sequences. |
| `VisibleWidth(text)` | Columns occupied on screen. Use this instead of `String.Len` for alignment. |
| `Truncate(text, width, ellipsis)` | Cuts to `width` columns, appending `ellipsis` inside the width; never splits a wide character; appends an SGR reset when the kept text was styled. |
| `PadEnd`, `PadStart`, `Center(text, width)` | Space padding by columns; never truncates. |
| `Wrap(text, width)` | Word wrap by columns; keeps existing newlines, collapses runs of spaces, and hard-breaks words wider than `width`. |
| `CodePointWidth(cp)`, `DecodeAt(text, at)`, `EscapeLength(text, at)` | Building blocks for custom layout. |

```beskid
use Ansi.Text;

string cell = Text.PadEnd(Text.Truncate(name, 20, "..."), 20);
```

Widths are per code point, not per grapheme cluster: multi-code-point emoji sequences (family emoji, flags) can measure wider than a terminal draws them.

## Colors

`Ansi.Sgr.ForegroundArgsFor(model, r, g, b)` and `BackgroundArgsFor` produce SGR arguments for an explicit `ColorModel`, so output is deterministic and testable:

| Model | Foreground output |
|-------|-------------------|
| `TrueColor` | `38;2;r;g;b` |
| `Indexed256` | `38;5;n`, the nearest xterm cube color or gray-ramp step (`RgbTo256Index`) |
| `Basic16` | nearest of the 16 default colors: `30`-`37` or bright `90`-`97` (`RgbToBasicForeground`) |
| `Basic8` | nearest of the first 8 colors: `30`-`37` |

`ForegroundColorArgs` and `BackgroundColorArgs` do the same using the model probed from stdout. Channels are clamped to `0..=255`. Nearest-color matching uses RGB distance against the xterm default palette.

## Capability policy

`Console.Capabilities.FromEnvironment(env)` computes the color policy from a `TerminalEnvironment` value (TTY state plus `TERM`, `COLORTERM`, `NO_COLOR`, and `FORCE_COLOR`), without reading the process environment:

- `NO_COLOR` with a non-empty value disables color.
- `FORCE_COLOR` emits color even without a TTY; `0` or `false` disables instead; `2` raises the model to at least 256 colors and `3` to truecolor.
- `COLORTERM=truecolor` or `24bit`, or a `TERM` containing `direct` or `truecolor`, selects truecolor; a `TERM` containing `256color` selects 256 colors; anything else selects 16 colors.
- `TERM=dumb` disables color unless forced; output to a non-TTY is uncolored unless forced.

`ProbeEnvironment()` captures the real values and `ProbeStdout()` returns `FromEnvironment(ProbeEnvironment())`. `ShouldStripColor(caps)` and `EffectiveColorModel(caps)` interpret the result.

## Terminal modes: Ansi.Modes

Raw (ungated) sequences; wrap them in `Escape.WhenEnabled` when the stream may not be a terminal.

| Function | Sequence |
|----------|----------|
| `SynchronizedOutput(enable)` | `CSI ?2026 h/l`: paint a whole frame at once. |
| `BracketedPaste(enable)` | `CSI ?2004 h/l`: pasted text arrives between `CSI 200~` and `CSI 201~`. |
| `FocusReporting(enable)` | `CSI ?1004 h/l`: focus `CSI I`, blur `CSI O`. |
| `CursorShape(style)` | `CSI n SP q` for `CursorStyle` block, underline, or bar, blinking or steady. |
| `HyperlinkWithId(id, uri, label)` | OSC 8 link whose segments the terminal groups by `id`. |
| `SetClipboard(text)` | OSC 52 clipboard write request (base64 payload). |
| `Notify(message)` | OSC 9 desktop notification. |

## Controls

`Console.Controls.Panel` sizes its border from `Ansi.Text.VisibleWidth`, so styled or wide-character bodies and titles stay aligned.
