#!/usr/bin/env python3
"""Generates the straight-line CLIF kernels of protocols/crypto.

Each kernel is a Beskid function whose body is one `clif { ... }` block. The script
rewrites the region between `// BEGIN GENERATED <name>` and `// END GENERATED <name>`
in the target source file. Run from any directory: `python3 tools/clifgen.py`.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    nxt = b.op("iadd %s, %s" % (pos, b.const("i64", word_bytes * 16)), "next")
    b.raw("store %s, %s+%d" % (nxt, mp, cursor * 8))
    b.raw("return %s" % nxt)
    return b


def looped(signature, doc, cond, block, assign=None):
    """A Beskid function that runs `block` inline while `cond` holds, so the per-call cost
    of array parameters (GC root registration) is paid once per call, not once per block.
    The block advances its own cursor with a payload store: a Beskid store into an `i64[]`
    calls the runtime write barrier (COMPILER-GAPS C53-2). The function returns i64: inside
    a loop the block takes its type from the function's return type (COMPILER-GAPS C53-1)."""
    return "%s\n%s {\n    mut i64 last = 0_i64;\n    while %s {\n        last = clif {\n%s\n        };\n    }\n    return last;\n}\n" % (
        doc, signature, cond, block.render("            "))


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


# ---------------------------------------------------------------- ChaCha20 / Poly1305


def lane_mask(indices):
    return "[" + " ".join(str(i) for i in indices) + "]"


ROT16 = lane_mask([j * 4 + k for j in range(4) for k in (2, 3, 0, 1)])
ROT8 = lane_mask([j * 4 + k for j in range(4) for k in (3, 0, 1, 2)])
UNPACK_LO32 = lane_mask([0, 1, 2, 3, 16, 17, 18, 19, 4, 5, 6, 7, 20, 21, 22, 23])
UNPACK_HI32 = lane_mask([8, 9, 10, 11, 24, 25, 26, 27, 12, 13, 14, 15, 28, 29, 30, 31])
UNPACK_LO64 = lane_mask(list(range(0, 8)) + list(range(16, 24)))
UNPACK_HI64 = lane_mask(list(range(8, 16)) + list(range(24, 32)))


