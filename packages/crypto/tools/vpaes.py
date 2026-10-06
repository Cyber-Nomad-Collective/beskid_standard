"""Vector-permute AES (Hamburg, "Accelerating AES with Vector Permute Instructions",
CHES 2009) as used by OpenSSL vpaes-x86_64.pl, written once against a small 16-byte
vector interface so the same code either emulates (to check the constants against
FIPS-197) or emits CLIF (`swizzle` = pshufb for indices in 0..15 or with the top bit set,
which is all vpaes produces)."""

# Constant vectors, as OpenSSL lists them (.quad low, high; little-endian bytes).
QUADS = {
    "inv": (0x0E05060F0D080180, 0x040703090A0B0C02),
    "inva": (0x01040A060F0B0780, 0x030D0E0C02050809),
    "s0F": (0x0F0F0F0F0F0F0F0F, 0x0F0F0F0F0F0F0F0F),
    "iptlo": (0xC2B2E8985A2A7000, 0xCABAE09052227808),
    "ipthi": (0x4C01307D317C4D00, 0xCD80B1FCB0FDCC81),
    "sb1u": (0xB19BE18FCB503E00, 0xA5DF7A6E142AF544),
    "sb1t": (0x3618D415FAE22300, 0x3BF7CCC10D2ED9EF),
    "sb2u": (0xE27A93C60B712400, 0x5EB7E955BC982FCD),
    "sb2t": (0x69EB88400AE12900, 0xC2A163C8AB82234A),
    "sbou": (0xD0D26D176FBDC700, 0x15AABF7AC502A878),
    "sbot": (0xCFE474A55FBB6A00, 0x8E1E90D1412B35FA),
    "mcf0": (0x0407060500030201, 0x0C0F0E0D080B0A09),
    "mcf1": (0x080B0A0904070605, 0x000302010C0F0E0D),
    "mcf2": (0x0C0F0E0D080B0A09, 0x0407060500030201),
    "mcf3": (0x000302010C0F0E0D, 0x080B0A0904070605),
    "mcb0": (0x0605040702010003, 0x0E0D0C0F0A09080B),
    "mcb1": (0x020100030E0D0C0F, 0x0A09080B06050407),
    "mcb2": (0x0E0D0C0F0A09080B, 0x0605040702010003),
    "mcb3": (0x0A09080B06050407, 0x020100030E0D0C0F),
    "sr0": (0x0706050403020100, 0x0F0E0D0C0B0A0908),
    "sr1": (0x030E09040F0A0500, 0x0B06010C07020D08),
    "sr2": (0x0F060D040B020900, 0x070E050C030A0108),
    "sr3": (0x0B0E0104070A0D00, 0x0306090C0F020508),
    "rcon": (0x1F8391B9AF9DEEB6, 0x702A98084D7C7D81),
    "s63": (0x5B5B5B5B5B5B5B5B, 0x5B5B5B5B5B5B5B5B),
    "optlo": (0xFF9F4929D6B66000, 0xF7974121DEBE6808),
    "opthi": (0x01EDBD5150BCEC00, 0xE10D5DB1B05C0CE0),
}
NAMES = list(QUADS)


def const_bytes(name):
    lo, hi = QUADS[name]
    return list(lo.to_bytes(8, "little") + hi.to_bytes(8, "little"))


def table_bytes():
    out = []
    for name in NAMES:
        out += const_bytes(name)
    return out


class Emu:
    """Concrete 16-byte vectors as Python lists."""

    def const(self, name):
        return const_bytes(name)

    def xor(self, a, b):
        return [x ^ y for x, y in zip(a, b)]

    def band(self, a, b):
        return [x & y for x, y in zip(a, b)]

    def shr4(self, a):
        # Bytes are already masked to their high nibble; a 32-bit lane shift by 4 then
        # leaves each nibble in its own byte.
        return [x >> 4 for x in a]

    def swizzle(self, table, index):
        return [table[i] if i < 16 else 0 for i in index]

    def shuffle(self, a, b, mask):
        both = a + b
        return [both[i] for i in mask]

    def zero(self):
        return [0] * 16


