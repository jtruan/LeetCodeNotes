import SwiftUI

@main
struct RunTrackerApp: App {
    @StateObject private var healthKit = HealthKitService()
    @StateObject private var planVM = TrainingPlanViewModel()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(healthKit)
                .environmentObject(planVM)
        }
    }
}
