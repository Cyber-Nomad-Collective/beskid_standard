# Changelog

All notable changes to this package are documented here, following Keep a Changelog.

## [Unreleased]

### Added

- Portable typed DNS, TCP, and UDP APIs with bounded ports, exact-width IP
  addresses, a closed NetworkError union, and Foundation disposal integration.
- TCP conformance to the existing Core.IO transfer and close contracts, with
  no duplicate ReadExact or WriteAll implementation.
- Corelib language tests for addressing, errors, resolver filtering, stream
  transfer, datagram boundaries, cleanup, and stale resource generations.
