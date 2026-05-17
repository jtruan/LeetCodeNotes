import SwiftUI

struct TrainingPlanView: View {
    @EnvironmentObject var planVM: TrainingPlanViewModel
    @State private var selectedSession: TrainingSession?

    var body: some View {
        NavigationStack {
            if let plan = planVM.plan {
                planContent(plan)
            } else {
                emptyState
            }
        }
    }

    private func planContent(_ plan: TrainingPlan) -> some View {
        ScrollView {
            VStack(spacing: 0) {
                // Goal header
                goalHeader(plan)

                // Week picker
                weekPicker(totalWeeks: plan.totalWeeks)

                // Sessions for selected week
                LazyVStack(spacing: 12) {
                    ForEach(plan.sessions(forWeek: planVM.currentWeek)) { session in
                        SessionCard(session: session) {
                            selectedSession = session
                        } onToggle: {
                            planVM.toggleSession(session)
                        }
                    }
                }
                .padding()
            }
        }
        .navigationTitle("Training Plan")
        .sheet(item: $selectedSession) { session in
            SessionDetailView(session: session) {
                planVM.toggleSession(session)
            }
        }
    }

    private func goalHeader(_ plan: TrainingPlan) -> some View {
        VStack(spacing: 8) {
            Text(plan.profile.goal.rawValue)
                .font(.title2).bold()
            ProgressView(value: planVM.completionPercent)
                .tint(.blue)
                .padding(.horizontal)
            Text("\(plan.completedCount) of \(plan.totalRunSessions) sessions completed")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(Color(.systemGray6))
    }

    private func weekPicker(totalWeeks: Int) -> some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(1...totalWeeks, id: \.self) { week in
                    Button("Wk \(week)") {
                        planVM.currentWeek = week
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(week == planVM.currentWeek ? .blue : .gray)
                    .controlSize(.small)
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
        }
    }

    private var emptyState: some View {
        ContentUnavailableView(
            "No Plan Yet",
            systemImage: "figure.run.circle",
            description: Text("Complete onboarding to generate your personalized training plan.")
        )
        .navigationTitle("Training Plan")
    }
}

struct SessionCard: View {
    let session: TrainingSession
    let onTap: () -> Void
    let onToggle: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 14) {
                Text(session.type.emoji)
                    .font(.title2)

                VStack(alignment: .leading, spacing: 4) {
                    Text("\(session.dayName) — \(session.type.rawValue)")
                        .font(.subheadline).bold()
                    Text(session.formattedDistance)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                Button {
                    onToggle()
                } label: {
                    Image(systemName: session.isCompleted ? "checkmark.circle.fill" : "circle")
                        .font(.title3)
                        .foregroundStyle(session.isCompleted ? .green : .gray)
                }
                .buttonStyle(.plain)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(session.isCompleted ? Color.green.opacity(0.08) : Color(.systemGray6))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(session.type.color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
    }
}
