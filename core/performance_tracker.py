"""
Performance Tracker
Tracks timing and resource metrics for orchestrator performance analysis
Phase 1 Local Optimization - Performance Instrumentation
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PhaseMetrics:
    """Metrics for a single processing phase"""
    name: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_seconds: float = 0.0
    files_processed: int = 0
    files_failed: int = 0
    metadata: Dict = field(default_factory=dict)

    def start(self):
        """Start timing this phase"""
        self.start_time = time.time()

    def end(self):
        """End timing this phase"""
        self.end_time = time.time()
        if self.start_time:
            self.duration_seconds = self.end_time - self.start_time

    def get_duration_formatted(self) -> str:
        """Get human-readable duration"""
        if self.duration_seconds < 60:
            return f"{self.duration_seconds:.1f}s"
        elif self.duration_seconds < 3600:
            minutes = self.duration_seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = self.duration_seconds / 3600
            return f"{hours:.1f}h"


@dataclass
class BatchMetrics:
    """Metrics for a single batch"""
    batch_number: int
    files: List[str] = field(default_factory=list)
    total_audio_minutes: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_seconds: float = 0.0
    successes: int = 0
    failures: int = 0

    def start(self):
        """Start timing this batch"""
        self.start_time = time.time()

    def end(self):
        """End timing this batch"""
        self.end_time = time.time()
        if self.start_time:
            self.duration_seconds = self.end_time - self.start_time


class PerformanceTracker:
    """
    Tracks performance metrics for the recording orchestrator
    Provides clean, actionable summaries for performance analysis
    """

    def __init__(self):
        self.session_start_time = time.time()
        self.phases: Dict[str, PhaseMetrics] = {}
        self.batches: List[BatchMetrics] = []
        self.baseline_metrics: Dict = {}

    def start_phase(self, phase_name: str):
        """Start tracking a processing phase"""
        if phase_name not in self.phases:
            self.phases[phase_name] = PhaseMetrics(name=phase_name)
        self.phases[phase_name].start()

    def end_phase(self, phase_name: str, files_processed: int = 0, files_failed: int = 0, **metadata):
        """End tracking a processing phase"""
        if phase_name in self.phases:
            self.phases[phase_name].end()
            self.phases[phase_name].files_processed = files_processed
            self.phases[phase_name].files_failed = files_failed
            self.phases[phase_name].metadata.update(metadata)

    def add_batch_metrics(self, batch: BatchMetrics):
        """Add metrics for a completed batch"""
        self.batches.append(batch)

    def set_baseline(self, baseline: Dict):
        """Set baseline metrics for comparison"""
        self.baseline_metrics = baseline

    def get_total_duration(self) -> float:
        """Get total session duration in seconds"""
        return time.time() - self.session_start_time

    def generate_report(self) -> str:
        """
        Generate a clean, actionable performance summary
        Focused on business impact, not engineering details
        """
        total_duration = self.get_total_duration()

        # Calculate summary statistics
        total_files = sum(p.files_processed for p in self.phases.values())
        total_failed = sum(p.files_failed for p in self.phases.values())
        success_rate = ((total_files - total_failed) / total_files * 100) if total_files > 0 else 0

        # Build report
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📊 PERFORMANCE SUMMARY")
        report_lines.append("=" * 60)
        report_lines.append("")

        # Overall metrics
        report_lines.append("⏱️  OVERALL PERFORMANCE")
        report_lines.append(f"   Total Duration: {self._format_duration(total_duration)}")
        report_lines.append(f"   Files Processed: {total_files - total_failed}/{total_files}")
        report_lines.append(f"   Success Rate: {success_rate:.0f}%")
        report_lines.append("")

        # Phase breakdown
        if self.phases:
            report_lines.append("📈 PHASE BREAKDOWN")
            for phase_name in ['detect', 'validate', 'transcribe', 'process', 'archive', 'cleanup']:
                if phase_name in self.phases:
                    phase = self.phases[phase_name]
                    percentage = (phase.duration_seconds / total_duration * 100) if total_duration > 0 else 0
                    report_lines.append(f"   {phase_name.capitalize()}: {phase.get_duration_formatted()} ({percentage:.0f}%)")

                    # Add phase-specific details
                    if phase.metadata:
                        for key, value in phase.metadata.items():
                            if key not in ['start_time', 'end_time']:
                                report_lines.append(f"      └─ {key}: {value}")
            report_lines.append("")

        # Batch analysis
        if self.batches:
            report_lines.append("🔄 BATCH ANALYSIS")
            total_batch_time = sum(b.duration_seconds for b in self.batches)
            avg_batch_time = total_batch_time / len(self.batches) if self.batches else 0

            report_lines.append(f"   Total Batches: {len(self.batches)}")
            report_lines.append(f"   Average Batch Time: {self._format_duration(avg_batch_time)}")
            report_lines.append("")

            # Show individual batches if there are performance outliers
            batch_times = [b.duration_seconds for b in self.batches]
            if batch_times and max(batch_times) > avg_batch_time * 1.5:
                report_lines.append("   ⚠️  Batch Performance Outliers:")
                for batch in self.batches:
                    if batch.duration_seconds > avg_batch_time * 1.5:
                        report_lines.append(f"      Batch {batch.batch_number}: {self._format_duration(batch.duration_seconds)} ({len(batch.files)} files, {batch.total_audio_minutes:.1f}min audio)")
                report_lines.append("")

        # Baseline comparison
        if self.baseline_metrics:
            report_lines.append("📊 BASELINE COMPARISON")
            baseline_duration = self.baseline_metrics.get('duration_minutes', 0) * 60
            if baseline_duration > 0:
                improvement = ((baseline_duration - total_duration) / baseline_duration) * 100
                speedup = baseline_duration / total_duration if total_duration > 0 else 0

                report_lines.append(f"   Baseline Duration: {self._format_duration(baseline_duration)}")
                report_lines.append(f"   Current Duration: {self._format_duration(total_duration)}")
                report_lines.append(f"   Improvement: {improvement:.0f}% faster")
                report_lines.append(f"   Speedup: {speedup:.1f}x")

                # Visual indicator
                if speedup >= 5:
                    report_lines.append("   ✅ TARGET ACHIEVED: 5-10x improvement!")
                elif speedup >= 3:
                    report_lines.append("   ⚠️  Good progress, but below 5x target")
                else:
                    report_lines.append("   ❌ Below target, needs further optimization")
            report_lines.append("")

        # Bottleneck analysis
        if self.phases:
            slowest_phase = max(self.phases.values(), key=lambda p: p.duration_seconds)
            report_lines.append("🎯 BOTTLENECK ANALYSIS")
            report_lines.append(f"   Slowest Phase: {slowest_phase.name.capitalize()} ({slowest_phase.get_duration_formatted()})")

            # Provide actionable recommendations
            if slowest_phase.name == 'transcribe':
                report_lines.append("   💡 Recommendation: Consider Groq cloud migration (Phase 2)")
            elif slowest_phase.name == 'process':
                report_lines.append("   💡 Recommendation: Optimize AI analysis or enable pipelining")
            elif slowest_phase.name == 'detect':
                report_lines.append("   💡 Recommendation: Check USB I/O or staging configuration")

        report_lines.append("")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def save_report(self, filepath: str):
        """Save performance report to file"""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            f.write(report)
            f.write("\n\n")
            f.write("=" * 60)
            f.write("\nDETAILED METRICS (for engineering analysis)\n")
            f.write("=" * 60)
            f.write("\n\n")

            # Write detailed phase data
            for phase_name, phase in self.phases.items():
                f.write(f"\n{phase_name.upper()}:\n")
                f.write(f"  Duration: {phase.duration_seconds:.2f}s\n")
                f.write(f"  Files Processed: {phase.files_processed}\n")
                f.write(f"  Files Failed: {phase.files_failed}\n")
                if phase.metadata:
                    f.write(f"  Metadata: {phase.metadata}\n")

            # Write detailed batch data
            if self.batches:
                f.write("\n\nBATCH DETAILS:\n")
                for batch in self.batches:
                    f.write(f"\nBatch {batch.batch_number}:\n")
                    f.write(f"  Files: {', '.join(batch.files)}\n")
                    f.write(f"  Audio Duration: {batch.total_audio_minutes:.2f}m\n")
                    f.write(f"  Processing Duration: {batch.duration_seconds:.2f}s\n")
                    f.write(f"  Successes: {batch.successes}\n")
                    f.write(f"  Failures: {batch.failures}\n")
