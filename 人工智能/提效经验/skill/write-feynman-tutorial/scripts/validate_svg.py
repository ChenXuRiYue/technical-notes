#!/usr/bin/env python3
"""Validate deterministic structural requirements for teaching SVG files."""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
LENGTH_RE = re.compile(
    r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:px)?$"
)
URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def finite_number(raw: str) -> float | None:
    if not NUMBER_RE.fullmatch(raw.strip()):
        return None
    value = float(raw)
    return value if math.isfinite(value) else None


def positive_length(raw: str | None) -> bool:
    if raw is None:
        return False
    match = LENGTH_RE.fullmatch(raw.strip())
    if not match:
        return False
    value = float(match.group(1))
    return math.isfinite(value) and value > 0


def is_external_reference(value: str) -> bool:
    value = value.strip().strip("'\"")
    if not value or value.startswith("#") or value.startswith("data:"):
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc or value.startswith("//") or not value.startswith("#"))


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return ["file does not exist or is not a regular file"]

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot read UTF-8 SVG: {exc}"]

    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        return [f"invalid XML: {exc}"]

    if local_name(root.tag) != "svg":
        errors.append("root element must be <svg>")
    if root.get("role") != "img":
        errors.append('root role must be "img"')

    for attribute in ("width", "height"):
        if not positive_length(root.get(attribute)):
            errors.append(f"root {attribute} must be a positive number or px length")

    view_box = root.get("viewBox")
    if view_box is None:
        errors.append("root must define viewBox")
    else:
        parts = re.split(r"[\s,]+", view_box.strip())
        values = [finite_number(part) for part in parts]
        if len(parts) != 4 or any(value is None for value in values):
            errors.append("viewBox must contain four finite numbers")
        elif values[2] <= 0 or values[3] <= 0:
            errors.append("viewBox width and height must be positive")

    elements = list(root.iter())
    if any(local_name(element.tag) == "script" for element in elements):
        errors.append("SVG must not contain <script>")

    ids: list[str] = []
    id_to_element: dict[str, ET.Element] = {}
    for element in elements:
        element_id = element.get("id") or element.get(XML_ID)
        if element_id is not None:
            if not element_id.strip():
                errors.append(f"<{local_name(element.tag)}> has an empty id")
            else:
                ids.append(element_id)
                id_to_element.setdefault(element_id, element)

    for element_id, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate id: {element_id}")

    title = next((item for item in list(root) if local_name(item.tag) == "title"), None)
    desc = next((item for item in list(root) if local_name(item.tag) == "desc"), None)
    for label, element in (("title", title), ("desc", desc)):
        if element is None:
            errors.append(f"root must contain a direct <{label}> child")
            continue
        if not "".join(element.itertext()).strip():
            errors.append(f"<{label}> must contain text")
        if not (element.get("id") or element.get(XML_ID)):
            errors.append(f"<{label}> must have an id")

    labelled_by = root.get("aria-labelledby")
    if not labelled_by:
        errors.append("root must define aria-labelledby")
    else:
        aria_ids = labelled_by.split()
        if len(aria_ids) != len(set(aria_ids)):
            errors.append("aria-labelledby contains duplicate references")
        for ref_id in aria_ids:
            if ref_id not in id_to_element:
                errors.append(f"aria-labelledby references missing id: {ref_id}")
        for label, element in (("title", title), ("desc", desc)):
            if element is not None:
                element_id = element.get("id") or element.get(XML_ID)
                if element_id and element_id not in aria_ids:
                    errors.append(f"aria-labelledby must reference <{label}> id: {element_id}")

    expected_types = {
        "marker-start": "marker",
        "marker-mid": "marker",
        "marker-end": "marker",
        "filter": "filter",
    }
    for element in elements:
        element_name = local_name(element.tag)
        for attribute, raw_value in element.attrib.items():
            attribute_name = local_name(attribute)
            if attribute_name == "href":
                if is_external_reference(raw_value):
                    errors.append(
                        f"<{element_name}> {attribute_name} uses an external resource: {raw_value}"
                    )
                elif raw_value.startswith("#") and raw_value[1:] not in id_to_element:
                    errors.append(f"<{element_name}> references missing id: {raw_value[1:]}")

            for match in URL_RE.finditer(raw_value):
                reference = match.group(2).strip()
                if is_external_reference(reference):
                    errors.append(
                        f"<{element_name}> {attribute_name} uses an external resource: {reference}"
                    )
                    continue
                if not reference.startswith("#"):
                    continue
                ref_id = reference[1:]
                target = id_to_element.get(ref_id)
                if target is None:
                    errors.append(f"<{element_name}> {attribute_name} references missing id: {ref_id}")
                    continue
                expected = expected_types.get(attribute_name)
                if expected and local_name(target.tag) != expected:
                    errors.append(
                        f"<{element_name}> {attribute_name} must reference <{expected}>, got "
                        f"<{local_name(target.tag)}> for id {ref_id}"
                    )

    for style in (element for element in elements if local_name(element.tag) == "style"):
        css = "".join(style.itertext())
        if re.search(r"@import\b", css, re.IGNORECASE):
            errors.append("styles must not use @import")
        for match in URL_RE.finditer(css):
            reference = match.group(2).strip()
            if is_external_reference(reference):
                errors.append(f"<style> uses an external resource: {reference}")
            elif reference.startswith("#") and reference[1:] not in id_to_element:
                errors.append(f"<style> references missing id: {reference[1:]}")

    return list(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate structural and accessibility requirements for teaching SVG files."
    )
    parser.add_argument("svg", nargs="+", type=Path, help="SVG file(s) to validate")
    args = parser.parse_args()

    failed = False
    for path in args.svg:
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