def chacha4():
    """Four ChaCha20 blocks (RFC 8439 2.3) in i32x4 lanes, XORed into the output.
    %0 state u32[20] (words 16..20 = 0, 1, 2, 3), %1 input, %2 output, %3 meta i64[]:
    meta[0] input offset, meta[1] output offset minus input offset. Advances the counter
    word by 4 and yields the next input offset."""
    b = Block()
    sp = b.op("payload %0", "sp")
    ip = b.op("payload %1", "ip")
    op = b.op("payload %2", "op")
    mp = b.op("payload %3", "mp")
    pos = b.op("load.i64 %s" % mp, "pos")
    delta = b.op("load.i64 %s+8" % mp, "delta")
    src = b.op("iadd %s, %s" % (ip, pos), "src")
    dst0 = b.op("iadd %s, %s" % (op, pos), "dst")
    dst = b.op("iadd %s, %s" % (dst0, delta), "dst")
    lanes = b.op("load.i32x4 %s+64" % sp, "lanes")

    def initial(i):
        word = b.op("load.i32 %s+%d" % (sp, 4 * i))
        v = b.op("splat.i32x4 %s" % word, "x")
        if i == 12:
            v = b.op("iadd %s, %s" % (v, lanes), "x")
        return v

    x = [initial(i) for i in range(16)]
    c12 = b.const("i32", 12)
    c20 = b.const("i32", 20)
    c7 = b.const("i32", 7)
    c25 = b.const("i32", 25)

    def rot_bytes(v, mask):
        bytes_ = b.op("bitcast.i8x16 little %s" % v)
        shuffled = b.op("shuffle %s, %s, %s" % (bytes_, bytes_, mask))
        return b.op("bitcast.i32x4 little %s" % shuffled)

    def rot_shift(v, left, right):
        return b.op("bor %s, %s" % (b.op("ishl %s, %s" % (v, left)), b.op("ushr %s, %s" % (v, right))))

    def qr(a, bb, c, d):
        x[a] = b.op("iadd %s, %s" % (x[a], x[bb]))
        x[d] = rot_bytes(b.op("bxor %s, %s" % (x[d], x[a])), ROT16)
        x[c] = b.op("iadd %s, %s" % (x[c], x[d]))
        x[bb] = rot_shift(b.op("bxor %s, %s" % (x[bb], x[c])), c12, c20)
        x[a] = b.op("iadd %s, %s" % (x[a], x[bb]))
        x[d] = rot_bytes(b.op("bxor %s, %s" % (x[d], x[a])), ROT8)
        x[c] = b.op("iadd %s, %s" % (x[c], x[d]))
        x[bb] = rot_shift(b.op("bxor %s, %s" % (x[bb], x[c])), c7, c25)

    for _ in range(10):
        qr(0, 4, 8, 12); qr(1, 5, 9, 13); qr(2, 6, 10, 14); qr(3, 7, 11, 15)
        qr(0, 5, 10, 15); qr(1, 6, 11, 12); qr(2, 7, 8, 13); qr(3, 4, 9, 14)
    y = [b.op("iadd %s, %s" % (x[i], initial(i)), "y") for i in range(16)]

    def shuf(u, v, mask):
        ub = b.op("bitcast.i8x16 little %s" % u)
        vb = b.op("bitcast.i8x16 little %s" % v)
        return b.op("shuffle %s, %s, %s" % (ub, vb, mask))

    def as32(v):
        return b.op("bitcast.i32x4 little %s" % v)

    for g in range(4):
        a, bb, c, d = y[4 * g:4 * g + 4]
        t0 = as32(shuf(a, bb, UNPACK_LO32))
        t1 = as32(shuf(c, d, UNPACK_LO32))
        t2 = as32(shuf(a, bb, UNPACK_HI32))
        t3 = as32(shuf(c, d, UNPACK_HI32))
        blocks = [shuf(t0, t1, UNPACK_LO64), shuf(t0, t1, UNPACK_HI64),
                  shuf(t2, t3, UNPACK_LO64), shuf(t2, t3, UNPACK_HI64)]
        for j, ks in enumerate(blocks):
            offset = 64 * j + 16 * g
            data = b.op("load.i8x16 %s+%d" % (src, offset))
            b.raw("store %s, %s+%d" % (b.op("bxor %s, %s" % (data, ks)), dst, offset))
    counter = b.op("load.i32 %s+48" % sp)
    b.raw("store %s, %s+48" % (b.op("iadd %s, %s" % (counter, b.const("i32", 4))), sp))
    nxt = b.op("iadd %s, %s" % (pos, b.const("i64", 256)), "next")
    b.raw("store %s, %s" % (nxt, mp))
    b.raw("return %s" % nxt)
    return b


def chacha1():
    """One ChaCha20 keystream block for the counter in word 12 of %0 into %1[0, 64)."""
    b = Block()
    sp = b.op("payload %0", "sp")
    op = b.op("payload %1", "op")
    s = [b.op("load.i32 %s+%d" % (sp, 4 * i), "s") for i in range(16)]
    x = list(s)
    rot = {n: b.const("i32", n) for n in (16, 12, 8, 7)}

    def qr(a, bb, c, d):
        for (p, q, r, n) in ((a, bb, d, 16), (c, d, bb, 12), (a, bb, d, 8), (c, d, bb, 7)):
            x[p] = b.op("iadd %s, %s" % (x[p], x[q]))
            x[r] = b.op("rotl %s, %s" % (b.op("bxor %s, %s" % (x[r], x[p])), rot[n]))

    for _ in range(10):
        qr(0, 4, 8, 12); qr(1, 5, 9, 13); qr(2, 6, 10, 14); qr(3, 7, 11, 15)
        qr(0, 5, 10, 15); qr(1, 6, 11, 12); qr(2, 7, 8, 13); qr(3, 4, 9, 14)
    for i in range(16):
        b.raw("store %s, %s+%d" % (b.op("iadd %s, %s" % (x[i], s[i])), op, 4 * i))
    b.raw("return %s" % b.const("i64", 0))
    return b


