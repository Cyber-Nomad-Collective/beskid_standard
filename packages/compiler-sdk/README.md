# corelib_compiler_sdk

Typed Mod SDK facades under `Beskid.Compiler.*` for compiler meta projects.

## Generated surfaces

`src/Beskid/Compiler/{Query,Diagnostics,Emit,Process,Compilation}.bd` each combine:

1. **Generated** structural mirrors from `beskid_analysis` (via `beskid_ast_reflect_gen`), using `ReflectStub` for payloads where the Rust shape is not mapped field-for-field.
2. **Hand-maintained** version tokens and facade helpers at the bottom of each file.

**Syntax** is split for stack-friendly consumption:

- `src/Beskid/Compiler/Syntax.bd` — thin entry (`ReflectStub`, `pub mod …Nodes`, `SyntaxFacadeVersion`).
- `src/Beskid/Compiler/Syntax/Nodes.bd` — barrel that re-exports one module per AST node type.
- `src/Beskid/Compiler/Syntax/Nodes/*.bd` — one file per logical syntax node (from `beskid_analysis` `syntax/**` scan), with real fields where the mapping is straightforward (`string`, `bool`, `i64`, cross-references under `Beskid.Compiler.Syntax.Nodes.*`) and `Beskid.Compiler.Syntax.ReflectStub` for `Vec`/optional subtrees and other complex Rust shapes.

### Syntax node field names (generated)

Regeneration uses `beskid_ast_reflect_gen::syntax_nodes::emit_syntax_sdk` (see `crates/beskid_ast_reflect_gen/README.md`).

- **Struct fields:** Rust field identifiers are preserved; tuple-struct Rust fields use `field_0`, `field_1`, … (never `f0` / `f1`).
- **Enum tuple variants:** a single payload uses `payload`; multiple unnamed slots use `variant_field_0`, `variant_field_1`, …
- **Beskid keywords / keyword-prefix clashes:** names that match a Beskid reserved word, or start with one as the first snake segment (e.g. `contract_name`, `type_name`), are escaped as `_name` so they parse as normal identifiers.
- **Documentation:** each file begins with `///` lines listing the mirrored Rust path, optional one-line Rust `///` summary, and bullet lines for every `ReflectStub` field with a short reason (`Vec`, non-primitive `Option`, opaque Rust type, etc.).
- `src/Beskid/Compiler/Syntax/Nodes/_inventory.txt` — sorted type names (checked in tests) kept in sync with `ReflectSdkNodeKind` plus documented extras (`FieldKind`, `AssignOp`).

`src/Prelude.bd` is hand-maintained and only re-exports the modules above.

## Regenerating

From the **compiler** repository root (directory containing `crates/` and `corelib/`):

```bash
./corelib/packages/compiler-sdk/regen_mod_sdk_surfaces.sh
```

Equivalent manual invocation uses `cargo run -p beskid_ast_reflect_gen` with `--no-banner` and `--no-reflect-stub` when stitching into the checked-in files; see the script for exact allowlists.

After changing reflected Rust sources (`compiler_sdk_reflect.rs`, any `crates/beskid_analysis/src/syntax/**` AST struct or enum, `hir/item.rs`, or diagnostic enums), re-run the script and commit the updated `.bd` files (including `Syntax/Nodes/` and `tests/expected/syntax_nodes_inventory.txt` in `beskid_ast_reflect_gen` when the inventory changes).
