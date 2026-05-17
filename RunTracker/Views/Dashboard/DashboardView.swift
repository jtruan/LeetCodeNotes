import SwiftUI

struct DashboardView: View {
    @StateObject private var vm: DashboardViewModel
    @EnvironmentObject var planVM: TrainingPlanViewModel
    @EnvironmentObject var healthKit: HealthKitService

    init(healthKit: HealthKitService) {
        _vm = StateObject(wrappedValue: DashboardViewModel(healthKit: healthKit))
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    weekSummaryCard
                    if let next = planVM.nextSession() {
                        nextWorkoutCard(next)
                    }
                    recentRunsList
                }
                .padding()
            }
            .navigationTitle("Dashboard")
            .task { await vm.load() }
            .refreshable { await vm.load() }
            .overlay {
                if vm.isLoading && vm.recentRuns.isEmpty {
                    ProgressView()
                }
            }
        }
    }

    // MARK: - Subviews

    private var weekSummaryCard: some View {
        HStack(spacing: 0) {
            statCell(value: String(format: "%.1f", vm.thisWeekKm), label: "km this week")
            Divider().frame(height: 40)
            statCell(value: "\(vm.thisWeekRuns)", label: "runs")
            Divider().frame(height: 40)
            statCell(value: String(format: "%.0f%%", planVM.completionPercent * 100), label: "plan done")
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 16).fill(Color(.systemGray6)))
    }

    private func statCell(value: String, label: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title2).bold()
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
    }

    private func nextWorkoutCard(_ session: TrainingSession) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Next Workout")
                    .font(.headline)
                Spacer()
                Text("Week \(planVM.currentWeek)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            HStack(spacing: 12) {
                Text(session.type.emoji)
                    .font(.largeTitle)
                VStack(alignment: .leading, spacing: 4) {
                    Text(session.type.rawValue)
                        .font(.title3).bold()
                    Text(session.formattedDistance)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Spacer()
            }
            Text(session.type.description)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(session.type.color.opacity(0.12))
                .overlay(RoundedRectangle(cornerRadius: 16).stroke(session.type.color.opacity(0.3), lineWidth: 1))
        )
    }

    private var recentRunsList: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Runs")
                .font(.headline)
            if vm.recentRuns.isEmpty && !vm.isLoading {
                Text("No runs found in Apple Health.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                ForEach(vm.recentRuns) { run in
                    RunRowView(run: run)
                }
            }
        }
    }
}

struct RunRowView: View {
    let run: RunWorkout

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(run.date.shortFormatted)
                    .font(.subheadline).bold()
                Text(run.formattedDuration)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 4) {
                Text(run.formattedDistance)
                    .font(.subheadline).bold()
                Text(run.formattedPace)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.systemGray6)))
    }
}
