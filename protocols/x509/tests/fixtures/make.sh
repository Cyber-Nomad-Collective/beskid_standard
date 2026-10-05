#!/usr/bin/env bash
# Regenerates the X.509 test fixtures with OpenSSL 3 (tested with 3.6).
# Only certificates are kept; private keys stay in a temporary directory.
# Validity windows are fixed so that tests can pass an explicit time:
#   CAs     2025-01-01 .. 2035-01-01
#   leaves  2025-01-01 .. 2030-01-01
#   expired 2020-01-01 .. 2021-01-01
# Tests validate at 2026-06-01T00:00:00Z (epoch 1780272000).
set -euo pipefail
OUT="$(cd "$(dirname "$0")" && pwd)"
OPENSSL="${OPENSSL:-openssl}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"

CA_FROM=20250101000000Z; CA_TO=20350101000000Z
LEAF_FROM=20250101000000Z; LEAF_TO=20300101000000Z
OLD_FROM=20200101000000Z; OLD_TO=20210101000000Z

rsa_key() { "$OPENSSL" genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$1.key" 2>/dev/null; }
ec_key()  { "$OPENSSL" genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out "$1.key" 2>/dev/null; }

# self_signed NAME SUBJECT EXTFILE DIGEST
self_signed() {
  "$OPENSSL" req -new -key "$1.key" -subj "$2" -config /dev/null -out "$1.csr"
  "$OPENSSL" x509 -req -in "$1.csr" -key "$1.key" -"$4" -set_serial "0x$("$OPENSSL" rand -hex 8)" \
    -not_before "$CA_FROM" -not_after "$CA_TO" -extfile "$3" -extensions ext -out "$1.pem" 2>/dev/null
}

# issue NAME SUBJECT ISSUER EXTFILE DIGEST FROM TO [sigopts...]
issue() {
  local name=$1 subj=$2 issuer=$3 ext=$4 dgst=$5 from=$6 to=$7; shift 7
  "$OPENSSL" req -new -key "$name.key" -subj "$subj" -config /dev/null -out "$name.csr"
  "$OPENSSL" x509 -req -in "$name.csr" -CA "$issuer.pem" -CAkey "$issuer.key" -"$dgst" \
    -set_serial "0x$("$OPENSSL" rand -hex 8)" -not_before "$from" -not_after "$to" \
    -extfile "$ext" -extensions ext "$@" -out "$name.pem" 2>/dev/null
}

cat > root.ext <<'X'
[ext]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
X
cat > int0.ext <<'X'
[ext]
basicConstraints=critical,CA:TRUE,pathlen:0
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always
X
cat > int.ext <<'X'
[ext]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always
X
cat > noca.ext <<'X'
[ext]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyCertSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always
X
cat > nc.ext <<'X'
[ext]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
nameConstraints=critical,permitted;DNS:allowed.test,excluded;DNS:bad.allowed.test
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always
X
leaf_ext() { # FILE SANS EKU
  cat > "$1" <<X
[ext]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=$3
subjectAltName=$2
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always
X
}
leaf_ext leaf.ext "DNS:www.example.test,DNS:*.api.example.test,IP:192.0.2.10,IP:2001:db8::1" serverAuth
leaf_ext client.ext "DNS:client.example.test" clientAuth
leaf_ext ncok.ext "DNS:www.allowed.test,DNS:allowed.test" serverAuth
leaf_ext ncbad.ext "DNS:www.evil.test" serverAuth
leaf_ext ncexcl.ext "DNS:x.bad.allowed.test" serverAuth
leaf_ext plain.ext "DNS:leaf.example.test" serverAuth
cp plain.ext crit.ext
echo "1.3.6.1.4.1.99999.1=critical,ASN1:NULL" >> crit.ext

# RSA chain: root -> int (pathlen 0) -> leaf
rsa_key rsa-root; self_signed rsa-root "/C=PL/O=Beskid Test/CN=Beskid Test RSA Root" root.ext sha256
rsa_key rsa-int; issue rsa-int "/C=PL/O=Beskid Test/CN=Beskid Test RSA Intermediate" rsa-root int0.ext sha256 "$CA_FROM" "$CA_TO"
rsa_key rsa-leaf; issue rsa-leaf "/CN=www.example.test" rsa-int leaf.ext sha256 "$LEAF_FROM" "$LEAF_TO"
rsa_key rsa-leaf512; issue rsa-leaf512 "/CN=leaf.example.test" rsa-int plain.ext sha512 "$LEAF_FROM" "$LEAF_TO"
rsa_key rsa-leafpss; issue rsa-leafpss "/CN=leaf.example.test" rsa-int plain.ext sha256 "$LEAF_FROM" "$LEAF_TO" \
  -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 -sigopt rsa_mgf1_md:sha256
# pathLen violation: rsa-int (pathlen 0) -> rsa-sub (CA) -> rsa-subleaf
rsa_key rsa-sub; issue rsa-sub "/CN=Beskid Test RSA Sub CA" rsa-int int.ext sha256 "$CA_FROM" "$CA_TO"
ec_key rsa-subleaf; issue rsa-subleaf "/CN=leaf.example.test" rsa-sub plain.ext sha256 "$LEAF_FROM" "$LEAF_TO"

# P-256 chain: root -> int (SHA-384 signature) -> leaf
ec_key ec-root; self_signed ec-root "/C=PL/O=Beskid Test/CN=Beskid Test EC Root" root.ext sha256
ec_key ec-int; issue ec-int "/C=PL/O=Beskid Test/CN=Beskid Test EC Intermediate" ec-root int.ext sha384 "$CA_FROM" "$CA_TO"
ec_key ec-leaf; issue ec-leaf "/CN=www.example.test" ec-int leaf.ext sha256 "$LEAF_FROM" "$LEAF_TO"
ec_key ec-expired; issue ec-expired "/CN=leaf.example.test" ec-int plain.ext sha256 "$OLD_FROM" "$OLD_TO"
ec_key ec-client; issue ec-client "/CN=client.example.test" ec-int client.ext sha256 "$LEAF_FROM" "$LEAF_TO"
ec_key ec-crit; issue ec-crit "/CN=leaf.example.test" ec-int crit.ext sha256 "$LEAF_FROM" "$LEAF_TO"
# Non-CA "intermediate" that signs a leaf.
ec_key ec-noca; issue ec-noca "/CN=Beskid Test Not A CA" ec-int noca.ext sha256 "$CA_FROM" "$CA_TO"
ec_key ec-nocaleaf; issue ec-nocaleaf "/CN=leaf.example.test" ec-noca plain.ext sha256 "$LEAF_FROM" "$LEAF_TO"
# Name constraints: permitted allowed.test, excluded bad.allowed.test.
ec_key ec-nc; issue ec-nc "/CN=Beskid Test Constrained CA" ec-root nc.ext sha256 "$CA_FROM" "$CA_TO"
ec_key ec-ncok; issue ec-ncok "/CN=www.allowed.test" ec-nc ncok.ext sha256 "$LEAF_FROM" "$LEAF_TO"
ec_key ec-ncbad; issue ec-ncbad "/CN=www.evil.test" ec-nc ncbad.ext sha256 "$LEAF_FROM" "$LEAF_TO"
ec_key ec-ncexcl; issue ec-ncexcl "/CN=x.bad.allowed.test" ec-nc ncexcl.ext sha256 "$LEAF_FROM" "$LEAF_TO"

for f in *.pem; do cp "$f" "$OUT/$f"; done
cat rsa-root.pem ec-root.pem > "$OUT/roots.pem"
echo "fixtures written to $OUT"
