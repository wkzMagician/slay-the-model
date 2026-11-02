"""Replay actual JAR/JDK outputs against production APIs, not a second model."""
import gzip
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, cast

import pytest

from utils.compatible_random import (
    GameRandom, JavaRandom48, RandomXS128, java_round_float,
)
from utils.seed import decode_seed, encode_seed, sterilize_seed, valid_seed_character

FIXTURE = Path(__file__).parent / "fixtures" / "original_random_vectors.jsonl.gz"
RAW = gzip.decompress(FIXTURE.read_bytes())
ROWS = [json.loads(line) for line in RAW.splitlines()]
CATEGORIES = sorted({row["category"] for row in ROWS})


def _value(value, expected):
    kind = expected["type"]
    if kind == "int64":
        assert str(value) == expected["decimal"]
    elif kind in ("float32", "float64"):
        assert struct.pack(">f" if kind == "float32" else ">d", value).hex() == expected["bits"]
    elif kind == "signed_bytes":
        assert value == expected["values"]
    else:
        assert value == expected["value"]


def _operation(rng, operation):
    operation = operation.split(":")[0]
    if operation == "randomLong()":
        return rng.random_long()
    kind, text = operation[:-1].split("(")

    def number(token):
        if token == "MIN":
            return -(1 << (31 if kind == "int" else 63))
        if token == "MAX":
            return (1 << (31 if kind == "int" else 63)) - 1
        if token in ("MIN_SUBNORMAL", "nextDown1"):
            return struct.unpack(">f", bytes.fromhex("00000001" if token == "MIN_SUBNORMAL" else "3f7fffff"))[0]
        return float(token.rstrip("f")) if kind in ("float", "boolean") else int(token)

    arguments = [number(field.split("=")[1]) for field in text.split(",") if field]
    method = {"int": rng.random_int, "long": rng.random_long_range,
              "float": rng.random_float, "boolean": rng.random_boolean}[kind]
    return method(*arguments)


def _raw(state):
    rng = RandomXS128(0)
    rng.restore_state(state)
    return rng


def test_reference_integrity():
    assert hashlib.sha256(RAW).hexdigest() == "5588bf214b82fadd045d7c540dc5ea5548bab2bae86c81291c1d6bc55991608c"
    assert len(ROWS) == len({row["id"] for row in ROWS}) == 5444


@pytest.mark.parametrize("category", CATEGORIES)
def test_original_utility_references(category):
    java_rngs = {}
    for row in ROWS:
        if row["category"] != category:
            continue
        try:
            _replay(row, java_rngs)
        except Exception as error:
            raise AssertionError(f"Original reference {row['id']}: {error}") from error


