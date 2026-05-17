import Foundation
import SwiftUI

extension Date {
    var shortFormatted: String {
        let f = DateFormatter()
        f.dateFormat = "MMM d"
        return f.string(from: self)
    }

    var weekLabel: String {
        let f = DateFormatter()
        f.dateFormat = "MMM d"
        return f.string(from: self)
    }

    func startOfWeek() -> Date {
        let cal = Calendar.current
        return cal.date(from: cal.dateComponents([.yearForWeekOfYear, .weekOfYear], from: self)) ?? self
    }
}

extension Double {
    var kmString: String { String(format: "%.1f km", self) }
    var paceString: String {
        let total = Int(self)
        return String(format: "%d:%02d /km", total / 60, total % 60)
    }
}

extension Color {
    static let sessionEasy     = Color.green
    static let sessionLong     = Color.blue
    static let sessionTempo    = Color.orange
    static let sessionInterval = Color.red
    static let sessionRest     = Color.gray
}

extension SessionType {
    var color: Color {
        switch self {
        case .easy:     return .sessionEasy
        case .long:     return .sessionLong
        case .tempo:    return .sessionTempo
        case .interval: return .sessionInterval
        case .rest:     return .sessionRest
        }
    }
}