def poly1305_blocks():
    """Poly1305 in radix 2^64 (as OpenSSL poly1305.c with 128-bit products) over the 16-byte
    blocks of %2 from meta[2] to meta[3]. %0 r = [r0, r1, r1 + (r1 >> 2)], %1 h = [h0, h1, h2],
    %3 meta i64[]; meta[4] is the 2^128 pad bit (1 for full blocks, 0 for the final one)."""
    b = Block()
    rp = b.op("payload %0", "rp")
    hp = b.op("payload %1", "hp")
    dp = b.op("payload %2", "dp")
    mp = b.op("payload %3", "mp")
    pos = b.op("load.i64 %s+16" % mp, "pos")
    padbit = b.op("load.i64 %s+32" % mp, "pad")
    src = b.op("iadd %s, %s" % (dp, pos), "src")
    r0, r1, s1 = [b.op("load.i64 %s+%d" % (rp, 8 * i), "r") for i in range(3)]
    h0, h1, h2 = [b.op("load.i64 %s+%d" % (hp, 8 * i), "h") for i in range(3)]
    zero = b.const("i64", 0)

    def add(x, y):
        out, carry = b.fresh("s"), b.fresh("c")
        b.raw("%s, %s = uadd_overflow %s, %s" % (out, carry, x, y))
        return out, carry

    def addc(x, y, cin):
        # uadd_overflow_cin has no x64 lowering in Cranelift 0.136 (COMPILER-GAPS C53-3).
        partial, c1 = add(x, y)
        out, c2 = add(partial, b.op("uextend.i64 %s" % cin))
        return out, b.op("bor %s, %s" % (c1, c2))

    def ext(carry):
        return b.op("uextend.i64 %s" % carry)

    def mul(x, y):
        return b.op("imul %s, %s" % (x, y)), b.op("umulhi %s, %s" % (x, y))

    # h += m || padbit
    t0 = b.op("load.i64 %s" % src, "m")
    t1 = b.op("load.i64 %s+8" % src, "m")
    h0, c = add(h0, t0)
    h1, c = addc(h1, t1, c)
    h2 = b.op("iadd %s, %s" % (b.op("iadd %s, %s" % (h2, ext(c))), padbit))
    # h *= r mod p, with 2^130 = 5 folded into s1 = 5 r1 / 4 (r1 is a multiple of 4).
    a_lo, a_hi = mul(h0, r0)
    b_lo, b_hi = mul(h1, s1)
    d0_lo, c = add(a_lo, b_lo)
    d0_hi = b.op("iadd %s, %s" % (b.op("iadd %s, %s" % (a_hi, b_hi)), ext(c)))
    e_lo, e_hi = mul(h0, r1)
    f_lo, f_hi = mul(h1, r0)
    d1_lo, c = add(e_lo, f_lo)
    d1_hi = b.op("iadd %s, %s" % (b.op("iadd %s, %s" % (e_hi, f_hi)), ext(c)))
    d1_lo, c = add(d1_lo, b.op("imul %s, %s" % (h2, s1)))
    d1_hi = b.op("iadd %s, %s" % (d1_hi, ext(c)))
    d1_lo, c = add(d1_lo, d0_hi)
    d1_hi = b.op("iadd %s, %s" % (d1_hi, ext(c)))
    h2 = b.op("iadd %s, %s" % (b.op("imul %s, %s" % (h2, r0)), d1_hi))
    # Partial reduction: h2 * 2^128 = (h2 >> 2) * 5 * 2^0 + (h2 & 3) * 2^128.
    hi_bits = b.op("band %s, %s" % (h2, b.const("i64", -4)))
    fold = b.op("iadd %s, %s" % (hi_bits, b.op("ushr %s, %s" % (h2, b.const("i64", 2)))))
    h2 = b.op("band %s, %s" % (h2, b.const("i64", 3)))
    h0, c = add(d0_lo, fold)
    h1, c = addc(d1_lo, zero, c)
    h2 = b.op("iadd %s, %s" % (h2, ext(c)))
    for i, v in enumerate((h0, h1, h2)):
        b.raw("store %s, %s+%d" % (v, hp, 8 * i))
    nxt = b.op("iadd %s, %s" % (pos, b.const("i64", 16)), "next")
    b.raw("store %s, %s+16" % (nxt, mp))
    b.raw("return %s" % nxt)
    return b


