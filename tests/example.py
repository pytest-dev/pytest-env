from __future__ import annotations

import os


class TestSimpleBehavior:
    def test_returns_value(self) -> None:
        assert os.environ.get("NEW_KEY") == "INI_VALUE_1"

    def test_returns_value_regardless_of_the_set_default_flag(self) -> None:
        assert os.environ.get("NEW_KEY_D") == "INI_VALUE_2"


class TestBehaviorGivenAlreadyExistingEnvironmentVariable:
    def test_without_default_flag_returns_new_value(self) -> None:
        assert os.environ.get("EXISTING_KEY") == "INI_VALUE_5"

    def test_with_default_flag_returns_existing_value(self) -> None:
        assert os.environ.get("EXISTING_KEY_D") == "EXISTING_VALUE_D"


class TestBehaviorGivenCurlyBraces:
    def test_given_no_raw_flag_returns_concatenated(self) -> None:
        assert os.environ.get("CURLY_BRACES_KEY") == "HELLO_WORLD_1"

    def test_given_raw_flag_returns_raw_value(self) -> None:
        assert os.environ.get("CURLY_BRACES_KEY_R") == "HELLO_{PLANET}_2"

    def test_given_references_to_ini_keys_takes_only_the_newest_and_only_applied_values(self) -> None:
        assert os.environ.get("WITH_INI_REFERENCES_KEY") == "INI_VALUE_1_INI_VALUE_5_EXISTING_VALUE_D"


class TestBehaviorGivenMultipleFlags:
    def test_given_two_flags_applies_both_of_them(self) -> None:
        assert os.environ.get("CURLY_BRACES_KEY_DR") == "HELLO_{PLANET}_3"

    def test_given_two_flags_of_reversed_order_applies_both_of_them(self) -> None:
        assert os.environ.get("CURLY_BRACES_KEY_RD") == "HELLO_{PLANET}_4"
