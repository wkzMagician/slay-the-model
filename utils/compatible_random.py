"""Explicit original-game RNG APIs. Production stream migration is separate.

Integer bounds are inclusive on GameRandom, exclusive on the raw generators.
Float operations round at each Java float operation, not just at the end.
"""
import math
import struct
from typing import Mapping, MutableSequence, TypeVar

from utils.seed import MASK64, signed64

T = TypeVar("T")


def signed32(value: int) -> int:
    value &= (1 << 32) - 1
    return value if value < (1 << 31) else value - (1 << 32)


def float32(value: float) -> float:
    try:
        return struct.unpack(">f", struct.pack(">f", value))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


def java_round_float(value: float) -> int:
    value = float32(value)
    if math.isnan(value):
        return 0
    if value >= (1 << 31) - 1:
        return (1 << 31) - 1
    if value <= -(1 << 31):
        return -(1 << 31)
    return math.floor(value + 0.5)


def _mix(value: int) -> int:
    value &= MASK64
    value ^= value >> 33
    value = value * 0xff51afd7ed558ccd & MASK64
    value ^= value >> 33
    value = value * 0xc4ceb9fe1a85ec53 & MASK64
    return (value ^ (value >> 33)) & MASK64


class RandomXS128:
    def __init__(self, seed: int):
        self.draws = 0
        self.set_seed(seed)

    def set_seed(self, seed: int) -> None:
        seed = signed64(seed)
        self.state0 = _mix(seed if seed else -(1 << 63))
        self.state1 = _mix(self.state0)

    def export_state(self) -> dict[str, str]:
        return {"state0": str(signed64(self.state0)), "state1": str(signed64(self.state1))}

    def restore_state(self, state: Mapping[str, str | int]) -> None:
        self.state0 = int(state["state0"]) & MASK64
        self.state1 = int(state["state1"]) & MASK64

    def next_long(self, bound: int | None = None) -> int:
        if bound is not None:
            if not 0 < bound < (1 << 63):
                raise ValueError("n must be positive signed64")
            while True:
                bits = (self.next_long() & MASK64) >> 1
                value = bits % bound
                if signed64(bits - value + bound - 1) >= 0:
                    return value
        a, b = self.state0, self.state1
        a = (a ^ (a << 23)) & MASK64
        self.state0 = b
        self.state1 = (a ^ b ^ (a >> 17) ^ (b >> 26)) & MASK64
        self.draws += 1
        return signed64(self.state1 + b)

    def next_int(self, bound: int | None = None) -> int:
        return signed32(self.next_long()) if bound is None else int(self.next_long(bound))

    def next_float(self) -> float:
        return float32(((self.next_long() & MASK64) >> 40) * 2.0**-24)

    def next_double(self) -> float:
        return ((self.next_long() & MASK64) >> 11) * 2.0**-53

    def next_boolean(self) -> bool:
        return bool(self.next_long() & 1)

    def next_bytes(self, length: int) -> list[int]:
        if length < 0:
            raise ValueError("length must be nonnegative")
        result = [0] * length
        index = length
        while index:
            word = self.next_long()
            for _ in range(min(index, 8)):
                index -= 1
                byte = word & 255
                result[index] = byte if byte < 128 else byte - 256
                word >>= 8
        return result


class GameRandom:
    """Original Random wrapper with explicit methods for Java overloads."""
    def __init__(self, seed: int, counter: int = 0):
        self.raw = RandomXS128(seed)
        self.counter = 0
        for _ in range(max(0, signed32(counter))):
            self.random_int(999)

    def _advance(self) -> None:
        self.counter = signed32(self.counter + 1)

    def export_state(self) -> dict[str, str | int]:
        return {**self.raw.export_state(), "counter": self.counter}

    def restore_state(self, state: Mapping[str, str | int]) -> None:
        self.raw.restore_state(state)
        self.counter = signed32(int(state["counter"]))

    @classmethod
    def from_state(cls, state: Mapping[str, str | int]) -> "GameRandom":
        result = cls(0)
        result.restore_state(state)
        return result

    def copy(self, math_rng: RandomXS128 | None = None) -> "GameRandom":
        """Copy gameplay state without implicit entropy.

        Supply the separate MathUtils RNG to reproduce Java copy's discarded
        default-constructor draws. No hidden global RNG is introduced here.
        """
        if math_rng is not None:
            math_rng.next_double()  # MathUtils.random(9999L)
            math_rng.next_int(100)  # MathUtils.random(99)
        return self.from_state(self.export_state())

    def set_counter(self, target: int) -> None:
        count = signed32(signed32(target) - self.counter)
        if self.counter < signed32(target):
            for _ in range(max(0, count)):
                self.random_boolean()

    def random_int(self, start: int, end: int | None = None) -> int:
        self._advance()
        if end is None:
            start, end = 0, start
        return signed32(start + self.raw.next_int(signed32(end - start + 1)))

    def random_long(self) -> int:
        self._advance()
        return self.raw.next_long()

    def random_long_range(self, start: int, end: int | None = None) -> int:
        self._advance()
        if end is None:
            start, end = 0, start
        value = self.raw.next_double() * float(signed64(end - start))
        cast = max(-(1 << 63), min((1 << 63) - 1, int(value)))
        return signed64(start + cast)

    def random_float(self, start: float | None = None, end: float | None = None) -> float:
        self._advance()
        value = self.raw.next_float()
        if start is None:
            return value
        if end is None:
            return float32(value * float32(start))
        start, end = float32(start), float32(end)
        return float32(start + float32(value * float32(end - start)))

    def random_boolean(self, chance: float | None = None) -> bool:
        self._advance()
        return self.raw.next_boolean() if chance is None else self.raw.next_float() < float32(chance)

    def shuffle(self, values: MutableSequence[T]) -> int:
        """Consume a parent long even for empty/singleton lists; return child seed."""
        seed = self.random_long()
        JavaRandom48(seed).shuffle(values)
        return seed


class JavaRandom48:
    def __init__(self, seed: int):
        self.state = (seed ^ 0x5deece66d) & ((1 << 48) - 1)
        self.draws = 0

    def next_bits(self, bits: int) -> int:
        if not 1 <= bits <= 32:
            raise ValueError("bits must be in 1..32")
        self.state = (self.state * 0x5deece66d + 11) & ((1 << 48) - 1)
        self.draws += 1
        return self.state >> (48 - bits)

    def next_int(self, bound: int) -> int:
        if not 0 < bound < (1 << 31):
            raise ValueError("bound must be positive signed32")
        if bound & (bound - 1) == 0:
            return (bound * self.next_bits(31)) >> 31
        while True:
            bits = self.next_bits(31)
            value = bits % bound
            if signed32(bits - value + bound - 1) >= 0:
                return value

    def shuffle(self, values: MutableSequence[T]) -> None:
        for size in range(len(values), 1, -1):
            index = self.next_int(size)
            values[size - 1], values[index] = values[index], values[size - 1]
