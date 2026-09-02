#!/usr/bin/env python3
"""Build the MDBList Kodi repository files."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
REPO_DIR = ROOT / "repo"
ZIPS_DIR = REPO_DIR / "zips"
SOURCE_ADDON = ROOT.parent / "kodi-mdblist-scrobbler"
ADDON_ID = "service.mdblist-scrobbler"
REPOSITORY_ID = "repository.mdblist"

COPY_PATHS = [
    "addon.xml",
    "CHANGELOG.md",
    "icon.png",
    "LICENSE",
    "mdblist-kodi.png",
    "plugin.py",
    "README.md",
    "resources",
    "script.py",
    "service.py",
]

IGNORED_NAMES = {
    ".DS_Store",
    "__pycache__",
}


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def copy_addon_source() -> None:
    target = REPO_DIR / ADDON_ID
    remove_path(target)
    target.mkdir(parents=True)

    for relative in COPY_PATHS:
        source = SOURCE_ADDON / relative
        destination = target / relative
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*IGNORED_NAMES))
        elif source.exists():
            shutil.copy2(source, destination)


def addon_entries() -> list[ElementTree.Element]:
    entries = []
    for addon_xml in sorted(REPO_DIR.glob("*/addon.xml")):
        if addon_xml.parent.name == "zips":
            continue
        entries.append(ElementTree.parse(addon_xml).getroot())
    return entries


def zip_addon(addon_folder: Path, addon_id: str, version: str) -> None:
    zip_folder = ZIPS_DIR / addon_id
    zip_folder.mkdir(parents=True, exist_ok=True)
    zip_path = zip_folder / f"{addon_id}-{version}.zip"
    remove_path(zip_path)

    root_parent = addon_folder.parent
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(addon_folder.rglob("*")):
            if file_path.is_file() and not any(part in IGNORED_NAMES for part in file_path.parts):
                archive.write(file_path, file_path.relative_to(root_parent))

    for metadata in ["addon.xml", "icon.png", "fanart.jpg"]:
        source = addon_folder / metadata
        if source.exists():
            shutil.copy2(source, zip_folder / metadata)


def build_addons_xml(entries: list[ElementTree.Element]) -> Path:
    addons = ElementTree.Element("addons")
    for entry in sorted(entries, key=lambda element: element.get("id", "")):
        addons.append(entry)

    ZIPS_DIR.mkdir(parents=True, exist_ok=True)
    addons_xml = ZIPS_DIR / "addons.xml"
    ElementTree.indent(addons, space="    ")
    ElementTree.ElementTree(addons).write(addons_xml, encoding="utf-8", xml_declaration=True)
    return addons_xml


def write_md5(path: Path) -> None:
    digest = hashlib.md5(path.read_bytes()).hexdigest()
    path.with_suffix(path.suffix + ".md5").write_text(digest, encoding="utf-8")


def build() -> None:
    copy_addon_source()
    entries = addon_entries()

    remove_path(ZIPS_DIR)
    for entry in entries:
        addon_id = entry.attrib["id"]
        version = entry.attrib["version"]
        zip_addon(REPO_DIR / addon_id, addon_id, version)

    addons_xml = build_addons_xml(entries)
    write_md5(addons_xml)

    repo_entry = ElementTree.parse(REPO_DIR / REPOSITORY_ID / "addon.xml").getroot()
    repo_version = repo_entry.attrib["version"]
    repo_zip = ZIPS_DIR / REPOSITORY_ID / f"{REPOSITORY_ID}-{repo_version}.zip"
    shutil.copy2(repo_zip, ROOT / repo_zip.name)


if __name__ == "__main__":
    build()
