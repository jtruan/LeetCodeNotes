# RunTracker — iOS App Setup

## Requirements
- Xcode 14+
- iOS 16+ deployment target (required for Swift Charts)
- Physical device (HealthKit does not work in Simulator)

## Steps to Build & Run

1. **Create a new Xcode project**
   - File → New → Project → App
   - Product Name: `RunTracker`
   - Interface: SwiftUI
   - Language: Swift
   - iOS 16.0 minimum deployment target

2. **Add HealthKit capability**
   - Select the RunTracker target → Signing & Capabilities
   - Click `+ Capability` → add **HealthKit**

3. **Replace generated files**
   - Delete the auto-generated `ContentView.swift` and `RunTrackerApp.swift`
   - Drag all `.swift` files from this folder into Xcode (keep folder structure)
   - Copy `Info.plist` entries into your project's `Info.plist`
     (or replace it entirely if Xcode uses an Info.plist file)

4. **Build & Run**
   - Select your physical iPhone as the run target
   - Press ▶ (Cmd+R)
   - Grant Health permissions when prompted

## App Flow

```
First Launch  →  Onboarding (goal / level / days/week)
                     ↓
              Auto-fetches Apple Health avg weekly km
                     ↓
              Generates 8–16 week training plan
                     ↓
              Home tab (Dashboard)
```

## Tabs

| Tab | What it shows |
|-----|--------------|
| Home | This week's km, next scheduled workout, recent runs |
| Plan | Week-by-week training sessions, mark complete |
| Analytics | Weekly volume bar chart, pace trend line chart, all runs |

## Architecture Notes

- **HealthKitService** — all HK queries; requests auth, fetches workouts
- **TrainingPlanService** — pure function, generates plan from `UserProfile`
- **TrainingPlanViewModel** — holds plan in memory, persists to UserDefaults
- **DashboardViewModel / AnalyticsViewModel** — fetch and aggregate run data

## Customisation Ideas

- Add a heart rate zone pie chart (SwiftUI Charts + HK heart rate samples)
- Persist completed sessions to CloudKit for cross-device sync
- Add push notifications for upcoming workouts (UserNotifications)
- Show predicted race time based on recent 5K or 10K effort
