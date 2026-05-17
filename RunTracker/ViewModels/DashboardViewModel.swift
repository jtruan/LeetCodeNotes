import Foundation

@MainActor
class DashboardViewModel: ObservableObject {
    @Published var recentRuns: [RunWorkout] = []
    @Published var thisWeekKm: Double = 0
    @Published var thisWeekRuns: Int = 0
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
            let all = try await healthKit.fetchRunningWorkouts(limit: 30)
            recentRuns = Array(all.prefix(10))
            let weekStart = Date().startOfWeek()
            let weekRuns = all.filter { $0.date >= weekStart }
            thisWeekKm = weekRuns.reduce(0) { $0 + $1.distanceKm }
            thisWeekRuns = weekRuns.count
        } catch {
            self.error = error.localizedDescription
        }
    }
}
