import SwiftUI

struct SessionDetailView: View {
    let session: TrainingSession
    let onToggle: () -> Void
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Type icon + title
                    VStack(spacing: 8) {
                        Text(session.type.emoji)
                            .font(.system(size: 64))
                        Text(session.type.rawValue)
                            .font(.title).bold()
                        Text(session.formattedDistance)
                            .font(.title3)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.top, 16)

                    // Description card
                    VStack(alignment: .leading, spacing: 8) {
                        Text("How to run it")
                            .font(.headline)
                        Text(session.type.description)
                            .font(.body)
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 12).fill(Color(.systemGray6)))
                    .padding(.horizontal)

                    // Mark done button
                    if session.type != .rest {
                        Button {
                            onToggle()
                            dismiss()
                        } label: {
                            Label(
                                session.isCompleted ? "Mark as Not Done" : "Mark as Done",
                                systemImage: session.isCompleted ? "xmark.circle" : "checkmark.circle.fill"
                            )
                            .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(session.isCompleted ? .gray : .green)
                        .controlSize(.large)
                        .padding(.horizontal)
                    }
                }
            }
            .navigationTitle("\(session.dayName)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}
