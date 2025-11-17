class ChartGenerator:
    @staticmethod
    def create_chart(data, symbol, chart_type, start_date, end_date):
        if not data or not data['dates']:
            return None

        chart_type_str = 'bar' if chart_type == 1 else 'line'

        # Return HTML/JS block for Chart.js
        html_content = f"""
        <div class="chart-container" style="position: relative; height:600px;">
            <h2>Stock Data for {symbol}: {start_date} to {end_date}</h2>
            <canvas id="stockChart"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('stockChart').getContext('2d');
            new Chart(ctx, {{
                type: '{chart_type_str}',
                data: {{
                    labels: {data['dates']},
                    datasets: [
                        {{
                            label: 'Open',
                            data: {data['open']},
                            borderColor: 'rgba(255,99,132,1)',
                            backgroundColor: 'rgba(255,99,132,0.25)',
                            fill: false
                        }},
                        {{
                            label: 'High',
                            data: {data['high']},
                            borderColor: 'rgba(54,162,235,1)',
                            backgroundColor: 'rgba(54,162,235,0.25)',
                            fill: false
                        }},
                        {{
                            label: 'Low',
                            data: {data['low']},
                            borderColor: 'rgba(75,192,192,1)',
                            backgroundColor: 'rgba(75,192,192,0.25)',
                            fill: false
                        }},
                        {{
                            label: 'Close',
                            data: {data['close']},
                            borderColor: 'rgba(255,206,86,1)',
                            backgroundColor: 'rgba(255,206,86,0.25)',
                            fill: false
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            title: {{
                                display: true,
                                text: 'Price ($)'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Date'
                            }},
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 45
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }}
                }}
            }});
        </script>
        """
        return html_content
