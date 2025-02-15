# Test File Expectations
import os

import pytest

import great_expectations as gx
from great_expectations.data_context.util import file_relative_path


@pytest.mark.unit
def test_expect_file_hash_to_equal():
    # Test for non-existent file
    fake_file = gx.data_asset.FileDataAsset(file_path="abc")

    with pytest.raises(IOError):
        fake_file.expect_file_hash_to_equal(value="abc")

    # Test for non-existent hash algorithm
    titanic_path = file_relative_path(__file__, "../test_sets/Titanic.csv")
    titanic_file = gx.data_asset.FileDataAsset(titanic_path)

    with pytest.raises(ValueError):
        titanic_file.expect_file_hash_to_equal(hash_alg="md51", value="abc")

    # Test non-matching hash value
    fake_hash_value = titanic_file.expect_file_hash_to_equal(value="abc")
    assert not fake_hash_value.success

    # Test matching hash value with default algorithm
    hash_value = "63188432302f3a6e8c9e9c500ff27c8a"
    good_hash_default_alg = titanic_file.expect_file_hash_to_equal(value=hash_value)
    assert good_hash_default_alg.success

    # Test matching hash value with specified algorithm
    hash_value = "f89f46423b017a1fc6a4059d81bddb3ff64891e3c81250fafad6f3b3113ecc9b"
    good_hash_new_alg = titanic_file.expect_file_hash_to_equal(
        value=hash_value, hash_alg="sha256"
    )
    assert good_hash_new_alg.success


@pytest.mark.unit
def test_expect_file_size_to_be_between():
    fake_file = gx.data_asset.FileDataAsset("abc")

    # Test for non-existent file
    with pytest.raises(OSError):
        fake_file.expect_file_size_to_be_between(0, 10000)

    titanic_path = file_relative_path(__file__, "../test_sets/Titanic.csv")
    titanic_file = gx.data_asset.FileDataAsset(titanic_path)

    # Test minsize not an integer
    with pytest.raises(ValueError):
        titanic_file.expect_file_size_to_be_between("a", 10000)

    # Test maxsize not an integer
    with pytest.raises(ValueError):
        titanic_file.expect_file_size_to_be_between(0, "10000a")

    # Test minsize less than 0
    with pytest.raises(ValueError):
        titanic_file.expect_file_size_to_be_between(-1, 10000)

    # Test maxsize less than 0
    with pytest.raises(ValueError):
        titanic_file.expect_file_size_to_be_between(0, -1)

    # Test minsize > maxsize
    with pytest.raises(ValueError):
        titanic_file.expect_file_size_to_be_between(10000, 0)

    # Test file size not in range
    bad_range = titanic_file.expect_file_size_to_be_between(0, 10000)
    assert not bad_range.success

    # Test file size in range
    lower, upper = (70000, 72000)
    good_range = titanic_file.expect_file_size_to_be_between(lower, upper)
    assert good_range.success


@pytest.mark.unit
def test_expect_file_to_exist():
    # Test for non-existent file
    fake_file = gx.data_asset.FileDataAsset("abc")
    fake_file_existence = fake_file.expect_file_to_exist()
    assert not fake_file_existence.success

    # Test for existing file
    real_file = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/Titanic.csv")
    )
    real_file_existence = real_file.expect_file_to_exist()
    assert real_file_existence.success


@pytest.mark.unit
def test_expect_file_to_have_valid_table_header():
    # Test for non-existent file
    fake_file = gx.data_asset.FileDataAsset("abc")
    with pytest.raises(IOError):
        fake_file.expect_file_to_have_valid_table_header(regex="")

    # Test for non-unique column names
    invalid_header_dat = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/same_column_names.csv")
    )
    invalid_header_dat_expectation = (
        invalid_header_dat.expect_file_to_have_valid_table_header(regex=r"\|", skip=2)
    )
    assert not invalid_header_dat_expectation.success

    # Test for unique column names
    valid_header_dat = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/Titanic.csv")
    )
    valid_header_dat_expectation = (
        valid_header_dat.expect_file_to_have_valid_table_header(regex=",")
    )
    assert valid_header_dat_expectation.success


@pytest.mark.unit
def test_expect_file_to_be_valid_json():
    # Test for non-existent file
    fake_file = gx.data_asset.FileDataAsset("abc")
    with pytest.raises(IOError):
        fake_file.expect_file_to_be_valid_json()

    # Test invalid JSON file
    invalid_JSON_file = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/invalid_json_file.json")
    )
    invalid_JSON_expectation = invalid_JSON_file.expect_file_to_be_valid_json()
    assert not invalid_JSON_expectation.success

    # Test valid JSON file
    valid_JSON_file = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/titanic_expectations.json")
    )
    valid_JSON_expectation = valid_JSON_file.expect_file_to_be_valid_json()
    assert valid_JSON_expectation.success

    # Test valid JSON file with non-matching schema
    schema_file = file_relative_path(__file__, "../test_sets/sample_schema.json")
    test_file = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/json_test1_against_schema.json")
    )
    test_file_expectation = test_file.expect_file_to_be_valid_json(schema=schema_file)
    assert not test_file_expectation.success

    # Test valid JSON file with valid schema
    test_file = gx.data_asset.FileDataAsset(
        file_relative_path(__file__, "../test_sets/json_test2_against_schema.json")
    )
    schema_file = file_relative_path(__file__, "../test_sets/sample_schema.json")
    test_file_expectation = test_file.expect_file_to_be_valid_json(schema=schema_file)
    assert test_file_expectation.success
