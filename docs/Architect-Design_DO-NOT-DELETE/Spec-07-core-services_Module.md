# SPEC-07: Core Services Module

1. Background
The  Core Services  module comprises foundational microservices that power authentication, user
management, configuration, feature toggles, and telemetry ingestion across the Hearthlink ecosystem.
Core Services underpin all other modules (Alden, Alice, Mimic, Synapse, Vault, Sentry) by providing stable,
secure APIs for identity, permissions, settings, and analytics.
2. Requirements (MoSCoW)
## Must have
• OAuth2.0/OpenID Connect provider issuing JWTs and supporting introspection
• User Profile Service with CRUD APIs and encrypted-at-rest storage
• Feature Flag Service for dynamic toggles with rollout and audit logging
• Configuration Store: versioned key-value settings scoped by environment
• Metrics Ingestion API: high-throughput bulk write to time-series DB (Prometheus/Timescale)
## Should have
• Analytics Query API: pre-aggregated telemetry for dashboards
• Centralized Rate-Limit Service with policy management
## Could have
• Billing & Usage reporting for cost analysis
• Service Catalog UI for API discovery
Won’t have (this increment)
• GraphQL Gateway
• Advanced A/B testing engine
3. Method
## 3.1 Architecture Diagram
@startuml
package "Core Services" {
[Auth Service] --> [User DB]
[Profile Service] --> [User DB]
[Feature Flag Service] --> [Config Store]
[Config Store] --> [Config DB]
[Metrics API] --> [Metrics Store]
1
[RateLimit Service] --> [RateLimit Store]
}
package "Consumers" {
[UI Modules]
[Synapse]
[Sentry]
[Vault]
[Mimic]
}
[Consumers] --> [Auth Service]
[Consumers] --> [Profile Service]
[Consumers] --> [Feature Flag Service]
[Consumers] --> [Config Store]
[Consumers] --> [Metrics API]
[Consumers] --> [RateLimit Service]
@enduml
## 3.2 Data Schema
@startuml
table Users {
+ user_id      : UUID [PK]
+ email        : VARCHAR [UNIQUE]
+ password_hash: VARCHAR
+ created_at   : TIMESTAMP
+ last_login   : TIMESTAMP
}
table Roles {
+ role_name    : VARCHAR [PK]
+ description  : TEXT
}
table UserRoles {
+ user_id     : UUID [FK]
+ role_name   : VARCHAR [FK]
+ assigned_at : TIMESTAMP
}
table FeatureFlags {
+ flag_name   : VARCHAR [PK]
+ enabled      : BOOLEAN
+ rollout_pct  : INT
+ metadata     : JSON
+ updated_at   : TIMESTAMP
}
2
table Configurations {
+ key         : VARCHAR [PK]
+ value       : JSON
+ version     : INT
+ environment : VARCHAR
+ updated_at  : TIMESTAMP
}
table Metrics {
+ metric_id   : BIGINT [PK, auto]
+ namespace   : VARCHAR
+ name        : VARCHAR
+ labels      : JSON
+ value       : DOUBLE
+ timestamp   : TIMESTAMP
}
table RateLimits {
+ service     : VARCHAR [PK]
+ key         : VARCHAR [PK]
+ limit       : INT
+ window_sec  : INT
+ updated_at  : TIMESTAMP
}
@enduml
4. UI Components & Wireframes
## 4.1 User Management Panel
+--------------------------------------------------+
| User Management                                  |
| [Create User] [Bulk Import ▼] [Refresh]          |
|--------------------------------------------------|
| [Users Table: ID, Email, Roles, Last Login]      |
+--------------------------------------------------+
## Component Function Data/API Call
## Lists users with pagination
UsersTable GET /v1/users?limit=50&page=1
and filters
## CreateUserButton Opens new user form N/A
## BulkImportDropdown Handles CSV/YAML import POST /v1/users/import
3
## Component Function Data/API Call
## RefreshButton Reloads user list GET /v1/users
PUT /v1/users/{id} ,  DELETE /v1/
## UserActionsCell Edit/Delete per user
users/{id}
## 4.2 Roles & Permissions Panel
+--------------------------------------------------+
| Roles & Permissions                              |
| [Add Role] [Export Roles]                        |
|--------------------------------------------------|
| [Roles Table: Role Name, Description, Assigned]  |
+--------------------------------------------------+
## Component Function Data/API Call
## RolesTable Lists roles GET /v1/roles
## AddRoleButton Opens form to create role N/A
## ExportRolesButton Exports role list GET /v1/roles/export
## AssignRoleDialog Map users to roles POST /v1/userroles
## 4.3 Feature Flags Panel
+--------------------------------------------------+
| Feature Flags                                    |
| [New Flag] [Import Flags] [Toggle All]           |
|--------------------------------------------------|
| [Flags Table: Name, Enabled, Rollout%, Updated]  |
+--------------------------------------------------+
## Component Function Data/API Call
## FlagsTable Lists feature flags GET /v1/flags
## NewFlagButton Creates or updates a flag N/A
## ImportFlagsButton Bulk import flags POST /v1/flags/import
ToggleFlagSwitch Enable/disable flag PUT /v1/flags/{name}
4
## 4.4 Configuration Store Panel
+--------------------------------------------------+
| Configuration Store                              |
| [Add Config] [Export]                            |
|--------------------------------------------------|
| [Config Table: Key, Value (JSON), Version, Env]  |
+--------------------------------------------------+
## Component Function Data/API Call
ConfigTable Shows config entries GET /v1/config?environment=prod
## AddConfigButton Opens entry form N/A
## ExportConfigButton Exports config JSON GET /v1/config/export
## EditConfigDialog Edit value/version/env POST /v1/config
## 4.5 Metrics Ingestion Panel
+--------------------------------------------------+
| Metrics Ingestion                                |
| [Upload File ▼] [Send Batch]                     |
|--------------------------------------------------|
| [Batch Status: Last Ingest Count, Errors]        |
+--------------------------------------------------+
## Component Function Data/API Call
## UploadFileDropdown Selects metrics file for batch ingest N/A
## SendBatchButton Sends file payload POST /v1/metrics/bulk
## BatchStatusCard Displays last ingest results N/A
## 4.6 Full-Screen Conference Room Interface
+===================================================================================+
|                             Conference Room
Management                              |
| [Create Room] [Join Room ▼] [Leave Room] [End Room]
[Refresh]                       |
|-----------------------------------------------------------------------------------|
|  Rooms
List                                                                        |
5
|  +---------------------------------------------------------------------------
+      |
|  | ID    | Name             | Participants | Status   | Created At
|      |
|  +---------------------------------------------------------------------------
+      |
|
|
|  +-----------------------------+   +-----------------------------
+                |
|  | Room Detail Pane            |   | Participants List
|                |
|  | - Name: <Room Name>         |   | - User A
|                |
|  | - ID: <UUID>                |   | - User B
|                |
|  | - Status: Active            |   | - ...
|                |
|  | - Created: <Timestamp>      |   |
|                |
|  | - Settings: [Edit] [Delete] |   | [Add Participant ▼]
|                |
|  +-----------------------------+   +-----------------------------
+                |
+===================================================================================+
## Component Function Data/API Call
## Global actions and room
## ConferenceHeaderBar N/A
filters
## Full-screen table of rooms
## RoomsListTable GET /v1/conference/rooms
with sorting and pagination
Detailed view/edit of GET /v1/conference/rooms/{id} ,
## RoomDetailPane
selected room settings PUT /v1/conference/rooms/{id}
Lists and manages GET /v1/conference/rooms/{id}/
## ParticipantsList
participants participants
POST /v1/conference/rooms/{id}/
## AddParticipantDropdown Adds users to room
participants
## Opens modal to configure
## CreateRoomButton POST /v1/conference/rooms
new room
POST /v1/conference/rooms/{id}/
## JoinRoomButton Joins selected room
join
6
## Component Function Data/API Call
POST /v1/conference/rooms/{id}/
## LeaveRoomButton Leaves current room
leave
POST /v1/conference/rooms/{id}/
## EndRoomButton Ends and archives room
end
## RefreshButton Reloads room list and details GET /v1/conference/rooms
## 4.7 Full-Screen Project Command Workspace
+===================================================================================+
|                               Project Command
Workspace                            |
| [New Command] [Import SOP ▼] [Export Commands]
[Refresh]                          |
|-----------------------------------------------------------------------------------|
| Commands
Catalog                                                                  |
|  +-------------------------------------------------------------------------
+      |
|  | ID   | Type          | Status      | Triggered By | Created At      |
|
|  +-------------------------------------------------------------------------
+      |
|
|
|  +-----------------------------+   +----------------------------------------
+      |
|  | Command Detail Pane         |   | SOP Template Library
|      |
|  | - ID: <UUID>                |   | - SOP A
|      |
|  | - Type: <Type>              |   | - SOP B
|      |
|  | - Status: Pending/Running   |   | - ...
|      |
|  | - Output: (Log or result)   |   | [Search SOP ▼]
|      |
|  | - Actions: [Execute] [Cancel]|  +----------------------------------------
+      |
|  +-----------------------------+                                            |
+===================================================================================+
7
## Component Function Data/API Call
Global actions: new, import/
## CommandWorkspaceHeader N/A
export, refresh
## Full-screen table listing
## CommandsCatalogTable GET /v1/commands
commands with filters
## Detailed view of selected
GET /v1/commands/{id} ,
## CommandDetailPane command including logs and
PUT /v1/commands/{id}
results
## Sidebar listing SOP templates for GET /v1/commands/sop-
## SOPTemplateLibrary
new commands templates
Triggers execution of selected POST /v1/commands/{id}/
## ExecuteCommandButton
command execute
POST /v1/commands/{id}/
## CancelCommandButton Cancels a running command
cancel
## Exports command list as JSON or
## ExportCommandsButton GET /v1/commands/export
## CSV
## Reloads command catalog and
## RefreshButton GET /v1/commands
details
5. API Endpoints Project Command Panel
+--------------------------------------------------+
| Project Command                                  |
| [New Command] [Import SOP ▼] [Execute]           |
|--------------------------------------------------|
| [Commands List: ID, Type, Status, TriggeredBy]   |
+--------------------------------------------------+
## Component Function Data/API Call
## CommandsListTable Lists project commands GET /v1/commands
## Opens form to create a command via
## NewCommandButton N/A
## SOP template
## ImportSOPDropdown Bulk import SOP definitions POST /v1/commands/import
POST /v1/commands/{id}/
## ExecuteButton Trigger selected command
execute
Displays real-time status of command GET /v1/commands/{id}/
## CommandStatusBadge
execution status
8
5. API Endpoints. API Endpoints
## Service Method Path Description Auth Scope
## Obtain access
## Auth Service POST /oauth/token public
token
## GET /oauth/introspect Validate token auth.introspect
## Profile Service POST /v1/users Create user profile.write
## GET /v1/users List users profile.read
PUT /v1/users/{id} Update user profile.write
DELETE /v1/users/{id} Deactivate user profile.write
## Feature Flag
## GET /v1/flags List flags flag.read
## Service
## Create/update
## POST /v1/flags flag.write
flag
/v1/config? Fetch config
## Config Service GET config.read
environment={env} values
## Create/update
## POST /v1/config config.write
config
## Ingest metrics
## Metrics API POST /v1/metrics/bulk metrics.write
batch
Rate-Limit /v1/ratelimits/{service}/
## GET Get rate limits ratelimit.read
Service {key}
6. Implementation
1. Provision databases (PostgreSQL & TimescaleDB) and Redis for rate-limits.
2. Deploy Auth & Profile services with OIDC flows (Keycloak or custom).
3. Implement Feature Flag and Config services (e.g. Unleash, custom Go service).
4. Build Metrics ingestion endpoint: handle JSON/CSV payloads efficiently.
5. Develop rate-limit sidecar using Redis token bucket algorithm.
6. Secure mTLS and audit logging for all service calls.
7. Write unit, integration, and performance tests (target 5k req/sec).
7. Milestones
## Milestone Timeline Owner
## Auth & Profile MVP Week 1-2 Security Team
9
## Milestone Timeline Owner
Feature Flags & Config MVP Week 3 Backend Team
## Metrics Ingestion & Rate-Limit Week 4 SRE/DevOps Team
## UI Panel Implementations Week 5 Frontend Team
## Security Hardening & Auditing Week 6 Security Team
## Performance & Fault Testing Week 7-8 QA Team
8. Gathering Results
• Auth token latency <50 ms; introspection <20 ms.
• User management operations success rate >99.9%.
• Feature flag toggle latency <20 ms.
• Config reads/writes <50 ms.
• Metrics ingestion throughput >20k points/sec.
• Rate-limit accuracy >99.9% under bursts.
9. References & Dependencies
• Integration Blueprints: appendix_b_integration_blueprints.md
• UI Blueprints: appendix_c_ui_blueprints.md
• DevOps Guide: _DEVELOPMENT_OPERATIONS_GUIDE.md
• Security Policies: VOICE_ACCESS_POLICY.md & SOP_Role_Assignment.md
Need Professional Help in Developing Your Architecture?
Please contact me at sammuti.com :)
10