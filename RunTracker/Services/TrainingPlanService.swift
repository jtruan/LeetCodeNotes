import Foundation

struct TrainingPlanService {

    // MARK: - Public

    static func generate(profile: UserProfile) -> TrainingPlan {
        let weeks = profile.goal.planWeeks
        let weeklyVolumes = buildVolumeProgression(base: profile.baseWeeklyKm, totalWeeks: weeks)
        let sessions = buildAllSessions(profile: profile, weeklyVolumes: weeklyVolumes)
        return TrainingPlan(profile: profile, sessions: sessions, weeklyTargetKm: weeklyVolumes)
    }

    // MARK: - Volume Progression

    // 4-week cycles: 3 build weeks + 1 recovery, tapering in the final 2 weeks
    private static func buildVolumeProgression(base: Double, totalWeeks: Int) -> [Double] {
        var volumes: [Double] = []
        for week in 1...totalWeeks {
            let v: Double
            let isTaperWeek = week >= totalWeeks - 1
            if isTaperWeek {
                v = week == totalWeeks ? base * 0.5 : base * 0.7
            } else {
                let cyclePos = (week - 1) % 4
                switch cyclePos {
                case 0: v = base * 1.0
                case 1: v = base * 1.1
                case 2: v = base * 1.2
                case 3: v = base * 0.85 // recovery
                default: v = base
                }
            }
            volumes.append(v)
        }
        return volumes
    }

    // MARK: - Session Generation

    private static func buildAllSessions(profile: UserProfile, weeklyVolumes: [Double]) -> [TrainingSession] {
        var sessions: [TrainingSession] = []
        let template = weekTemplate(days: profile.daysPerWeek)

        for (weekIdx, volume) in weeklyVolumes.enumerated() {
            let weekNum = weekIdx + 1
            let longRunKm = volume * 0.30
            let easyCount = template.filter { $0 == .easy }.count
            let easyKm = easyCount > 0 ? (volume - longRunKm) / Double(easyCount) : 0

            var longAssigned = false
            for (dayIdx, type) in template.enumerated() {
                let dist: Double
                switch type {
                case .long:
                    dist = longRunKm
                    longAssigned = true
                case .easy:
                    dist = easyKm
                case .tempo:
                    dist = max(5, volume * 0.15)
                case .interval:
                    dist = max(4, volume * 0.12)
                case .rest:
                    dist = 0
                }
                _ = longAssigned
                sessions.append(TrainingSession(
                    id: UUID(),
                    weekNumber: weekNum,
                    dayOfWeek: dayIdx,
                    type: type,
                    targetDistanceKm: dist,
                    isCompleted: false
                ))
            }
        }
        return sessions
    }

    // Returns a 7-element array (Mon–Sun) of SessionType for a given days/week count.
    // Unused days are .rest.
    private static func weekTemplate(days: Int) -> [SessionType] {
        switch days {
        case 3:
            // Mon easy, Wed tempo/interval, Sat long
            return [.easy, .rest, .tempo, .rest, .rest, .long, .rest]
        case 4:
            // Mon easy, Wed tempo, Thu easy, Sat long
            return [.easy, .rest, .tempo, .easy, .rest, .long, .rest]
        case 5:
            // Mon easy, Tue interval, Thu easy, Fri tempo, Sat long
            return [.easy, .interval, .rest, .easy, .tempo, .long, .rest]
        default:
            // 3-day fallback
            return [.easy, .rest, .tempo, .rest, .rest, .long, .rest]
        }
    }
}