def gen_chacha():
    replace_region("ChaCha20.bd", "ChaCha20Kernels", looped(
        "i64 XorBlocks4(u32[] s, u8[] input, u8[] output, i64[] meta)",
        "/// XORs the keystream of 4-block groups into `output` for input offsets `meta[0]` up to\n"
        "/// `meta[2]` (a multiple of 256 past `meta[0]`); `meta[1]` is the output minus input offset.\n"
        "/// Precondition: all ranges are in bounds; the block does not check.",
        "meta[0] < meta[2]", chacha4(), "meta[0]") + "\n" + function(
        "i64 KeystreamBlock(u32[] s, u8[] out)", chacha1(),
        "/// The keystream block for the counter in `s[12]` into `out[0, 64)` (RFC 8439 2.3)."))
    replace_region("Poly1305.bd", "Poly1305Blocks", looped(
        "i64 Blocks(i64[] r, i64[] h, u8[] data, i64[] meta)",
        "/// Absorbs the 16-byte blocks of `data` from offset `meta[2]` up to `meta[3]` with pad\n"
        "/// bit `meta[4]` (radix 2^64). Precondition: the range is in bounds.",
        "meta[2] < meta[3]", poly1305_blocks(), "meta[2]"))


# ---------------------------------------------------------------- AES (vpaes) and GHASH

import vpaes  # noqa: E402  (tools/vpaes.py, the checked model)


class VecEmit:
    """vpaes vector interface emitting CLIF for `width` independent blocks at once.
    A value is either one SSA name shared by every block (constants, round keys) or a
    tuple with one name per block; each operation is emitted block by block, which
    interleaves the independent blocks for the out-of-order core."""

    def __init__(self, block, tables, width):
        self.b = block
        self.tp = tables
        self.width = width

    def _lanes(self, value):
        return value if isinstance(value, tuple) else (value,) * self.width

    def _map(self, fmt, *values):
        if all(not isinstance(v, tuple) for v in values):
            return self.b.op(fmt % values)
        lanes = [self._lanes(v) for v in values]
        return tuple(self.b.op(fmt % tuple(l[i] for l in lanes)) for i in range(self.width))

    def const(self, name):
        # A fresh load per use: a single-use load can fold into its consumer.
        return self.b.op("load.i8x16 %s+%d" % (self.tp, 16 * vpaes.NAMES.index(name)), "k")

    def xor(self, a, b):
        return self._map("bxor %s, %s", a, b)

    def band(self, a, b):
        return self._map("band %s, %s", a, b)

    def shr4(self, a):
        four = self.b.const("i32", 4)
        wide = self._map("bitcast.i32x4 little %s", a)
        shifted = self._map("ushr %%s, %s" % four.replace("%", "%%"), wide)
        return self._map("bitcast.i8x16 little %s", shifted)

    def swizzle(self, table, index):
        return self._map("swizzle %s, %s", table, index)

    def shuffle(self, a, b, mask):
        return self._map("shuffle %%s, %%s, %s" % lane_mask(mask), a, b)

    def zero(self):
        return self.b.op("splat.i8x16 %s" % self.b.const("i8", 0), "z")


def aes_rounds_of(bits):
    return {128: 10, 192: 12, 256: 14}[bits]


def aes_schedule(bits):
    """vpaes encryption key schedule: %0 key bytes, %1 tables, %2 out ((rounds+1) * 16)."""
    b = Block()
    kp = b.op("payload %0", "kp")
    tp = b.op("payload %1", "tp")
    op = b.op("payload %2", "op")
    v = VecEmit(b, tp, 1)
    lo = b.op("load.i8x16 %s" % kp, "key")
    hi = None
    if bits == 192:
        hi = b.op("load.i8x16 %s+8" % kp, "key")
    elif bits == 256:
        hi = b.op("load.i8x16 %s+16" % kp, "key")
    keys = vpaes.schedule(v, lo, hi, bits)
    for i, k in enumerate(keys):
        b.raw("store %s, %s+%d" % (k, op, 16 * i))
    b.raw("return %s" % b.const("i64", 0))
    return b


