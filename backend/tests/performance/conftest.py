from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
import gc
import time
import tracemalloc
from typing import Any

import pytest


@dataclass
class TimingResult:
    """Result of a timing measurement"""

    name: str
    iterations: int
    total_time_ns: int
    min_time_ns: int
    max_time_ns: int
    avg_time_ns: float

    @property
    def total_ms(self) -> float:
        return self.total_time_ns / 1_000_000

    @property
    def avg_ms(self) -> float:
        return self.avg_time_ns / 1_000_000

    @property
    def avg_us(self) -> float:
        return self.avg_time_ns / 1_000

    @property
    def min_us(self) -> float:
        return self.min_time_ns / 1_000

    @property
    def max_us(self) -> float:
        return self.max_time_ns / 1_000

    def __str__(self) -> str:
        return (
            f"{self.name}: "
            f"avg={self.avg_us:.1f}µs, "
            f"min={self.min_us:.1f}µs, "
            f"max={self.max_us:.1f}µs "
            f"({self.iterations} iterations)"
        )


@dataclass
class MemoryResult:
    """Result of a memory measurement"""

    name: str
    peak_bytes: int
    allocated_bytes: int
    freed_bytes: int
    net_bytes: int
    allocations: int

    @property
    def peak_kb(self) -> float:
        return self.peak_bytes / 1024

    @property
    def allocated_kb(self) -> float:
        return self.allocated_bytes / 1024

    @property
    def net_kb(self) -> float:
        return self.net_bytes / 1024

    def __str__(self) -> str:
        return (
            f"{self.name}: "
            f"peak={self.peak_kb:.1f}KB, "
            f"allocated={self.allocated_kb:.1f}KB, "
            f"net={self.net_kb:.1f}KB, "
            f"allocations={self.allocations}"
        )


@dataclass
class BenchmarkResult:
    """Combined timing and memory results"""

    timing: TimingResult
    memory: MemoryResult
    gc_collections: dict[int, int] = field(default_factory=dict)

    def __str__(self) -> str:
        gc_str = ", ".join(f"gen{k}={v}" for k, v in self.gc_collections.items())
        return f"{self.timing}\n{self.memory}\nGC: {gc_str}"


class PerfTimer:
    """High-precision timer for performance measurements"""

    @staticmethod
    def time_function(
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10,
        name: str = "unnamed",
    ) -> TimingResult:
        """Time a function over multiple iterations"""
        # Warmup
        for _ in range(warmup):
            func()

        # Force GC before timing
        gc.collect()
        gc.collect()
        gc.collect()

        times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            func()
            end = time.perf_counter_ns()
            times.append(end - start)

        return TimingResult(
            name=name,
            iterations=iterations,
            total_time_ns=sum(times),
            min_time_ns=min(times),
            max_time_ns=max(times),
            avg_time_ns=sum(times) / len(times),
        )

    @staticmethod
    async def time_async_function(
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10,
        name: str = "unnamed",
    ) -> TimingResult:
        """Time an async function over multiple iterations"""
        # Warmup
        for _ in range(warmup):
            await func()

        gc.collect()
        gc.collect()
        gc.collect()

        times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            await func()
            end = time.perf_counter_ns()
            times.append(end - start)

        return TimingResult(
            name=name,
            iterations=iterations,
            total_time_ns=sum(times),
            min_time_ns=min(times),
            max_time_ns=max(times),
            avg_time_ns=sum(times) / len(times),
        )


class MemoryProfiler:
    """Memory profiling utilities"""

    @staticmethod
    @contextmanager
    def profile(name: str = "unnamed") -> Generator[dict[str, Any]]:
        """Context manager for memory profiling"""
        gc.collect()
        gc.collect()
        gc.collect()

        tracemalloc.start()
        gc_before = {i: gc.get_count()[i] for i in range(3)}

        result: dict[str, Any] = {}

        try:
            yield result
        finally:
            snapshot = tracemalloc.take_snapshot()
            tracemalloc.stop()

            gc_after = {i: gc.get_count()[i] for i in range(3)}

            stats = snapshot.statistics("lineno")
            total_allocated = sum(stat.size for stat in stats)
            total_count = sum(stat.count for stat in stats)

            result["memory"] = MemoryResult(
                name=name,
                peak_bytes=total_allocated,
                allocated_bytes=total_allocated,
                freed_bytes=0,
                net_bytes=total_allocated,
                allocations=total_count,
            )
            result["gc_delta"] = {i: gc_after[i] - gc_before[i] for i in range(3)}
            result["top_allocations"] = stats[:10]

    @staticmethod
    def profile_function(
        func: Callable[[], Any], iterations: int = 100, name: str = "unnamed"
    ) -> MemoryResult:
        """Profile memory usage of a function over multiple iterations"""
        gc.collect()
        gc.collect()
        gc.collect()

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        for _ in range(iterations):
            func()

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Compare snapshots
        top_stats = snapshot2.compare_to(snapshot1, "lineno")

        total_allocated = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        total_freed = abs(sum(stat.size_diff for stat in top_stats if stat.size_diff < 0))
        net = sum(stat.size_diff for stat in top_stats)
        allocations = sum(stat.count_diff for stat in top_stats if stat.count_diff > 0)

        return MemoryResult(
            name=name,
            peak_bytes=total_allocated,
            allocated_bytes=total_allocated,
            freed_bytes=total_freed,
            net_bytes=net,
            allocations=allocations,
        )


