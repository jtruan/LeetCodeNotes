import Foundation

@MainActor
class TrainingPlanViewModel: ObservableObject {
    @Published var plan: TrainingPlan?
    @Published var currentWeek: Int = 1

    private let planKey = "saved_training_plan"

    init() {
        load()
    }

    func generatePlan(profile: UserProfile) {
        var p = profile
        if let loaded = loadedBaseKm() { p.baseWeeklyKm = loaded }
        plan = TrainingPlanService.generate(profile: p)
        save()
    }

    func toggleSession(_ session: TrainingSession) {
        guard let idx = plan?.sessions.firstIndex(where: { $0.id == session.id }) else { return }
        plan?.sessions[idx].isCompleted.toggle()
        save()
    }

    func nextSession() -> TrainingSession? {
        plan?.sessions.first { !$0.isCompleted && $0.type != .rest }
    }

    var completionPercent: Double {
        guard let plan, plan.totalRunSessions > 0 else { return 0 }
        return Double(plan.completedCount) / Double(plan.totalRunSessions)
    }

    // MARK: - Persistence

    private func save() {
        guard let plan else { return }
        if let data = try? JSONEncoder().encode(plan) {
            UserDefaults.standard.set(data, forKey: planKey)
        }
    }

    private func load() {
        guard let data = UserDefaults.standard.data(forKey: planKey),
              let decoded = try? JSONDecoder().decode(TrainingPlan.self, from: data) else { return }
        plan = decoded
        currentWeek = currentPlanWeek(startDate: decoded.profile.planStartDate)
    }

    private func currentPlanWeek(startDate: Date) -> Int {
        let days = Calendar.current.dateComponents([.day], from: startDate, to: Date()).day ?? 0
        return max(1, (days / 7) + 1)
    }

    private func loadedBaseKm() -> Double? { nil } // Override by injecting HealthKit avg if desired
}