def split(v, x):
    """(low nibbles, high nibbles) of every byte."""
    s0f = v.const("s0F")
    lo = v.band(x, s0f)
    hi = v.shr4(v.xor(x, lo))
    return lo, hi


def transform(v, x, lo_name, hi_name):
    lo, hi = split(v, x)
    return v.xor(v.swizzle(v.const(lo_name), lo), v.swizzle(v.const(hi_name), hi))


def inversion(v, x):
    """The shared top of a round: returns (io, jo) for the sbox output tables."""
    k, i = split(v, x)
    ak = v.swizzle(v.const("inva"), k)
    j = v.xor(k, i)
    inv = v.const("inv")
    iak = v.xor(v.swizzle(inv, i), ak)
    jak = v.xor(v.swizzle(inv, j), ak)
    io = v.xor(v.swizzle(inv, iak), j)
    jo = v.xor(v.swizzle(inv, jak), i)
    return io, jo


def first(v, block, key0):
    """Input transform and round-0 key."""
    return v.xor(transform(v, block, "iptlo", "ipthi"), key0)


def middle(v, x, key, forward, backward):
    """One full round; `forward`/`backward` are mc_forward/mc_backward[r mod 4]."""
    io, jo = inversion(v, x)
    a = v.xor(v.xor(v.swizzle(v.const("sb1u"), io), key), v.swizzle(v.const("sb1t"), jo))
    a2 = v.xor(v.swizzle(v.const("sb2u"), io), v.swizzle(v.const("sb2t"), jo))
    b = v.swizzle(a, forward)
    two_a_b = v.xor(a2, b)
    d = v.swizzle(a, backward)
    return v.xor(v.swizzle(two_a_b, forward), v.xor(two_a_b, d))


def last(v, x, key, sr):
    """The final round; `sr` is the ShiftRows permutation sr[rounds mod 4]."""
    io, jo = inversion(v, x)
    out = v.xor(v.xor(v.swizzle(v.const("sbou"), io), key), v.swizzle(v.const("sbot"), jo))
    return v.swizzle(out, sr)


def encrypt(v, block, keys, rounds):
    """`keys` holds rounds + 1 vectors in vpaes form; `rounds` is 10, 12 or 14."""
    x = first(v, block, keys[0])
    for r in range(1, rounds):
        x = middle(v, x, keys[r], v.const("mcf%d" % (r % 4)), v.const("mcb%d" % (r % 4)))
    return last(v, x, keys[rounds], v.const("sr%d" % (rounds % 4)))


