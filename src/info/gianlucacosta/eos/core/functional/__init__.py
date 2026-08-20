from collections.abc import Callable
from typing import Any

type AnyCallable = Callable[..., Any]

type Consumer[TInput] = Callable[[TInput], None]
type Producer[TOutput] = Callable[[], TOutput]
type Lender[TOutput] = Callable[[], TOutput]

type Unit = Callable[[], None]
type TriggerListener = Callable[[], None]

type Result[TOutput] = TOutput | Exception

type Mapper[TInput, TOutput] = Callable[[TInput], TOutput]
type Predicate[TInput] = Mapper[TInput, bool]

type ContinuationProvider = Producer[bool]
