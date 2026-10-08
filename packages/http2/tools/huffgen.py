#!/usr/bin/env python3
"""Generates the HPACK Huffman (RFC 7541 Appendix B) nibble decoding automaton in
src/Http2/HpackHuffman.bd between the GENERATED HuffmanFsm markers.

States are the internal nodes of the code tree (root = 0). For each state and 4-bit input,
the entry packs: next state (bits 0-7), EMIT (bit 8), EOS (bit 9), symbol (bits 10-17),
stored as 5 characters 'A'..'P' in a string literal.
Codes are at least 5 bits long, so one nibble completes at most one symbol.
`StateInfo` packs the depth of a state (bits since the last symbol, bits 0-7) and whether
the path from the root is all ones (bit 8): a string may end only in an all-ones state of
depth <= 7 (RFC 7541 section 5.2).
"""
import re, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "src/Http2/HpackHuffman.bd"
text = SRC.read_text()

def array(name):
    body = text[text.index(name + "() {"):]
    body = body[body.index("return [") + 8: body.index("];")]
    return [int(v.split("_")[0], 0) for v in re.findall(r"0x[0-9a-fA-F]+_u\d+|\d+_u\d+|\d+_i64", body)]

codes = array("u32[] Codes")
lengths = array("u8[] Lengths")
assert len(codes) == 257 and len(lengths) == 257

# Build the tree: node -> [child0, child1]; leaves are ("sym", s).
nodes = [[None, None]]
info = [(0, True)]  # depth, all ones
for sym in range(257):
    code, length = codes[sym], lengths[sym]
    n = 0
    for k in range(length - 1, -1, -1):
        bit = (code >> k) & 1
        if k == 0:
            assert nodes[n][bit] is None
            nodes[n][bit] = ("sym", sym)
        else:
            child = nodes[n][bit]
            if child is None:
                nodes.append([None, None])
                d, ones = info[n]
                info.append((d + 1, ones and bit == 1))
                child = len(nodes) - 1
                nodes[n][bit] = child
            assert not isinstance(child, tuple)
            n = child
assert len(nodes) == 256, len(nodes)

table = []
for state in range(256):
    for nib in range(16):
        n, emit, eos, sym = state, 0, 0, 0
        for k in range(3, -1, -1):
            bit = (nib >> k) & 1
            nxt = nodes[n][bit]
            if isinstance(nxt, tuple):
                if nxt[1] == 256:
                    eos = 1
                    n = 0
                    break
                assert emit == 0
                emit, sym, n = 1, nxt[1], 0
            else:
                n = nxt
        table.append(n | (emit << 8) | (eos << 9) | (sym << 16))

def rows(values, per=16):
    out = []
    for i in range(0, len(values), per):
        out.append("        " + ", ".join(f"{v}_i64" for v in values[i:i + per]) + ",")
    return "\n".join(out)

def packed(e):
    # 18-bit entry: next | EMIT << 8 | EOS << 9 | symbol << 10, as 5 base-16 digits 'A'..'P'
    v = (e & 255) | (((e >> 8) & 3) << 8) | (((e >> 16) & 255) << 10)
    return "".join(chr(65 + ((v >> (4 * k)) & 15)) for k in range(4, -1, -1))

fsm = "".join(packed(e) for e in table)

gen = f"""// BEGIN GENERATED HuffmanFsm (tools/huffgen.py)
/// Nibble automaton, 5 characters per entry (state * 16 + nibble), base-16 digits 'A'..'P'
/// of: next state | EMIT << 8 | EOS << 9 | symbol << 10. A string literal compiles in
/// negligible time; a 4096-element array literal costs minutes per test (COMPILER-GAPS PERF1).
string FsmTable() {{ return "{fsm}"; }}

/// Per state: depth since the last symbol | all-ones path << 8.
i64[] StateInfo() {{
    return [
{rows([d | (int(o) << 8) for d, o in info])}
    ];
}}
// END GENERATED HuffmanFsm"""

start = text.find("// BEGIN GENERATED HuffmanFsm")
if start >= 0:
    end = text.index("// END GENERATED HuffmanFsm") + len("// END GENERATED HuffmanFsm")
    text = text[:start] + gen + text[end:]
else:
    anchor = "/// Decoding tables built once"
    text = text.replace(anchor, gen + "\n\n" + anchor, 1)
SRC.write_text(text)
print("states", len(nodes), "entries", len(table))
