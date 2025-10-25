# 🏗️ AI Agent Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      ClubSync.AI System                         │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Web UI     │    │  Flask App   │    │   Database   │    │
│  │  (Frontend)  │◄──►│  (Backend)   │◄──►│  (SQLite)    │    │
│  └──────────────┘    └──────┬───────┘    └──────────────┘    │
│                             │                                  │
│                             ▼                                  │
│                  ┌──────────────────────┐                     │
│                  │   AI Agent Module    │                     │
│                  │  (MeetingScheduler)  │                     │
│                  └──────────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## AI Agent Internal Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                    MeetingSchedulerAgent                          │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              1. DATA COLLECTION LAYER                   │    │
│  │  - get_all_user_availability()                          │    │
│  │  - get_all_users()                                      │    │
│  │  - get_booking_history()                                │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              2. PATTERN LEARNING LAYER                  │    │
│  │  - learn_user_patterns()                                │    │
│  │  - estimate_attendance_probability()                    │    │
│  │  - calculate_expected_attendance()                      │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           3. AVAILABILITY ANALYSIS LAYER                │    │
│  │  - build_availability_grid()                            │    │
│  │  - _is_continuous_slot()                                │    │
│  │  - _get_available_users_for_slot()                      │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           4. CONSTRAINT SOLVING LAYER                   │    │
│  │  - check_constraints()                                  │    │
│  │    • required_members                                   │    │
│  │    • required_mentors                                   │    │
│  │    • min/max_attendees                                  │    │
│  │    • time_constraints                                   │    │
│  │    • club_filter                                        │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              5. SCORING & RANKING LAYER                 │    │
│  │  - score_slot()                                         │    │
│  │    Objectives:                                          │    │
│  │    • max_attendance                                     │    │
│  │    • max_probability                                    │    │
│  │    • fairness                                           │    │
│  │    • mentor_priority                                    │    │
│  │    • balanced                                           │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            6. MAIN ALGORITHM LAYER                      │    │
│  │  - find_optimal_slots()                                 │    │
│  │  - create_smart_poll()                                  │    │
│  │  - _enrich_slot_info()                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│ Database │
└────┬─────┘
     │
     │ 1. Fetch Data
     ▼
┌─────────────────────────┐
│ UserAvailability Table  │
│ - user_id               │
│ - day_of_week           │
│ - start_hour/end_hour   │
│ - is_busy               │
└────┬────────────────────┘
     │
     │ 2. Build Grid
     ▼
┌─────────────────────────┐
│ Availability Grid       │
│ grid[date][hour] = {    │
│   busy_users: set       │
│   available_users: set  │
│   total_users: int      │
│ }                       │
└────┬────────────────────┘
     │
     │ 3. Learn Patterns
     ▼
┌─────────────────────────┐
│ Booking History         │
│ - start_time            │
│ - user_id               │
│ - status                │
└────┬────────────────────┘
     │
     │ 4. Calculate Probability
     ▼
┌─────────────────────────┐
│ User Patterns           │
│ - preferred_hours       │
│ - attendance_rate       │
│ - hour_probability      │
│ - day_probability       │
└────┬────────────────────┘
     │
     │ 5. Apply to Slots
     ▼
┌─────────────────────────┐
│ Candidate Slots         │
│ For each slot:          │
│ - available_users       │
│ - expected_attendance   │
│ - probabilities         │
└────┬────────────────────┘
     │
     │ 6. Check Constraints
     ▼
┌─────────────────────────┐
│ Valid Slots             │
│ (constraints satisfied) │
└────┬────────────────────┘
     │
     │ 7. Score & Rank
     ▼
┌─────────────────────────┐
│ Top N Slots             │
│ - sorted by score       │
│ - enriched info         │
└────┬────────────────────┘
     │
     │ 8. Return Results
     ▼
┌─────────────────────────┐
│ API Response / Output   │
└─────────────────────────┘
```

## Scoring Mechanism Flow

```
For each candidate slot:

    ┌──────────────────────────────────────┐
    │  1. Get available users              │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  2. Calculate attendance probability │
    │     for each user                    │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  3. Sum to get expected attendance   │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  4. Apply objective-specific scoring │
    │     - max_attendance: high count     │
    │     - fairness: low variance         │
    │     - mentor_priority: mentors+      │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  5. Add bonuses & penalties          │
    │     + Required members present       │
    │     + Good time (9-17h)              │
    │     + Mentors available              │
    │     - Too far in future              │
    │     - Lunch time (12-14h)            │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  6. Final score                      │
    └──────────────────────────────────────┘
```

## Smart Poll Creation Flow

```
create_smart_poll()
    │
    ├─► Objective 1: max_attendance
    │   └─► find_optimal_slots(objective='max_attendance', top_n=1)
    │       └─► Slot A (most people)
    │
    ├─► Objective 2: balanced
    │   └─► find_optimal_slots(objective='balanced', top_n=1)
    │       └─► Slot B (balanced)
    │
    ├─► Objective 3: mentor_priority
    │   └─► find_optimal_slots(objective='mentor_priority', top_n=1)
    │       └─► Slot C (with mentor)
    │
    ├─► Remove duplicates
    │   └─► Ensure 3 unique time slots
    │
    ├─► Generate recommendation
    │   └─► Pick best slot and explain why
    │
    └─► Return poll with 3 options
```

## API Request/Response Flow

```
Client Request
    │
    ▼
