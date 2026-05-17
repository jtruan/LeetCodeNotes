import Foundation

enum SessionType: String, Codable, CaseIterable {
    case easy = "Easy Run"
    case long = "Long Run"
    case tempo = "Tempo Run"
    case interval = "Intervals"
    case rest = "Rest"

    var emoji: String {
        switch self {
        case .easy:     return "🟢"
        case .long:     return "🔵"
        case .tempo:    return "🟠"
        case .interval: return "🔴"
        case .rest:     return "⚪️"
        }
    }

    var colorName: String {
        switch self {
        case .easy:     return "green"
        case .long:     return "blue"
        case .tempo:    return "orange"
        case .interval: return "red"
        case .rest:     return "gray"
        }
    }

    var description: String {
        switch self {
        case .easy:
            return "Conversational pace — you should be able to speak in full sentences. Builds aerobic base."
        case .long:
            return "Slow and steady. 60–90 sec/km slower than goal race pace. Build endurance and mental strength."
        case .tempo:
            return "Comfortably hard — a few words but not a sentence. Sustained effort for 20–40 min. Raises lactate threshold."
        case .interval:
            return "400m–1km repeats at 5K effort with equal-time recovery jogs between. Builds speed and running economy."
        case .rest:
            return "Full rest or light walking. Recovery is where fitness gains happen."
        }
    }
}

struct TrainingSession: Identifiable, Codable {
    let id: UUID
    let weekNumber: Int
    let dayOfWeek: Int            // 0 = Monday … 6 = Sunday
    let type: SessionType
    let targetDistanceKm: Double
    var isCompleted: Bool

    var dayName: String {
        let days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return days[dayOfWeek]
    }

    var formattedDistance: String {
        type == .rest ? "—" : String(format: "%.1f km", targetDistanceKm)
    }
}
