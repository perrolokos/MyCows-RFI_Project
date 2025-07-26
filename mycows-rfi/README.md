# MyCows_RFI

MyCows_RFI is a full-stack application designed for advanced livestock management. This platform integrates IoT technology, data analytics, and user-friendly interfaces to optimize the health, reproduction, and productivity of cattle.

## Features

- **Livestock Management**: Comprehensive CRUD operations for each animal, including genetic data, medical history, genealogy, and images.
- **Scoring System**: A specialized interface for scoring animals based on standardized phenotypic templates, providing a quality KPI.
- **IoT Monitoring and Alerts**: Real-time data ingestion from sensors, with automated alerts for critical events such as illness or abnormal behavior.
- **Analytics and Dashboards**: Executive and operational dashboards displaying KPIs and detailed health trends for informed decision-making.
- **Role-Based Access Control**: A robust authentication system that segments access based on user roles, ensuring data security and integrity.

## Project Structure

```
mycows-rfi
├── client                # Frontend application
│   ├── src
│   │   ├── components    # Reusable React components
│   │   ├── pages         # Main application pages
│   │   ├── services      # API calls and business logic
│   │   ├── types         # TypeScript definitions
│   │   └── App.tsx       # Main entry point for React
│   ├── package.json      # Client configuration
│   └── tsconfig.json     # TypeScript configuration for client
├── server                # Backend application
│   ├── src
│   │   ├── controllers   # Request handlers
│   │   ├── models        # Data models
│   │   ├── routes        # API endpoints
│   │   ├── services      # Business logic
│   │   └── app.ts        # Main entry point for server
│   ├── package.json      # Server configuration
│   └── tsconfig.json     # TypeScript configuration for server
├── docker-compose.yml    # Docker configuration
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## Getting Started

### Prerequisites

- Node.js
- Docker and Docker Compose
- PostgreSQL (for the backend)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mycows-rfi
   ```

2. Set up the environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

3. Start the application using Docker:
   ```
   docker-compose up
   ```

### Usage

- Access the frontend application at `http://localhost:3000`.
- The backend API can be accessed at `http://localhost:8000/api`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.