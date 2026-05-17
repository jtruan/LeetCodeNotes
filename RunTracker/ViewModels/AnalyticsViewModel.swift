import Foundation

struct WeeklyVolume: Identifiable {
    let id = UUID()
    let weekStart: Date
    let totalKm: Double
    var label: String { weekStart.shortFormatted }
}

@MainActor
class AnalyticsViewModel: ObservableObject {
    @Published var allRuns: [RunWorkout] = []
    @Published var weeklyVolumes: [WeeklyVolume] = []
    @Published var isLoading = false
    @Published var error: String?

    private let healthKit: HealthKitService

    init(healthKit: HealthKitService) {
        self.healthKit = healthKit
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            allRuns = try await healthKit.fetchRunningWorkouts(limit: 200)
            weeklyVolumes = buildWeeklyVolumes(from: allRuns, weeks: 8)
        } catch {
            self.error = error.localizedDescription
        }
    }

    private func buildWeeklyVolumes(from runs: [RunWorkout], weeks: Int) -> [WeeklyVolume] {
        let cal = Calendar.current
        let now = Date()
        return (0..<weeks).reversed().compactMap { offset -> WeeklyVolume? in
            guard let weekStart = cal.date(byAdding: .weekOfYear, value: -offset, to: now.startOfWeek()),
                  let weekEnd = cal.date(byAdding: .day, value: 7, to: weekStart) else { return nil }
            let km = runs.filter { $0.date >= weekStart && $0.date < weekEnd }
                        .reduce(0) { $0 + $1.distanceKm }
            return WeeklyVolume(weekStart: weekStart, totalKm: km)
        }
    }

    var recentRuns: [RunWorkout] { Array(allRuns.prefix(20)) }
}