# Byte masks for the SSE moves the key schedule uses, as two-input shuffles of (a, b).
def m_pshufd(imm):
    return [4 * ((imm >> (2 * (i // 4))) & 3) + i % 4 for i in range(16)]


def m_palignr(n):
    """palignr $n, src, dst: (dst:src) >> 8n, with shuffle(src, dst)."""
    return [i + n for i in range(16)]


M_PSLLDQ4 = [16 + i for i in range(4)] + list(range(12))   # shuffle(x, zero)
M_PSLLDQ8 = [16 + i for i in range(8)] + list(range(8))
M_MOVHLPS = [8 + i for i in range(8)] + [24 + i for i in range(8)]  # shuffle(src, dst)


def pslldq(v, x, n):
    return v.shuffle(x, v.zero(), M_PSLLDQ4 if n == 4 else M_PSLLDQ8)


def schedule(v, key_lo, key_hi, bits):
    """Encryption key schedule (_vpaes_schedule_core, direction 0). Returns round keys."""
    out = []
    state = {"rcon": v.const("rcon"), "x7": None, "r8": 0x30}

    def mangle(x):
        t = v.xor(x, v.const("s63"))
        f = v.const("mcf0")
        t = v.swizzle(t, f)
        acc = t
        t = v.swizzle(t, f)
        acc = v.xor(acc, t)
        t = v.swizzle(t, f)
        acc = v.xor(acc, t)
        out.append(v.swizzle(acc, v.const("sr%d" % (state["r8"] // 16))))
        state["r8"] = (state["r8"] - 16) & 0x30

    def low_round(x):
        x7 = state["x7"]
        x7 = v.xor(x7, pslldq(v, x7, 4))
        x7 = v.xor(x7, pslldq(v, x7, 8))
        x7 = v.xor(x7, v.const("s63"))
        io, jo = inversion(v, x)
        s = v.xor(v.swizzle(v.const("sb1u"), io), v.swizzle(v.const("sb1t"), jo))
        x = v.xor(s, x7)
        state["x7"] = x
        return x

    def round_(x):
        rc = state["rcon"]
        first = v.shuffle(rc, v.zero(), m_palignr(15))      # [rcon[15], 0, ...]
        state["rcon"] = v.shuffle(rc, rc, m_palignr(15))
        state["x7"] = v.xor(state["x7"], first)
        x = v.shuffle(x, x, m_pshufd(0xFF))
        x = v.shuffle(x, x, m_palignr(1))
        return low_round(x)

    def last(x):
        x = v.swizzle(x, v.const("sr%d" % (state["r8"] // 16)))
        x = v.xor(x, v.const("s63"))
        out.append(transform(v, x, "optlo", "opthi"))

    x = transform(v, key_lo, "iptlo", "ipthi")
    state["x7"] = x
    out.append(x)
    if bits == 128:
        for n in range(10, 0, -1):
            x = round_(x)
            if n == 1:
                last(x)
            else:
                mangle(x)
    elif bits == 192:
        # key_hi holds key bytes 8..24 (the second load is 8 bytes into the key).
        x = transform(v, key_hi, "iptlo", "ipthi")
        x6 = v.shuffle(v.zero(), x, M_MOVHLPS)             # low half <- zeros
        for n in range(4, 0, -1):
            x = round_(x)
            x = v.shuffle(x6, x, m_palignr(8))
            mangle(x)
            x6, x = smear(v, x6, state)
            mangle(x)
            x = round_(x)
            if n == 1:
                last(x)
                break
            mangle(x)
            x6, x = smear(v, x6, state)
    else:
        x = transform(v, key_hi, "iptlo", "ipthi")
        for n in range(7, 0, -1):
            mangle(x)
            x6 = x
            x = round_(x)
            if n == 1:
                last(x)
                break
            mangle(x)
            x = v.shuffle(x, x, m_pshufd(0xFF))
            x5 = state["x7"]
            state["x7"] = x6
            x = low_round(x)
            state["x7"] = x5
    return out


def smear(v, x6, state):
    x7 = state["x7"]
    x1 = v.shuffle(x6, x6, m_pshufd(0x80))
    x0 = v.shuffle(x7, x7, m_pshufd(0xFE))
    x6 = v.xor(v.xor(x6, x1), x0)
    x0 = x6
    x6 = v.shuffle(v.zero(), x6, M_MOVHLPS)
    return x6, x0


def check():
    vectors = [
        (bytes(range(16)), "69c4e0d86a7b0430d8cdb78070b4c55a"),
        (bytes(range(24)), "dda97ca4864cdfe06eaf70a0ec0d7191"),
        (bytes(range(32)), "8ea2b7ca516745bfeafc49904b496089"),
    ]
    pt = list(bytes.fromhex("00112233445566778899aabbccddeeff"))
    v = Emu()
    ok = True
    for key, expected in vectors:
        bits = len(key) * 8
        hi = list(key[8:24]) if bits == 192 else list(key[16:32]) + [0] * (32 - len(key))
        keys = schedule(v, list(key[:16]), hi[:16], bits)
        got = bytes(encrypt(v, pt, keys, len(keys) - 1)).hex()
        print(bits, len(keys), got, got == expected)
        ok = ok and got == expected
    return ok


if __name__ == "__main__":
    check()
