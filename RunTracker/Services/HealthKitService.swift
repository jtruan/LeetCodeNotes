import Foundation
import HealthKit

@MainActor
class HealthKitService: ObservableObject {
    private let store = HKHealthStore()

    @Published var isAuthorized = false
    @Published var authorizationError: String?

    static var isAvailable: Bool { HKHealthStore.isHealthDataAvailable() }

    private let readTypes: Set<HKObjectType> = {
        var types: Set<HKObjectType> = [.workoutType()]
        let quantities: [HKQuantityTypeIdentifier] = [
            .distanceWalkingRunning,
            .heartRate,
            .activeEnergyBurned,
            .runningPower
        ]
        quantities.compactMap { HKQuantityType.quantityType(forIdentifier: $0) }.forEach {
            types.insert($0)
        }
        return types
    }()

    func requestAuthorization() async {
        guard Self.isAvailable else {
            authorizationError = "HealthKit is not available on this device."
            return
        }
        do {
            try await store.requestAuthorization(toShare: [], read: readTypes)
            isAuthorized = true
        } catch {
            authorizationError = error.localizedDescription
        }
    }

    func fetchRunningWorkouts(limit: Int = 100) async throws -> [RunWorkout] {
        let predicate = HKQuery.predicateForWorkouts(with: .running)
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)

        return try await withCheckedThrowingContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: .workoutType(),
                predicate: predicate,
                limit: limit,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                let workouts = (samples as? [HKWorkout] ?? []).map { self.convert($0) }
                continuation.resume(returning: workouts)
            }
            store.execute(query)
        }
    }

    func fetchAverageWeeklyKm(weeks: Int = 4) async throws -> Double {
        let workouts = try await fetchRunningWorkouts(limit: 200)
        let cutoff = Calendar.current.date(byAdding: .weekOfYear, value: -weeks, to: Date()) ?? Date()
        let recent = workouts.filter { $0.date >= cutoff }
        let totalKm = recent.reduce(0) { $0 + $1.distanceKm }
        return totalKm / Double(weeks)
    }

    private func convert(_ workout: HKWorkout) -> RunWorkout {
        RunWorkout(
            id: workout.uuid,
            date: workout.startDate,
            distance: workout.totalDistance?.doubleValue(for: .meter()) ?? 0,
            duration: workout.duration,
            averageHeartRate: heartRate(from: workout),
            elevationGain: elevationGain(from: workout)
        )
    }

    private func heartRate(from workout: HKWorkout) -> Double? {
        // Heart rate is stored as statistics on the workout in newer HealthKit versions
        if #available(iOS 16.0, *) {
            let hrType = HKQuantityType(.heartRate)
            return workout.statistics(for: hrType)?
                .averageQuantity()?
                .doubleValue(for: HKUnit(from: "count/min"))
        }
        return nil
    }

    private func elevationGain(from workout: HKWorkout) -> Double? {
        let meta = workout.metadata
        if let gain = meta?[HKMetadataKeyElevationAscended] as? HKQuantity {
            return gain.doubleValue(for: .meter())
        }
        return nil
    }
}
