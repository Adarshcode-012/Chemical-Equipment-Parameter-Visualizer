# Chemical Equipment Parameter Visualizer

A full-stack application for visualizing and analyzing chemical equipment parameters. This project demonstrates a hybrid architecture using **Django** for the backend, **React** for the web interface, and **PyQt5** for a desktop client.

## Overview
Engineers often need to analyze equipment performance data (flow rates, pressures, temperatures) quickly. This tool allows users to upload standard CSV logs, automatically computes summary statistics, and visualizes equipment type distributions.

**Key Features:**
*   **Hybrid Client Support**: Access via web browser or native desktop application.
*   **Automated Analysis**: Instant calculation of averages and totals upon upload.
*   **Reporting**: Generates downloadable PDF reports for documentation.
*   **Data Lifecycle**: automatically retains only the most recent datasets to manage storage.

## Tech Stack

### Backend
*   **Django & Django REST Framework**: robust API design.
*   **Pandas**: Efficient data processing and analysis.
*   **SQLite**: Lightweight transactional database.
*   **ReportLab**: Programmatic PDF generation.

### Web Client
*   **React**: Component-based UI.
*   **Chart.js**: Responsive data visualization.
*   **Axios**: Promise-based HTTP client.

### Desktop Client
*   **PyQt5**: Native GUI framework.
*   **Matplotlib**: Scientific plotting integration.

## Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js 14+

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/chemical-equipment-visualizer.git
    cd chemical-equipment-visualizer
    ```

2.  **Initialize Database (First Run Only):**
    ```bash
    cd backend
    pip install -r ../requirements.txt
    python manage.py migrate
    python create_superuser.py
    ```
    *Creates default admin user: `admin` / `admin123`*

3.  **Start Production Server:**
    ```bash
    python run_prod.py
    ```
    Access the application at: `http://localhost:8080`

4.  **Run Desktop Client (Optional):**
    ```bash
    cd desktop
    pip install -r requirements.txt
    python app.py
    ```

## Project Structure
```
├── backend/            # Django API & Server logic
├── web/                # React Source Code
├── desktop/            # PyQt5 Application
└── sample_equipment_data.csv     # Example input file
```

## License
MIT

## Created By
[Adarshcode-012](https://github.com/Adarshcode-012)
