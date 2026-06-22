"""Unit tests for formalwear business rules (hollow_to_hem default, model_try_on default)."""
import pytest

from src.giraffe_jp.schemas import (
    HOLLOW_TO_HEM_CATEGORIES,
    VALID_PRODUCT_CATEGORIES,
    FormalwearOrderProfileCreate,
)


def _make_profile(product_category: str, **kwargs) -> dict:
    data = {
        "project_id": "00000000-0000-0000-0000-000000000001",
        "product_category": product_category,
        "occasion": "Wedding ceremony",
    }
    data.update(kwargs)
    return data


def test_hollow_to_hem_categories_set():
    assert "FORMAL_DRESS" in HOLLOW_TO_HEM_CATEGORIES
    assert "BRIDALWEAR" in HOLLOW_TO_HEM_CATEGORIES
    assert "LIGHT_WEDDING_DRESS" in HOLLOW_TO_HEM_CATEGORIES
    assert "WOMENS_SUIT" not in HOLLOW_TO_HEM_CATEGORIES
    assert "RECEPTION_DRESS" not in HOLLOW_TO_HEM_CATEGORIES


def test_valid_product_categories_set():
    assert VALID_PRODUCT_CATEGORIES == {
        "FORMAL_DRESS",
        "WOMENS_SUIT",
        "BRIDALWEAR",
        "LIGHT_WEDDING_DRESS",
        "RECEPTION_DRESS",
    }


def test_invalid_product_category_raises():
    import uuid
    with pytest.raises(Exception):
        FormalwearOrderProfileCreate(
            project_id=uuid.uuid4(),
            product_category="EVENING_GOWN",
            occasion="Party",
        )


def test_model_try_on_required_defaults_to_true():
    import uuid
    profile = FormalwearOrderProfileCreate(
        project_id=uuid.uuid4(),
        product_category="BRIDALWEAR",
        occasion="Wedding",
    )
    assert profile.model_try_on_required is True


def test_local_alteration_possible_defaults_to_true():
    import uuid
    profile = FormalwearOrderProfileCreate(
        project_id=uuid.uuid4(),
        product_category="WOMENS_SUIT",
        occasion="Business presentation",
    )
    assert profile.local_alteration_possible is True


def test_hollow_to_hem_not_set_by_schema_for_non_dress():
    import uuid
    profile = FormalwearOrderProfileCreate(
        project_id=uuid.uuid4(),
        product_category="WOMENS_SUIT",
        occasion="Meeting",
    )
    # Schema leaves it as None; service will set it to False
    assert profile.hollow_to_hem_required is None


def test_hollow_to_hem_explicit_false_preserved():
    import uuid
    profile = FormalwearOrderProfileCreate(
        project_id=uuid.uuid4(),
        product_category="BRIDALWEAR",
        occasion="Wedding",
        hollow_to_hem_required=False,
    )
    assert profile.hollow_to_hem_required is False


def test_hollow_to_hem_explicit_true_preserved_for_non_dress():
    import uuid
    profile = FormalwearOrderProfileCreate(
        project_id=uuid.uuid4(),
        product_category="WOMENS_SUIT",
        occasion="Meeting",
        hollow_to_hem_required=True,
    )
    assert profile.hollow_to_hem_required is True