def aes_round_kernels(width):
    """vpaes split into three inline blocks so one function serves every key size and the
    rounds run as a Beskid loop (a fully unrolled 4-wide AES-256 is ~2500 instructions and
    dominated JIT time). Parameters: %0 round keys, %1 tables, %2 counter block (width 4) or
    unused, %3 input, %4 output, %5 state (16 * width bytes), %6 meta i64[]:
    width 4: [pos, out - in, end, counter, round, rounds]; width 1: [in, out, -, -, round, rounds]."""
    first_b, middle_b, last_b = Block(), Block(), Block()

    def common(b):
        return {
            "kp": b.op("payload %0", "kp"),
            "tp": b.op("payload %1", "tp"),
            "sp": b.op("payload %5", "sp"),
            "mp": b.op("payload %6", "mp"),
        }

    # Entry: counter blocks (or the input block), input transform, round-0 key.
    b = first_b
    p = common(b)
    v = VecEmit(b, p["tp"], width)
    if width == 4:
        jp = b.op("payload %2", "jp")
        ctr = b.op("load.i32 %s+24" % p["mp"], "ctr")
        base = b.op("bitcast.i32x4 little %s" % b.op("load.i8x16 %s" % jp, "j0"))
        blocks = []
        for j in range(4):
            c = ctr if j == 0 else b.op("iadd %s, %s" % (ctr, b.const("i32", j)))
            lane = b.op("insertlane %s, %s, 3" % (base, b.op("bswap %s" % c)))
            blocks.append(b.op("bitcast.i8x16 little %s" % lane, "cb"))
        block = tuple(blocks)
    else:
        ip = b.op("payload %3", "ip")
        off = b.op("load.i64 %s" % p["mp"], "off")
        block = b.op("load.i8x16 %s" % b.op("iadd %s, %s" % (ip, off), "src"), "in")
    x = vpaes.first(v, block, b.op("load.i8x16 %s" % p["kp"], "rk"))
    for j, xj in enumerate(x if isinstance(x, tuple) else (x,)):
        b.raw("store %s, %s+%d" % (xj, p["sp"], 16 * j))
    one = b.const("i64", 1)
    b.raw("store %s, %s+32" % (one, p["mp"]))
    b.raw("return %s" % one)

    def round_key(b, p, r):
        return b.op("load.i8x16 %s" % b.op("iadd %s, %s" % (p["kp"], b.op("ishl %s, %s" % (r, b.const("i64", 4)))), "ka"), "rk")

    def table_at(b, p, name, r):
        sel = b.op("ishl %s, %s" % (b.op("band %s, %s" % (r, b.const("i64", 3))), b.const("i64", 4)))
        address = b.op("iadd %s, %s" % (p["tp"], sel), "ta")
        return b.op("load.i8x16 %s+%d" % (address, 16 * vpaes.NAMES.index(name)), "k")

    def load_state(b, p):
        xs = tuple(b.op("load.i8x16 %s+%d" % (p["sp"], 16 * j), "x") for j in range(width))
        return xs if width > 1 else xs[0]

    # One middle round r = meta[4].
    b = middle_b
    p = common(b)
    v = VecEmit(b, p["tp"], width)
    r = b.op("load.i64 %s+32" % p["mp"], "r")
    x = vpaes.middle(v, load_state(b, p), round_key(b, p, r), table_at(b, p, "mcf0", r), table_at(b, p, "mcb0", r))
    for j, xj in enumerate(x if isinstance(x, tuple) else (x,)):
        b.raw("store %s, %s+%d" % (xj, p["sp"], 16 * j))
    nr = b.op("iadd %s, %s" % (r, b.const("i64", 1)), "next")
    b.raw("store %s, %s+32" % (nr, p["mp"]))
    b.raw("return %s" % nr)

    # Final round, keystream use, cursor advance.
    b = last_b
    p = common(b)
    v = VecEmit(b, p["tp"], width)
    rounds = b.op("load.i64 %s+40" % p["mp"], "rounds")
    out = vpaes.last(v, load_state(b, p), round_key(b, p, rounds), table_at(b, p, "sr0", rounds))
    ip = b.op("payload %3", "ip")
    op = b.op("payload %4", "op")
    if width == 4:
        pos = b.op("load.i64 %s" % p["mp"], "pos")
        delta = b.op("load.i64 %s+8" % p["mp"], "delta")
        src = b.op("iadd %s, %s" % (ip, pos), "src")
        dst = b.op("iadd %s, %s" % (b.op("iadd %s, %s" % (op, pos)), delta), "dst")
        for j in range(4):
            data = b.op("load.i8x16 %s+%d" % (src, 16 * j))
            b.raw("store %s, %s+%d" % (b.op("bxor %s, %s" % (data, out[j])), dst, 16 * j))
        ctr = b.op("load.i32 %s+24" % p["mp"], "ctr")
        b.raw("store %s, %s+24" % (b.op("iadd %s, %s" % (ctr, b.const("i32", 4))), p["mp"]))
        nxt = b.op("iadd %s, %s" % (pos, b.const("i64", 64)), "next")
    else:
        dst = b.op("iadd %s, %s" % (op, b.op("load.i64 %s+8" % p["mp"], "off")), "dst")
        b.raw("store %s, %s" % (out, dst))
        nxt = b.op("iadd %s, %s" % (b.op("load.i64 %s" % p["mp"]), b.const("i64", 16)), "next")
    b.raw("store %s, %s" % (nxt, p["mp"]))
    b.raw("return %s" % nxt)
    return first_b, middle_b, last_b


