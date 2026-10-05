#!/usr/bin/env python3
"""Generates the straight-line CLIF kernels of protocols/crypto.

Each kernel is a Beskid function whose body is one `clif { ... }` block. The script
rewrites the region between `// BEGIN GENERATED <name>` and `// END GENERATED <name>`
in the target source file. Run from any directory: `python3 tools/clifgen.py`.
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "Crypto")


class Block:
    """Accumulates CLIF lines with fresh SSA names and cached constants."""

    def __init__(self):
        self.lines = []
        self.counter = 0
        self.consts = {}

    def fresh(self, stem="v"):
        self.counter += 1
        return "%%%s%d" % (stem, self.counter)

    def op(self, text, stem="v"):
        name = self.fresh(stem)
        self.lines.append("%s = %s" % (name, text))
        return name

    def raw(self, text):
        self.lines.append(text)

    def const(self, ty, value):
        key = (ty, value)
        if key not in self.consts:
            bits = {"i8": 8, "i16": 16, "i32": 32, "i64": 64}[ty]
            value &= (1 << bits) - 1
            if value >= 1 << (bits - 1):
                value -= 1 << bits
            self.consts[key] = self.op("iconst.%s %d" % (ty, value), "c")
        return self.consts[key]

    def render(self, indent="        "):
        return "\n".join(indent + line for line in self.lines)


def function(signature, block, doc):
    body = block.render()
    return "%s\n%s {\n    return clif {\n%s\n    };\n}\n" % (doc, signature, body)


def replace_region(filename, name, text):
    path = os.path.join(ROOT, filename)
    with open(path) as handle:
        source = handle.read()
    begin = "// BEGIN GENERATED %s (tools/clifgen.py)\n" % name
    end = "// END GENERATED %s\n" % name
    pattern = re.compile(re.escape(begin) + ".*?" + re.escape(end), re.S)
    if not pattern.search(source):
        sys.exit("missing region %s in %s" % (name, filename))
    source = pattern.sub(lambda _: begin + text + end, source)
    with open(path, "w") as handle:
        handle.write(source)


# ---------------------------------------------------------------- SHA-2

SHA256_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

SHA512_K = [
    0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc, 0x3956c25bf348b538,
    0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118, 0xd807aa98a3030242, 0x12835b0145706fbe,
    0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2, 0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235,
    0xc19bf174cf692694, 0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5, 0x983e5152ee66dfab,
    0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4, 0xc6e00bf33da88fc2, 0xd5a79147930aa725,
    0x06ca6351e003826f, 0x142929670a0e6e70, 0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed,
    0x53380d139d95b3df, 0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30, 0xd192e819d6ef5218,
    0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8, 0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
    0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8, 0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373,
    0x682e6ff3d6b2b8a3, 0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b, 0xca273eceea26619c,
    0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178, 0x06f067aa72176fba, 0x0a637dc5a2c898a6,
    0x113f9804bef90dae, 0x1b710b35131c471b, 0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc,
    0x431d67c49c100d4c, 0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817,
]


def sha2_compress(ty, k, word_bytes, sigma0, sigma1, big0, big1, cursor):
    """One SHA-2 compression. Parameters: %0 state words, %1 data bytes, %2 the i64[] meta
    array whose element `cursor` is the block offset. Yields the offset of the next block."""
    b = Block()
    hp = b.op("payload %0", "hp")
    dp = b.op("payload %1", "dp")
    mp = b.op("payload %2", "mp")
    pos = b.op("load.i64 %s+%d" % (mp, cursor * 8), "pos")
    base = b.op("iadd %s, %s" % (dp, pos), "base")

    def rotr(x, n):
        return b.op("rotr %s, %s" % (x, b.const(ty, n)))

    def shr(x, n):
        return b.op("ushr %s, %s" % (x, b.const(ty, n)))

    def xor3(x, y, z):
        return b.op("bxor %s, %s" % (b.op("bxor %s, %s" % (x, y)), z))

    w = []
    for t in range(16):
        raw = b.op("load.%s %s+%d" % (ty, base, t * word_bytes))
        w.append(b.op("bswap %s" % raw, "w"))

    def schedule(t):
        # Computed just before round t so only a 16-word window is live.
        w15, w2 = w[t - 15], w[t - 2]
        s0 = xor3(rotr(w15, sigma0[0]), rotr(w15, sigma0[1]), shr(w15, sigma0[2]))
        s1 = xor3(rotr(w2, sigma1[0]), rotr(w2, sigma1[1]), shr(w2, sigma1[2]))
        acc = b.op("iadd %s, %s" % (w[t - 16], s0))
        acc = b.op("iadd %s, %s" % (acc, w[t - 7]))
        w.append(b.op("iadd %s, %s" % (acc, s1), "w"))
    h = [b.op("load.%s %s+%d" % (ty, hp, i * word_bytes), "h") for i in range(8)]
    a, bb, c, d, e, f, g, hh = h
    for t in range(len(k)):
        if t >= 16:
            schedule(t)
        s1 = xor3(rotr(e, big1[0]), rotr(e, big1[1]), rotr(e, big1[2]))
        ch = b.op("bitselect %s, %s, %s" % (e, f, g))
        t1 = b.op("iadd %s, %s" % (hh, s1))
        t1 = b.op("iadd %s, %s" % (t1, ch))
        t1 = b.op("iadd %s, %s" % (t1, b.const(ty, k[t])))
        t1 = b.op("iadd %s, %s" % (t1, w[t]))
        s0 = xor3(rotr(a, big0[0]), rotr(a, big0[1]), rotr(a, big0[2]))
        # Maj(a, b, c) = (a ^ b) ? c : b, bit by bit.
        maj = b.op("bitselect %s, %s, %s" % (b.op("bxor %s, %s" % (a, bb)), c, bb))
        t2 = b.op("iadd %s, %s" % (s0, maj))
        hh, g, f = g, f, e
        e = b.op("iadd %s, %s" % (d, t1), "e")
        d, c, bb = c, bb, a
        a = b.op("iadd %s, %s" % (t1, t2), "a")
    for i, v in enumerate([a, bb, c, d, e, f, g, hh]):
        s = b.op("iadd %s, %s" % (h[i], v))
        b.raw("store %s, %s+%d" % (s, hp, i * word_bytes))
    b.raw("return %s" % b.op("iadd %s, %s" % (pos, b.const("i64", word_bytes * 16)), "next"))
    return b


def looped(signature, doc, cond, block, assign):
    """A Beskid function that runs `block` inline while `cond` holds, so the per-call cost
    of array parameters (GC root registration) is paid once per call, not once per block.
    The function returns i64: inside a loop the block takes its type from the function's
    return type (COMPILER-GAPS C53-1)."""
    return "%s\n%s {\n    while %s {\n        i64 next = clif {\n%s\n        };\n        %s = next;\n    }\n    return 0_i64;\n}\n" % (
        doc, signature, cond, block.render("            "), assign)


def gen_sha():
    b = sha2_compress("i32", SHA256_K, 4, (7, 18, 3), (17, 19, 10), (2, 13, 22), (6, 11, 25), 3)
    replace_region("Sha256.bd", "Sha256Block", looped(
        "i64 CompressBlocks(u32[] h, u8[] data, i64[] meta)",
        "/// SHA-256 compressions (FIPS 180-4 6.2.2) of the 64-byte blocks of `data` from offset\n"
        "/// `meta[3]` up to `meta[4]`. Precondition: the range is in bounds, a multiple of 64 long,\n"
        "/// and `h` has 8 words; the block does not check.",
        "meta[3] < meta[4]", b, "meta[3]"))
    b = sha2_compress("i64", SHA512_K, 8, (1, 8, 7), (19, 61, 6), (28, 34, 39), (14, 18, 41), 4)
    replace_region("Sha512.bd", "Sha512Block", looped(
        "i64 CompressBlocks(i64[] h, u8[] data, i64[] meta)",
        "/// SHA-512 compressions (FIPS 180-4 6.4.2) of the 128-byte blocks of `data` from offset\n"
        "/// `meta[4]` up to `meta[5]`. Precondition: the range is in bounds, a multiple of 128\n"
        "/// long, and `h` has 8 words; the block does not check.",
        "meta[4] < meta[5]", b, "meta[4]"))


GENERATORS = {"sha": gen_sha}

if __name__ == "__main__":
    names = sys.argv[1:] or sorted(GENERATORS)
    for name in names:
        GENERATORS[name]()
