# FINM 32500: Computing for Finance in Python

A comprehensive collection of assignments and projects from the University of Chicago's FINM 32500 course (Autumn 2025), 
focusing on building production-grade quantitative trading systems and tools used on real trading desks.

## 📚 Course Overview

This repository contains hands-on coursework for aspiring buy-side/sell-side quants and quant developers, covering:

- **Backtesting Engines**: Design and implement a full-featured backtester to simulate and refine trading strategies using historical data
- **Real-Time Trading Systems**: Build live trading engines that ingest market feeds, apply strategy logic, and execute orders via the Alpaca API
- **Performance Optimization**: Profile and optimize Python code using cProfile, py-spy, vectorization, and algorithmic complexity analysis
- **Advanced Python**: Master decorators, context managers, type hints, async I/O, generators, and metaprogramming
- **Parallel Computing**: Scale compute-intensive tasks using threading, multiprocessing, and Dask
- **Machine Learning Integration**: Incorporate scikit-learn and XGBoost into trading workflows with rigorous evaluation
- **Production Systems**: Structure codebases with pytest, CI/CD pipelines, and Docker containerization

## 🗂️ Repository Structure

```
finm-python/
├── docs/           # Weekly assignment instructions
├── data/           # Market data, historical datasets, and trading feeds
├── notebooks/      # Jupyter notebooks for in-class examples and quizs
├── scripts/        # Standalone Python scripts and utilities
└── src/            # Source code modules for homeworks
    └── finm_python
        ├── __init__.py
        ├── hw1/    # CSV-Based Algorithmic Trading Backtester
        ├── hw2/    # Multi-Signal Strategy Simulation on S&P 500
        ├── hw3/    # Runtime & Space Complexity in Financial Signal Processing
```

## 📖 Course Topics

| Theme | Focus Area | Key Activities |
|-------|------------|----------------|
| 1 | Python Refresher | Data types, control flow, functions |
| 2 | Advanced Language Features | OOP patterns, decorators, context managers |
| 3 | Iterators, Generators & Metaprogramming | Custom iterators, generator pipelines, metaclasses |
| 4 | Testing & CI | Writing tests with pytest, mocks, coverage reports, GitHub Actions |
| 5 | Performance Tuning & Optimization | Vectorized operations, memory-usage tuning, targeted algorithmic refinements |
| 6 | Algorithmic Complexity & Data Structures | Big-O analysis, divide-and-conquer, dynamic programming, heaps, bloom filters |
| 7 | Backtester Foundations | Building a backtesting engine, metrics computation, result visualization |
| 8 | Strategy Design & Simulation | Momentum and mean-reversion models, parameter sweeps, risk analysis |
| 9 | Parallel Computing & Concurrency | threading, multiprocessing, Dask for batch and real-time workloads |
| 10 | Real-Time Streaming & Socket Programming | TCP/UDP sockets, non-blocking I/O, message framing, error recovery |
| 11 | Machine Learning in Trading | Feature engineering, model training, backtest integration |
| 12 | Project Wrap-up | End-to-end integration, final demos |

## 🛠️ Technologies Used

- **Python 3.9+** with venv/conda environments
- **Data & Analysis**: pandas, NumPy, Matplotlib, Plotly
- **Testing & CI/CD**: pytest, unittest.mock, GitHub Actions
- **Performance**: cProfile, py-spy, algorithmic optimization
- **Parallel Computing**: threading, multiprocessing, Dask
- **Networking**: Python socket, ZeroMQ
- **Machine Learning**: scikit-learn, XGBoost
- **Trading Platform**: Alpaca Python SDK
- **Containerization**: Docker

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Prior programming experience in any language
- Basic familiarity with command line (Linux/macOS/Windows)
- Git for version control

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dafu-zhu/finm-python.git
cd finm-python
```

2. Create and activate a virtual environment with uv:
```bash
uv sync
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Set up Alpaca API credentials (for trading projects):
```bash
export APCA_API_KEY_ID="your_key_here"
export APCA_API_SECRET_KEY="your_secret_here"
```

## 📊 Key Deliverables

### Weekly Assignments (15%)
Group-based assignments (teams of 4) covering:
- Advanced Python features and design patterns
- Performance optimization and profiling
- Testing and CI/CD implementation
- Algorithm complexity analysis

### Alpaca Trading Competition (15%)
End-to-end trading system featuring:
- Live market data ingestion via Alpaca API
- Custom trading strategy implementation
- Automated order execution and management
- Real-time performance monitoring
- Comprehensive backtesting and validation

**Competition Metrics**:
- Risk-adjusted returns (Sharpe ratio, Sortino)
- Net profit and loss
- System resilience and error handling
- Code quality and maintainability

### Assessments
- **Midterm Exam** (30%): Closed book, onsite
- **Final Exam** (35%): Closed book, onsite
- **Participation & Code Reviews** (5%)

## 📚 Recommended Resources

- *High-Performance Python* by Micha Gorelick & Ian Ozsvald
- *Designing Data-Intensive Applications* by Martin Kleppmann
- [Alpaca API Documentation](https://alpaca.markets/docs/)
- [pandas Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [ZeroMQ Guide](https://zguide.zeromq.org/)

## 📝 License

This repository is for educational purposes as part of FINM 32500 coursework at the University of Chicago.

## 👤 Author

**Dafu Zhu**
- GitHub: [@dafu-zhu](https://github.com/dafu-zhu)
- Course: FINM 32500 - Computing for Finance in Python (Autumn 2025)
- Program: Financial Mathematics, University of Chicago

## 🙏 Acknowledgments

- Instructor: [Sebastien Donadio](https://www.linkedin.com/in/sebastien-donadio-01481920/)
- Alpaca Markets for API access and trading simulation platform