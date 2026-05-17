import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var planVM: TrainingPlanViewModel
    @EnvironmentObject var healthKit: HealthKitService

    @State private var step = 0
    @State private var selectedGoal: RaceGoal = .fiveK
    @State private var selectedLevel: ExperienceLevel = .beginner
    @State private var daysPerWeek = 3
    @State private var isLoading = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Progress dots
                HStack(spacing: 8) {
                    ForEach(0..<3) { i in
                        Circle()
                            .fill(i <= step ? Color.blue : Color.gray.opacity(0.3))
                            .frame(width: 8, height: 8)
                    }
                }
                .padding(.top, 24)

                TabView(selection: $step) {
                    goalStep.tag(0)
                    levelStep.tag(1)
                    daysStep.tag(2)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                .animation(.easeInOut, value: step)
            }
            .navigationTitle("Set Up Your Plan")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    // MARK: - Steps

    private var goalStep: some View {
        VStack(spacing: 24) {
            Text("What's your goal?")
                .font(.title2).bold()
                .padding(.top, 40)

            VStack(spacing: 12) {
                ForEach(RaceGoal.allCases, id: \.self) { goal in
                    Button {
                        selectedGoal = goal
                    } label: {
                        HStack {
                            Image(systemName: goal.icon)
                                .frame(width: 32)
                            Text(goal.rawValue)
                                .font(.headline)
                            Spacer()
                            if selectedGoal == goal {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.blue)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(selectedGoal == goal ? Color.blue.opacity(0.12) : Color(.systemGray6))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(selectedGoal == goal ? Color.blue : Color.clear, lineWidth: 2)
                                )
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)

            Spacer()
            nextButton("Next") { step = 1 }
        }
    }

    private var levelStep: some View {
        VStack(spacing: 24) {
            Text("Your experience?")
                .font(.title2).bold()
                .padding(.top, 40)

            VStack(spacing: 12) {
                ForEach(ExperienceLevel.allCases, id: \.self) { level in
                    Button {
                        selectedLevel = level
                    } label: {
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(level.rawValue).font(.headline)
                                Spacer()
                                if selectedLevel == level {
                                    Image(systemName: "checkmark.circle.fill").foregroundStyle(.blue)
                                }
                            }
                            Text(level.description)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(selectedLevel == level ? Color.blue.opacity(0.12) : Color(.systemGray6))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(selectedLevel == level ? Color.blue : Color.clear, lineWidth: 2)
                                )
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)

            Spacer()
            HStack {
                backButton { step = 0 }
                nextButton("Next") { step = 2 }
            }
            .padding(.horizontal)
        }
    }

    private var daysStep: some View {
        VStack(spacing: 24) {
            Text("Days per week?")
                .font(.title2).bold()
                .padding(.top, 40)

            VStack(spacing: 20) {
                Text("\(daysPerWeek) days")
                    .font(.system(size: 48, weight: .bold, design: .rounded))
                    .foregroundStyle(.blue)

                Slider(value: Binding(
                    get: { Double(daysPerWeek) },
                    set: { daysPerWeek = Int($0) }
                ), in: 3...5, step: 1)
                .padding(.horizontal)

                HStack {
                    Text("3").foregroundStyle(.secondary)
                    Spacer()
                    Text("4").foregroundStyle(.secondary)
                    Spacer()
                    Text("5").foregroundStyle(.secondary)
                }
                .padding(.horizontal)
                .font(.caption)
            }
            .padding(.horizontal)

            Spacer()

            HStack {
                backButton { step = 1 }
                Button(isLoading ? "Building…" : "Build My Plan") {
                    Task { await buildPlan() }
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .disabled(isLoading)
            }
            .padding(.horizontal)
            .padding(.bottom, 40)
        }
    }

    // MARK: - Actions

    private func buildPlan() async {
        isLoading = true
        await healthKit.requestAuthorization()

        var baseKm = selectedLevel.defaultWeeklyKm
        if let avg = try? await healthKit.fetchAverageWeeklyKm(), avg > 5 {
            baseKm = avg
        }

        let profile = UserProfile(
            goal: selectedGoal,
            experience: selectedLevel,
            daysPerWeek: daysPerWeek,
            planStartDate: Date(),
            baseWeeklyKm: baseKm
        )
        planVM.generatePlan(profile: profile)
        isLoading = false
        UserDefaults.standard.set(true, forKey: "onboarding_complete")
    }

    // MARK: - Reusable button helpers

    private func nextButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(title, action: action)
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .frame(maxWidth: .infinity)
            .padding(.horizontal)
            .padding(.bottom, 40)
    }

    private func backButton(action: @escaping () -> Void) -> some View {
        Button("Back", action: action)
            .buttonStyle(.bordered)
            .controlSize(.large)
    }
}
