import Foundation

enum RaceGoal: String, CaseIterable, Codable {
    case fiveK        = "5K"
    case tenK         = "10K"
    case halfMarathon = "Half Marathon"
    case marathon     = "Marathon"

    var distanceKm: Double {
        switch self {
        case .fiveK:        return 5
        case .tenK:         return 10
        case .halfMarathon: return 21.1
        case .marathon:     return 42.2
        }
    }

    var planWeeks: Int {
        switch self {
        case .fiveK:        return 8
        case .tenK:         return 10
        case .halfMarathon: return 12
        case .marathon:     return 16
        }
    }

    var icon: String {
        switch self {
        case .fiveK:        return "figure.run"
        case .tenK:         return "figure.run.circle"
        case .halfMarathon: return "medal"
        case .marathon:     return "trophy"
        }
    }
}

enum ExperienceLevel: String, CaseIterable, Codable {
    case beginner     = "Beginner"
    case intermediate = "Intermediate"
    case advanced     = "Advanced"

    var description: String {
        switch self {
        case .beginner:     return "Running < 6 months or < 20 km/week"
        case .intermediate: return "Running 6 months–2 years or 20–50 km/week"
        case .advanced:     return "Running 2+ years or > 50 km/week"
        }
    }

    var defaultWeeklyKm: Double {
        switch self {
        case .beginner:     return 15
        case .intermediate: return 35
        case .advanced:     return 55
        }
    }
}

struct UserProfile: Codable {
    var goal: RaceGoal
    var experience: ExperienceLevel
    var daysPerWeek: Int
    var planStartDate: Date
    var baseWeeklyKm: Double
}

struct TrainingPlan: Codable {
    let profile: UserProfile
    var sessions: [TrainingSession]
    let weeklyTargetKm: [Double] // index = weekNumber - 1

    var totalWeeks: Int { profile.goal.planWeeks }

    func sessions(forWeek week: Int) -> [TrainingSession] {
        sessions.filter { $0.weekNumber == week }.sorted { $0.dayOfWeek < $1.dayOfWeek }
    }

    var completedCount: Int { sessions.filter(\.isCompleted).count }
    var totalRunSessions: Int { sessions.filter { $0.type != .rest }.count }
}
