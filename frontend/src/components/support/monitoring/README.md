# Monitoring Components

This directory contains Vue components for system monitoring and performance tracking.

## Available Components

- **PerformanceMetrics.vue**: Displays system performance metrics including response times, request rates, and endpoint performance.
- **ErrorReporting.vue**: Shows error logs with filtering options and details view.
- **SystemHealth.vue**: Provides an overview of system health including service statuses.

## Authentication Requirements

The monitoring components require a valid authentication token with the **"support"** role to access backend data. Without proper authentication:

- Components will display mock data for development and testing purposes
- Real-time data fetching from the backend will fail with 401 errors

## Usage

To use these components:

1. Ensure the user is logged in with a valid token
2. Verify the user has the "support" role
3. Import the desired component:

```javascript
import PerformanceMetrics from '@/components/support/monitoring/PerformanceMetrics.vue';
import ErrorReporting from '@/components/support/monitoring/ErrorReporting.vue';
```

4. Use the components in your template:

```html
<template>
  <div>
    <PerformanceMetrics />
    <ErrorReporting />
  </div>
</template>
```

## API Endpoints

The components connect to these backend endpoints:

- `/api/v1/monitoring/health`: System health status
- `/api/v1/monitoring/metrics`: System performance metrics
- `/api/v1/monitoring/errors`: Error logs with filtering
- `/api/v1/monitoring/performance`: Historical performance data
- `/api/v1/monitoring/endpoints`: Endpoint-specific performance metrics
- `/api/v1/monitoring/dashboard`: Dashboard summary data
- `/api/v1/monitoring/alerts`: System alerts

These endpoints require authentication and the "support" role.

## Development Notes

When developing or testing without authentication:
- Mock data will be displayed instead of live data
- Authentication can be tested by logging in as a user with the "support" role
- The service automatically falls back to mock data when API calls fail 