import SwiftUI
import Charts

struct AnalyticsView: View {
    @StateObject private var vm: AnalyticsViewModel
    @State private var selectedRun: RunWorkout?

    init(healthKit: HealthKitService) {
        _vm = StateObject(wrappedValue: AnalyticsViewModel(healthKit: healthKit))
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    weeklyVolumeChart
                    paceTrendChart
                    runHistoryList
                }
                .padding()
            }
            .navigationTitle("Analytics")
            .task { await vm.load() }
            .refreshable { await vm.load() }
            .sheet(item: $selectedRun) { run in
                RunDetailView(run: run)
            }
        }
    }

    // MARK: - Weekly Volume Chart

    private var weeklyVolumeChart: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Weekly Volume")
                .font(.headline)
            if vm.weeklyVolumes.isEmpty {
                chartPlaceholder
            } else {
                Chart(vm.weeklyVolumes) { week in
                    BarMark(
                        x: .value("Week", week.label),
                        y: .value("km", week.totalKm)
                    )
                    .foregroundStyle(
                        week.weekStart >= Date().startOfWeek()
                            ? Color.blue
                            : Color.blue.opacity(0.45)
                    )
                    .cornerRadius(6)
                }
                .frame(height: 180)
                .chartYAxis {
                    AxisMarks(values: .automatic(desiredCount: 4)) { value in
                        AxisGridLine()
                        AxisValueLabel { if let v = value.as(Double.self) { Text("\(Int(v)) km") } }
                    }
                }
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 16).fill(Color(.systemGray6)))
    }

    // MARK: - Pace Trend Chart

    private var paceTrendChart: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Pace Trend")
                .font(.headline)
            if vm.recentRuns.isEmpty {
                chartPlaceholder
            } else {
                Chart(vm.recentRuns.reversed()) { run in
                    LineMark(
                        x: .value("Date", run.date),
                        y: .value("Pace", run.averagePaceSecondsPerKm)
                    )
                    .interpolationMethod(.catmullRom)
                    .foregroundStyle(Color.orange)

                    PointMark(
                        x: .value("Date", run.date),
                        y: .value("Pace", run.averagePaceSecondsPerKm)
                    )
                    .foregroundStyle(Color.orange)
                }
                .frame(height: 180)
                .chartYAxis {
                    AxisMarks(values: .automatic(desiredCount: 4)) { value in
                        AxisGridLine()
                        AxisValueLabel {
                            if let v = value.as(Double.self) {
                                Text(v.paceString)
                            }
                        }
                    }
                }
                .chartYScale(domain: .automatic(includesZero: false))
                // Lower pace = faster, so invert the axis
                .chartYAxis(content: { _ in })
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 16).fill(Color(.systemGray6)))
    }

    // MARK: - Run History

    private var runHistoryList: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("All Runs")
                .font(.headline)
            ForEach(vm.allRuns) { run in
                Button {
                    selectedRun = run
                } label: {
                    RunRowView(run: run)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var chartPlaceholder: some View {
        Text("No data yet — complete some runs to see charts.")
            .font(.caption)
            .foregroundStyle(.secondary)
            .frame(height: 100, alignment: .center)
            .frame(maxWidth: .infinity)
    }
}