def aes_round_function(name, width, doc):
    first_b, middle_b, last_b = aes_round_kernels(width)
    ind = "            "
    return ("%s\ni64 %s(u8[] keys, u8[] tables, u8[] counterBlock, u8[] input, u8[] output, u8[] state, i64[] meta) {\n"
            "    mut i64 last = 0_i64;\n"
            "    while meta[0] < meta[2] {\n"
            "        last = clif {\n%s\n        };\n"
            "        while meta[4] < meta[5] {\n"
            "            last = clif {\n%s\n            };\n"
            "        }\n"
            "        last = clif {\n%s\n        };\n"
            "    }\n"
            "    return last;\n}\n") % (doc, name, first_b.render(ind), middle_b.render(ind + "    "), last_b.render(ind))


def ghash_blocks():
    """GHASH (SP 800-38D) over the 16-byte blocks of %1 from g[8] to g[9], constant time:
    BearSSL ghash_ctmul64 (64-bit multiplies with 4-bit holes, Karatsuba on the bit-reversed
    halves). %0 g i64[]: y1, y0, h1, h0, h1r, h0r, h2 = h0^h1, h2r, pos, end."""
    b = Block()
    gp = b.op("payload %0", "gp")
    dp = b.op("payload %1", "dp")
    pos = b.op("load.i64 %s+64" % gp, "pos")
    src = b.op("iadd %s, %s" % (dp, pos), "src")
    y1, y0, h1, h0, h1r, h0r, h2, h2r = [b.op("load.i64 %s+%d" % (gp, 8 * i), "g") for i in range(8)]
    y1 = b.op("bxor %s, %s" % (y1, b.op("bswap %s" % b.op("load.i64 %s" % src))))
    y0 = b.op("bxor %s, %s" % (y0, b.op("bswap %s" % b.op("load.i64 %s+8" % src))))
    masks = [b.const("i64", m) for m in (0x1111111111111111, 0x2222222222222222, 0x4444444444444444, 0x8888888888888888)]

    def x(u, v):
        return b.op("bxor %s, %s" % (u, v))

    def bmul64(u, v):
        us = [b.op("band %s, %s" % (u, m)) for m in masks]
        vs = [b.op("band %s, %s" % (v, m)) for m in masks]
        pairs = [((0, 0), (1, 3), (2, 2), (3, 1)), ((0, 1), (1, 0), (2, 3), (3, 2)),
                 ((0, 2), (1, 1), (2, 0), (3, 3)), ((0, 3), (1, 2), (2, 1), (3, 0))]
        zs = []
        for k, terms in enumerate(pairs):
            prods = [b.op("imul %s, %s" % (us[i], vs[j])) for (i, j) in terms]
            z = x(x(prods[0], prods[1]), x(prods[2], prods[3]))
            zs.append(b.op("band %s, %s" % (z, masks[k])))
        return b.op("bor %s, %s" % (b.op("bor %s, %s" % (zs[0], zs[1])), b.op("bor %s, %s" % (zs[2], zs[3]))))

    def sh(op, u, n):
        return b.op("%s %s, %s" % (op, u, b.const("i64", n)))

    y0r = b.op("bitrev %s" % y0)
    y1r = b.op("bitrev %s" % y1)
    y2 = x(y0, y1)
    y2r = x(y0r, y1r)
    z0 = bmul64(y0, h0)
    z1 = bmul64(y1, h1)
    z2 = bmul64(y2, h2)
    z0h = bmul64(y0r, h0r)
    z1h = bmul64(y1r, h1r)
    z2h = bmul64(y2r, h2r)
    z2 = x(z2, x(z0, z1))
    z2h = x(z2h, x(z0h, z1h))
    z0h = sh("ushr", b.op("bitrev %s" % z0h), 1)
    z1h = sh("ushr", b.op("bitrev %s" % z1h), 1)
    z2h = sh("ushr", b.op("bitrev %s" % z2h), 1)
    v0, v1, v2, v3 = z0, x(z0h, z2), x(z1, z2h), z1h
    v3 = b.op("bor %s, %s" % (sh("ishl", v3, 1), sh("ushr", v2, 63)))
    v2 = b.op("bor %s, %s" % (sh("ishl", v2, 1), sh("ushr", v1, 63)))
    v1 = b.op("bor %s, %s" % (sh("ishl", v1, 1), sh("ushr", v0, 63)))
    v0 = sh("ishl", v0, 1)
    v2 = x(v2, x(x(v0, sh("ushr", v0, 1)), x(sh("ushr", v0, 2), sh("ushr", v0, 7))))
    v1 = x(v1, x(x(sh("ishl", v0, 63), sh("ishl", v0, 62)), sh("ishl", v0, 57)))
    v3 = x(v3, x(x(v1, sh("ushr", v1, 1)), x(sh("ushr", v1, 2), sh("ushr", v1, 7))))
    v2 = x(v2, x(x(sh("ishl", v1, 63), sh("ishl", v1, 62)), sh("ishl", v1, 57)))
    b.raw("store %s, %s" % (v3, gp))
    b.raw("store %s, %s+8" % (v2, gp))
    nxt = b.op("iadd %s, %s" % (pos, b.const("i64", 16)), "next")
    b.raw("store %s, %s+64" % (nxt, gp))
    b.raw("return %s" % nxt)
    return b