def _replay(row, java_rngs):
    category = row["category"]
    if category == "initial_state":
        assert GameRandom(int(row["seed"])).export_state() == row["state"]
    elif category in ("wrapper", "mixed"):
        rng = GameRandom.from_state(row["before"])
        if "exception" in row:
            with pytest.raises(ValueError):
                _operation(rng, row["operation"])
        else:
            _value(_operation(rng, row["operation"]), row["result"])
        assert rng.export_state() == row["after"]
    elif category == "counter_constructor":
        rng = GameRandom(int(row["seed"]), row["advance"])
        assert rng.export_state() == row["restored_before"]
        for a, b in zip(row["restored_tail"], row["stepped_tail"]):
            value = rng.random_long()
            _value(value, a)
            _value(value, b)
        assert rng.export_state() == row["restored_after"] == row["stepped_after"]
    elif category == "set_counter":
        rng = GameRandom.from_state(row["before"])
        rng.set_counter(row["target"])
        assert rng.export_state() == row["after"]
        _value(rng.random_long(), row["next"])
        assert rng.export_state() == row["final"]
    elif category == "copy":
        rng = GameRandom.from_state(row["before"])
        math_rng = _raw(row["controlled_MathUtils_before"])
        copied = rng.copy(math_rng)
        assert math_rng.export_state() == row["controlled_MathUtils_after"]
        assert copied.export_state() == row["copy_before"] == row["before"]
        for a, b in zip(row["original_tail"], row["copy_tail"]):
            _value(rng.random_long(), a)
            _value(copied.random_long(), b)
        assert rng.export_state() == row["original_after"]
        assert copied.export_state() == row["copy_after"]
    elif category == "raw_state_restore_fixture":
        rng = GameRandom.from_state(row["saved"])
        for a, b in zip(row["original_tail"], row["restored_tail"]):
            value = rng.random_int(99)
            _value(value, a)
            _value(value, b)
        assert rng.export_state() == row["original_after"] == row["restored_after"]
    elif category == "manufactured_API_state":
        if row["id"] == "zero_raw_state":
            raw = _raw(row["before"])
            _value(raw.next_long(), row["result"])
            assert raw.export_state() == row["after"]
        else:
            rng = GameRandom.from_state(row["before"])
            _value(rng.random_int(2147483646 if row["id"] == "forced_bounded_rejection" else 99), row["result"])
            assert rng.export_state() == row["after"]
            if "raw_nextLong_calls" in row:
                assert rng.raw.draws == row["raw_nextLong_calls"]
    elif category == "manufactured_raw_state_sequence":
        raw = _raw(row["before"])
        _value(raw.next_long(), row["result"])
        assert raw.export_state() == row["after"]
    elif category == "xs128":
        raw = _raw(row["before"])
        operation = row["operation"]

        def invoke():
            name, args = operation[:-1].split("(")
            if name == "nextBytes":
                return raw.next_bytes(11)
            method = {"nextInt": raw.next_int, "nextLong": raw.next_long,
                      "nextFloat": raw.next_float, "nextDouble": raw.next_double,
                      "nextBoolean": raw.next_boolean}[name]
            return method(int(args)) if args else method()

        if "exception" in row["result"]:
            with pytest.raises(ValueError):
                invoke()
        else:
            _value(invoke(), row["result"])
        assert raw.export_state() == row["after"]
        assert raw.draws == row["raw_nextLong_calls"]
    elif category == "shuffle":
        rng = GameRandom.from_state(row["before"])
        values = list(range(row["size"]))
        child = rng.shuffle(values)
        assert str(child) == row["child_seed"]
        assert rng.export_state() == row["after"]
        assert values == row["result"]
        java = JavaRandom48(child)
        other = list(range(row["size"]))
        java.shuffle(other)
        assert other == values and java.draws == row["java_next_calls"]
    elif category == "java48_bounded":
        key = row["seed"], row["bound"]
        java = java_rngs.setdefault(key, JavaRandom48(int(row["seed"])))
        assert java.draws == row["next_calls_before"]
        assert java.next_int(row["bound"]) == row["result"]
        assert java.draws == row["next_calls_after"]
    elif category == "seed_roundtrip":
        assert encode_seed(int(row["internal_seed"])) == row["code"]
        assert str(decode_seed(row["code"])) == row["decoded"] == row["internal_seed"]
    elif category == "seed_input":
        text = row["input"]
        if text is None:
            for function in (sterilize_seed, decode_seed):
                with pytest.raises((TypeError, AttributeError)):
                    function(cast(Any, text))
        else:
            assert sterilize_seed(text) == row["sterilized"]
            assert str(decode_seed(text)) == row["raw_decoded"]
            assert str(decode_seed(sterilize_seed(text))) == row["normalized_decoded"]
    elif category == "seed_character":
        if row["input"] is None:
            with pytest.raises((TypeError, AttributeError)):
                valid_seed_character(row["input"])
        else:
            assert valid_seed_character(row["input"]) == row["result"]
    elif category == "source_shaped_float_round_example":
        rng = GameRandom.from_state(row["before"])
        value = rng.random_float(45, 55)
        _value(value, row["sample"])
        assert java_round_float(value) == row["rounded"]
        assert rng.export_state() == row["after"]
    elif category == "round_boundary":
        value = struct.unpack(">f", bytes.fromhex(row["input"]["bits"]))[0]
        assert java_round_float(value) == row["result"]
    else:
        pytest.fail(f"Unhandled category: {category}")
