# MDBList Kodi Repository

Kodi repository for MDBList add-ons.

## Install

1. Enable unknown sources in Kodi.
2. Add this repository's GitHub Pages URL as a file source, or download `repository.mdblist-1.0.0.zip`.
3. Install the repository zip in Kodi.
4. Install **MDBList Scrobbler** from **MDBList Kodi Repository**.

## Build

Run this from the repository root:

```sh
python3 scripts/build_repo.py
```

The build script copies `service.mdblist-scrobbler` from the sibling `kodi-mdblist-scrobbler` checkout, creates Kodi zip packages, writes `addons.xml`, writes `addons.xml.md5`, and copies the repository installer zip to the repository root.
