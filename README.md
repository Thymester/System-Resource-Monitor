# System Resource Monitor

## Summary

The System Resource Monitor is a Python application built using the Tkinter GUI toolkit. It provides real-time monitoring of CPU and memory usage on a computer system. The application allows users to set thresholds for CPU and memory usage, and it sends notifications when these thresholds are exceeded. Additionally, users can export the monitored data to a CSV file for further analysis.

## Features

- **Resource Monitoring:** Continuous monitoring of CPU and memory usage in real-time.
- **Threshold Setting:** Users can set custom thresholds for CPU and memory usage. Notifications are sent upon threshold breaches.
- **Graphical Representation:** Monitored data is graphically presented in a line chart, showing CPU and memory usage over time.
- **Export Data:** Option to export monitored data to a CSV file for external analysis or record-keeping.
- **System Information Display:** Provides basic system information such as the number of CPU cores, total system RAM, and OS platform.

## About CPU Monitoring Interval

The CPU Monitoring Interval, as implemented in this application, refers to the length of time during which the application tracks and collects data on the CPU usage of the system before updating the graphical representation of CPU usage.

In simpler terms, when you set the CPU Monitoring Interval to a specific value (in seconds), the application waits for that duration before sampling the CPU usage again. After the specified interval, it calculates the average CPU usage over that time period and updates the graph accordingly.

For example, if you set the CPU Monitoring Interval to 1 second, the application will sample the CPU usage every second and update the graph based on the average CPU usage over each one-second interval. This allows for more frequent updates and potentially more granular insights into CPU usage patterns.

On the other hand, if you set the interval to a longer duration, such as 5 seconds, the application will wait for 5 seconds before sampling the CPU again and updating the graph. This might result in less frequent updates but could be useful for observing trends over longer periods.

In summary, the CPU Monitoring Interval determines how often the application refreshes and updates the CPU usage data on the graphical interface, providing users with insights into CPU performance over specified time intervals.

## How to Use

1. **Threshold Setting:** Enter desired CPU and memory thresholds.
2. **Start Monitoring:** Click "Start Monitoring" to begin monitoring.
3. **Stop Monitoring:** Click "Stop Monitoring" to pause monitoring.
4. **Export Data:** Click "Export Data" to save monitored data to a CSV file.

## Dependencies

- Tkinter: Python's standard GUI toolkit.
- psutil: Cross-platform library for retrieving system information.
- matplotlib: Plotting library for visualizations.
- plyer: Library for accessing platform features such as notifications.

## Usage

1. Clone the repository to your local machine.
2. Install dependencies.
3. Run the Python script.

## Contributing

Contributions are welcome! Open an issue for bug fixes, feature requests, or enhancements. Pull requests are appreciated.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.

## Authors

- Thymester/Tyler

## Disclaimer

This application is provided as-is without any warranty. The authors and contributors are not responsible for any damage or loss caused by the use of this software.