POST /api/agent/suggest-slots
    │
    ├─► Parse request JSON
    │   - duration_minutes
    │   - constraints
    │   - objective
    │   - days_ahead
    │   - top_n
    │
    ├─► Create agent instance
    │   agent = create_agent(db.session)
    │
    ├─► Call find_optimal_slots()
    │   │
    │   ├─► Fetch data from DB
    │   ├─► Learn patterns
    │   ├─► Build grid
    │   ├─► Find candidates
    │   ├─► Check constraints
    │   ├─► Score & rank
    │   └─► Return top N
    │
    ├─► Serialize to JSON
    │   - Convert datetime to ISO string
    │   - Extract relevant fields
    │
    └─► Return JSON response
        {
            "success": true,
            "slots": [...],
            "message": "Found N slots"
        }
```

## Pattern Learning Algorithm

```
Input: user_id, booking_history

    ┌──────────────────────────────────────┐
    │  1. Filter bookings by user_id       │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  2. Extract features                 │
    │     - Hour of each booking           │
    │     - Day of week                    │
    │     - Status (confirmed/cancelled)   │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  3. Count frequencies                │
    │     hour_counts = Counter()          │
    │     day_counts = Counter()           │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  4. Calculate probabilities          │
    │     P(hour) = count / total          │
    │     P(day) = count / total           │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  5. Categorize preference            │
    │     - morning: 7-12h                 │
    │     - afternoon: 12-18h              │
    │     - evening: 18-22h                │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  6. Calculate attendance rate        │
    │     rate = confirmed / total         │
    └──────────┬───────────────────────────┘
               │
               ▼
Output: {
    preferred_hours: {...},
    hour_probability: {...},
    day_probability: {...},
    time_slot_preference: "afternoon",
    attendance_rate: 0.85
}
```

## Constraint Satisfaction Process

```
Input: slot, available_users, constraints

    ┌──────────────────────────────────────┐
    │  Check required_members              │
    │  Are all in available_users?         │
    └──────────┬─────────────┬─────────────┘
               │ YES         │ NO
               ▼             ▼
            PASS          FAIL ──► Add violation
               │
               ▼
    ┌──────────────────────────────────────┐
    │  Check required_mentors              │
    │  Are all in available_users?         │
    └──────────┬─────────────┬─────────────┘
               │ YES         │ NO
               ▼             ▼
            PASS          FAIL ──► Add violation
               │
               ▼
    ┌──────────────────────────────────────┐
    │  Check min_attendees                 │
    │  len(available) >= min?              │
    └──────────┬─────────────┬─────────────┘
               │ YES         │ NO
               ▼             ▼
            PASS          FAIL ──► Add violation
               │
               ▼
    ┌──────────────────────────────────────┐
    │  Check time_constraints              │
    │  In allowed time range?              │
    └──────────┬─────────────┬─────────────┘
               │ YES         │ NO
               ▼             ▼
            PASS          FAIL ──► Add violation
               │
               ▼
    ┌──────────────────────────────────────┐
    │  Check club_filter                   │
    │  Any members from club?              │
    └──────────┬─────────────┬─────────────┘
               │ YES         │ NO
               ▼             ▼
            PASS          FAIL ──► Add violation
               │
               ▼
Output: (is_valid, violations)
```

## Database Schema (Relevant Tables)

```
┌──────────────────┐
│      User        │
├──────────────────┤
│ id               │ PK
│ username         │
│ email            │
│ club             │ (Pro/Multi/GCC)
│ is_admin         │ (mentor flag)
│ created_at       │
└──────┬───────────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│ UserAvailability │
├──────────────────┤
│ id               │ PK
│ user_id          │ FK → User
│ day_of_week      │ (0-6)
│ start_hour       │ (0-23)
│ end_hour         │ (0-23)
│ is_busy          │ (boolean)
│ recurring        │ (boolean)
└──────────────────┘

┌──────────────────┐
│     Booking      │
├──────────────────┤
│ id               │ PK
│ title            │
│ start_time       │ (datetime)
│ end_time         │ (datetime)
│ user_id          │ FK → User
│ room_id          │ FK → Room
│ status           │ (confirmed/cancelled)
│ created_at       │
└──────────────────┘
```

---

## Complexity Analysis

### Time Complexity

```
find_optimal_slots():
    - Days to check: D = 14
    - Hours per day: H = 15 (7am-10pm)
    - Users: U = 20
    - Constraints: C = 5

    Total slots to check: D × H = 210
    Per slot:
        - Get available users: O(U)
        - Check constraints: O(C)
        - Calculate probability: O(U)
        - Score: O(1)

    Total: O(D × H × U × C) = O(14 × 15 × 20 × 5)
         = O(21,000) operations
         ≈ < 1 second
```

### Space Complexity

```
Availability Grid: O(D × H × U)
    = 14 days × 15 hours × 20 users
    = 4,200 entries
    ≈ 50 KB memory

User Patterns Cache: O(U)
    = 20 users × ~500 bytes
    ≈ 10 KB

Total: ~60 KB (Very efficient!)
```

---

## Key Design Decisions

### 1. **Why not just count available users?**
   - Raw count doesn't reflect reality
   - Some users are more reliable than others
   - Pattern learning gives better predictions

### 2. **Why multiple objectives?**
   - Different meetings have different priorities
   - Flexibility for users
   - Better user experience

### 3. **Why cache patterns?**
   - Avoid recomputing for same user
   - Faster when processing multiple slots
   - Memory overhead is minimal

### 4. **Why weighted scoring?**
   - Fine-grained control over optimization
   - Easy to tune for specific needs
   - Transparent decision-making

---

**Architecture designed for:**
- ✅ Performance
- ✅ Scalability
- ✅ Flexibility
- ✅ Maintainability
