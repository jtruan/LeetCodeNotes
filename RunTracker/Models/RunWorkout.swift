import Foundation

struct RunWorkout: Identifiable {
    let id: UUID
    let date: Date
    let distance: Double       // meters
    let duration: TimeInterval // seconds
    let averageHeartRate: Double?
    let elevationGain: Double?

    var distanceKm: Double { distance / 1000 }

    var averagePaceSecondsPerKm: Double {
        guard distanceKm > 0 else { return 0 }
        return duration / distanceKm
    }

    var formattedPace: String {
        let totalSeconds = Int(averagePaceSecondsPerKm)
        let minutes = totalSeconds / 60
        let seconds = totalSeconds % 60
        return String(format: "%d:%02d /km", minutes, seconds)
    }

    var formattedDuration: String {
        let totalSeconds = Int(duration)
        let hours = totalSeconds / 3600
        let minutes = (totalSeconds % 3600) / 60
        let seconds = totalSeconds % 60
        if hours > 0 {
            return String(format: "%d:%02d:%02d", hours, minutes, seconds)
        } else {
            return String(format: "%d:%02d", minutes, seconds)
        }
    }

    var formattedDistance: String {
        String(format: "%.2f km", distanceKm)
    }
}
