"""Strict catalog-package validator for development assets.

It deliberately separates a material-test record from actual-garment validation.
The current catalog contains no customer data and grants only visualization capability.
"""
from __future__ import annotations
import json
from pathlib import Path

ALLOWED_SOURCE_CLASSES = {'pattern_cad', 'scan', 'photo_proxy', 'artistic_proxy'}
BOOLEAN_CAPABILITIES = {
    'visualization', 'measurement_matched_body', 'pattern_faithful_grading',
    'validated_drape', 'pressure_or_strain', 'actual_garment_fit', 'size_recommendation'
}


def load_and_validate_catalog(path: Path) -> dict:
    data = json.loads(path.read_text())
    if data.get('schema_version') != 1 or not isinstance(data.get('catalog_id'), str):
        raise ValueError('Unsupported catalog contract')
    items = data.get('items')
    if not isinstance(items, list) or not items:
        raise ValueError('Catalog must contain at least one item')
    seen_products = set()
    for item in items:
        product = item.get('product_id')
        if not product or product in seen_products:
            raise ValueError('Product IDs must be unique and non-empty')
        seen_products.add(product)
        if item.get('source_class') not in ALLOWED_SOURCE_CLASSES:
            raise ValueError('Unknown source class: ' + str(item.get('source_class')))
        variants = item.get('variants')
        if not isinstance(variants, list) or not variants:
            raise ValueError('Each product needs variants')
        seen_variants = set()
        for variant in variants:
            vid = variant.get('variant_id')
            if not vid or vid in seen_variants:
                raise ValueError('Variant IDs must be unique within a product')
            seen_variants.add(vid)
            bust = variant.get('development_bust_cm')
            if bust is not None and (not isinstance(bust, (int, float)) or not 30 <= bust <= 200):
                raise ValueError('Development circumference is outside the contract bounds')
        capabilities = item.get('capabilities', {})
        if set(capabilities) != BOOLEAN_CAPABILITIES or not all(isinstance(v, bool) for v in capabilities.values()):
            raise ValueError('Capability flags are incomplete or non-boolean')
        grade = item.get('grade', {})
        material = item.get('material', {})
        actual = item.get('actual_garment_validation', {})
        if capabilities['pattern_faithful_grading'] and grade.get('status') != 'validated':
            raise ValueError('Pattern-faithful grading requires validated grade evidence')
        if capabilities['validated_drape'] and material.get('status') != 'validated':
            raise ValueError('Validated drape requires validated material evidence')
        if capabilities['actual_garment_fit'] or capabilities['size_recommendation']:
            if actual.get('status') != 'validated':
                raise ValueError('Fit/recommendation capability requires actual-garment validation')
        if actual.get('status') == 'validated':
            if not actual.get('physical_sample_id') or not actual.get('measurement_protocol') or not actual.get('material_match_verified'):
                raise ValueError('Actual-garment validation is missing physical provenance')
        if material.get('status') == 'validated' and actual.get('status') != 'validated' and capabilities['actual_garment_fit']:
            raise ValueError('Material evidence cannot substitute for actual-garment validation')
        if item.get('source_class') == 'artistic_proxy' and any(capabilities[k] for k in BOOLEAN_CAPABILITIES - {'visualization'}):
            raise ValueError('Artistic proxy may expose visualization only')
    return data
