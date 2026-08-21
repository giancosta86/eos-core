from dataclasses import dataclass

from ..logic.ranges import InclusiveRange


@dataclass
class AgentConfigurationForTesting:
    timeout_seconds_range: InclusiveRange
    operation_sleep_seconds: float
    timeout_factor: int = 2


FAST_AGENT_CONFIGURATION = AgentConfigurationForTesting(
    operation_sleep_seconds=0.001,
    timeout_seconds_range=InclusiveRange(lower=0.001, upper=0.002),
)


SLOW_AGENT_CONFIGURATION = AgentConfigurationForTesting(
    operation_sleep_seconds=0.02,
    timeout_seconds_range=InclusiveRange(lower=0.05, upper=0.5),
)
