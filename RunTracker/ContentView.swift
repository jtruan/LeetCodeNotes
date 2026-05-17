import SwiftUI

struct ContentView: View {
    @EnvironmentObject var healthKit: HealthKitService
    @EnvironmentObject var planVM: TrainingPlanViewModel

    @State private var onboardingDone = UserDefaults.standard.bool(forKey: "onboarding_complete")

    var body: some View {
        if onboardingDone || planVM.plan != nil {
            mainTabView
                .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
                    onboardingDone = UserDefaults.standard.bool(forKey: "onboarding_complete")
                }
        } else {
            OnboardingView()
                .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
                    onboardingDone = UserDefaults.standard.bool(forKey: "onboarding_complete")
                }
        }
    }

    private var mainTabView: some View {
        TabView {
            DashboardView(healthKit: healthKit)
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }

            TrainingPlanView()
                .tabItem {
                    Label("Plan", systemImage: "calendar")
                }

            AnalyticsView(healthKit: healthKit)
                .tabItem {
                    Label("Analytics", systemImage: "chart.line.uptrend.xyaxis")
                }
        }
    }
}