def ghash_prepare():
    """Derives h1r, h0r, h2, h2r of g from h1, h0 (g[2], g[3])."""
    b = Block()
    gp = b.op("payload %0", "gp")
    h1 = b.op("load.i64 %s+16" % gp)
    h0 = b.op("load.i64 %s+24" % gp)
    h1r = b.op("bitrev %s" % h1)
    h0r = b.op("bitrev %s" % h0)
    b.raw("store %s, %s+32" % (h1r, gp))
    b.raw("store %s, %s+40" % (h0r, gp))
    b.raw("store %s, %s+48" % (b.op("bxor %s, %s" % (h0, h1)), gp))
    b.raw("store %s, %s+56" % (b.op("bxor %s, %s" % (h0r, h1r)), gp))
    b.raw("return %s" % b.const("i64", 0))
    return b


def gen_aes():
    if not vpaes.check():
        sys.exit("vpaes model does not match FIPS-197")
    parts = []
    for bits in (128, 192, 256):
        parts.append(function(
            "i64 Schedule%d(u8[] key, u8[] tables, u8[] out)" % bits, aes_schedule(bits),
            "/// vpaes encryption key schedule for a %d-bit key into `out` (%d bytes)." % (bits, 16 * (aes_rounds_of(bits) + 1))))
    parts.append(aes_round_function("Blocks4", 4,
        "/// AES-CTR over 64-byte groups (four blocks interleaved) from input offset `meta[0]` up\n"
        "/// to `meta[2]`; `meta[1]` is the output minus input offset, `meta[3]` the 32-bit block\n"
        "/// counter, `meta[5]` the round count. Precondition: all ranges are in bounds."))
    parts.append(aes_round_function("Block1", 1,
        "/// One AES block from `input[meta[0]]` to `output[meta[1]]` (run with `meta[2] = meta[0] + 1`)."))
    table = ", ".join("0x%02x_u8" % x for x in vpaes.table_bytes())
    parts.append("/// The vpaes constant vectors in `tools/vpaes.py` order.\nu8[] Tables() {\n    return [%s];\n}\n" % table)
    replace_region("Aes.bd", "AesKernels", "\n".join(parts))
    replace_region("AesGcm.bd", "GhashKernels", looped(
        "i64 GhashBlocks(i64[] g, u8[] data)",
        "/// GHASH over the 16-byte blocks of `data` from offset `g[8]` up to `g[9]`.\n"
        "/// Precondition: the range is in bounds.", "g[8] < g[9]", ghash_blocks()) + "\n" + function(
        "i64 GhashPrepare(i64[] g)", ghash_prepare(),
        "/// Fills the bit-reversed and Karatsuba middle hash-key words of `g`."))


GENERATORS = {"sha": gen_sha, "chacha": gen_chacha, "aes": gen_aes}

if __name__ == "__main__":
    names = sys.argv[1:] or sorted(GENERATORS)
    for name in names:
        GENERATORS[name]()
