# HR Management Dashboard

This is a comprehensive Human Resources management dashboard built with Vue 3 and Vite. It provides a suite of tools to streamline various HR processes, from recruitment to reporting.

## Features

The application is divided into several key modules, each handling a specific HR function:

*   **<i class="fas fa-home"></i> Home:** A central dashboard providing an overview and quick navigation to different modules.
*   **<i class="fas fa-users"></i> Recruitment:** A complete suite for managing the hiring process.
    *   **Vacancy List:** View and manage open positions.
    *   **Job Posting:** Create and publish new job postings.
    *   **Apply:** A form for candidates to apply for jobs.
    *   **Screening:** Tools for screening and evaluating candidates.
    *   **Hiring Pipeline:** A visual pipeline to track candidates through the hiring stages.
*   **<i class="fas fa-user-check"></i> Onboarding:** Manage the onboarding process for new hires.
*   **<i class="fas fa-chalkboard-teacher"></i> Training:** Coordinate and track employee training programs.
*   **<i class="fas fa-file-invoice-dollar"></i> Expense Management:** A dual-view system for submitting and approving expenses.
    *   **Employee View:** Submit expenses, upload receipts, and track status.
    *   **Manager View:** Review, approve, or reject expense claims.
*   **<i class="fas fa-chart-bar"></i> Reporting:** Generate and view various HR-related reports and analytics.
*   **<i class="fas fa-user-circle"></i> Account:** Manage user account settings and profile.

## Tech Stack

*   **Framework:** Vue 3 (using `<script setup>` SFCs)
*   **Build Tool:** Vite
*   **Charting:** Chart.js via `vue-chartjs` for data visualization in the reporting module.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).