class Benchmark:
    """Combined timing and memory benchmarking"""

    @staticmethod
    def run(
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10,
        name: str = "unnamed",
    ) -> BenchmarkResult:
        """Run a complete benchmark with timing and memory profiling"""
        # First, do timing (without memory overhead)
        timing = PerfTimer.time_function(func, iterations, warmup, name)

        # Then do memory profiling
        gc.collect()
        gc.collect()
        gc.collect()

        gc_before = [gc.get_count()[i] for i in range(3)]

        memory = MemoryProfiler.profile_function(func, iterations, name)

        gc.collect()
        gc_after = [gc.get_count()[i] for i in range(3)]

        gc_collections = {i: gc_after[i] - gc_before[i] for i in range(3)}

        return BenchmarkResult(timing=timing, memory=memory, gc_collections=gc_collections)

    @staticmethod
    async def run_async(
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10,
        name: str = "unnamed",
    ) -> BenchmarkResult:
        """Run a complete benchmark for async functions"""
        timing = await PerfTimer.time_async_function(func, iterations, warmup, name)

        gc.collect()
        gc.collect()
        gc.collect()

        gc_before = [gc.get_count()[i] for i in range(3)]

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        for _ in range(iterations):
            await func()

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        top_stats = snapshot2.compare_to(snapshot1, "lineno")

        total_allocated = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        total_freed = abs(sum(stat.size_diff for stat in top_stats if stat.size_diff < 0))
        net = sum(stat.size_diff for stat in top_stats)
        allocations = sum(stat.count_diff for stat in top_stats if stat.count_diff > 0)

        memory = MemoryResult(
            name=name,
            peak_bytes=total_allocated,
            allocated_bytes=total_allocated,
            freed_bytes=total_freed,
            net_bytes=net,
            allocations=allocations,
        )

        gc.collect()
        gc_after = [gc.get_count()[i] for i in range(3)]

        gc_collections = {i: gc_after[i] - gc_before[i] for i in range(3)}

        return BenchmarkResult(timing=timing, memory=memory, gc_collections=gc_collections)


# Pytest fixtures
@pytest.fixture
def perf_timer():
    """Provide PerfTimer for tests"""
    return PerfTimer()


@pytest.fixture
def memory_profiler():
    """Provide MemoryProfiler for tests"""
    return MemoryProfiler()


@pytest.fixture
def benchmark():
    """Provide Benchmark for tests"""
    return Benchmark()


class PerfAssert:
    """Assertion helpers for performance testing"""

    @staticmethod
    def timing_under(result: TimingResult, max_us: float, msg: str = ""):
        """Assert average timing is under threshold in microseconds"""
        assert result.avg_us < max_us, (
            f"{msg}: {result.name} took {result.avg_us:.1f}µs, expected < {max_us}µs"
        )

    @staticmethod
    def timing_under_ms(result: TimingResult, max_ms: float, msg: str = ""):
        """Assert average timing is under threshold in milliseconds"""
        assert result.avg_ms < max_ms, (
            f"{msg}: {result.name} took {result.avg_ms:.2f}ms, expected < {max_ms}ms"
        )

    @staticmethod
    def memory_under(result: MemoryResult, max_kb: float, msg: str = ""):
        """Assert memory allocation is under threshold in KB"""
        assert result.allocated_kb < max_kb, (
            f"{msg}: {result.name} allocated {result.allocated_kb:.1f}KB, expected < {max_kb}KB"
        )

    @staticmethod
    def allocations_under(result: MemoryResult, max_allocs: int, msg: str = ""):
        """Assert number of allocations is under threshold"""
        assert result.allocations < max_allocs, (
            f"{msg}: {result.name} made {result.allocations} allocations, expected < {max_allocs}"
        )

    @staticmethod
    def gc_collections_under(result: BenchmarkResult, max_gen0: int, msg: str = ""):
        """Assert GC collections are under threshold"""
        gen0 = result.gc_collections.get(0, 0)
        assert gen0 < max_gen0, (
            f"{msg}: {result.timing.name} triggered {gen0} gen0 GC, expected < {max_gen0}"
        )
