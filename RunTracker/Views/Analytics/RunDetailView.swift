import SwiftUI

struct RunDetailView: View {
    let run: RunWorkout
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Section("Summary") {
                    LabeledContent("Date", value: run.date.shortFormatted)
                    LabeledContent("Distance", value: run.formattedDistance)
                    LabeledContent("Duration", value: run.formattedDuration)
                    LabeledContent("Avg Pace", value: run.formattedPace)
                }
                if let hr = run.averageHeartRate {
                    Section("Heart Rate") {
                        LabeledContent("Average", value: String(format: "%.0f bpm", hr))
                    }
                }
                if let elev = run.elevationGain {
                    Section("Elevation") {
                        LabeledContent("Gain", value: String(format: "%.0f m", elev))
                    }
                }
            }
            .navigationTitle("Run Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}
