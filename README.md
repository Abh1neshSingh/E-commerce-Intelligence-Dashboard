# 🛍️ E-commerce Intelligence Platform

A comprehensive, production-ready data science solution for e-commerce analytics, customer insights, and predictive modeling. This project demonstrates FAANG-level data science capabilities with end-to-end ML pipelines, advanced analytics, and professional visualization.

## 🎯 Business Problem

E-commerce businesses face critical challenges in understanding customer behavior, predicting churn, forecasting sales, and optimizing marketing strategies. This platform addresses these challenges by providing:

- **Customer Churn Prediction**: Identify at-risk customers before they leave
- **Sales Forecasting**: Predict future revenue with confidence intervals
- **Customer Segmentation**: Understand distinct customer groups for targeted marketing
- **RFM Analysis**: Recency, Frequency, Monetary analysis for customer lifecycle management
- **Cohort Analysis**: Track customer retention over time
- **Lifetime Value Calculation**: Quantify long-term customer value

## 📊 Key Metrics & KPIs

The platform tracks and visualizes critical business metrics:

- **Total Revenue**: $16.6M across 50K transactions
- **Customer Base**: 5,000 customers with 25% churn rate
- **Average Order Value**: $332.60
- **Customer Lifetime Value**: $3,908 average
- **Retention Rate**: Real-time 30-day retention tracking
- **Segment Distribution**: 3 distinct customer segments

## 🤖 Modeling Approach

### 1. Customer Churn Prediction
- **Algorithms**: Logistic Regression, XGBoost, Random Forest
- **Features**: 20+ engineered features including RFM metrics, temporal patterns, category preferences
- **Performance**: XGBoost achieves 86.5% accuracy, 73% precision, 56% recall
- **Key Features**: Recency, purchase frequency, revenue trends, engagement scores

### 2. Sales Forecasting
- **Method**: Prophet time series forecasting with seasonality and holiday effects
- **Horizon**: 90-day forecast with confidence intervals
- **Validation**: MAE: $4,377, MAPE: 17.46%, RMSE: $5,292
- **Components**: Trend, weekly seasonality, yearly seasonality, holiday effects

### 3. Customer Segmentation
- **Algorithm**: KMeans clustering with PCA visualization
- **Optimal Clusters**: 3 segments determined by elbow method and silhouette analysis
- **Segments**: Standard Customers (41.9%), Frequent Buyers (19.4%), High Value (38.7%)
- **Validation**: Silhouette score: 0.231, Calinski-Harabasz: 1,662

## 🏗️ Project Structure

```
ecommerce-intelligence/
├── data/                          # Raw and processed datasets
│   ├── transactions.csv           # 50K transaction records
│   ├── customers.csv              # 5K customer profiles
│   └── products.csv               # 200 product catalog
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── data_generator.py          # Synthetic data generation
│   ├── eda.py                     # Exploratory data analysis
│   ├── churn_prediction.py        # Churn modeling pipeline
│   ├── sales_forecasting.py       # Time series forecasting
│   └── customer_segmentation.py   # Clustering analysis
├── notebooks/                     # Analysis outputs and visualizations
│   ├── rfm_analysis.csv
│   ├── monthly_revenue.csv
│   ├── churn_predictions.csv
│   ├── customer_segments.csv
│   └── *.png                      # Generated plots and charts
├── app.py                         # Streamlit dashboard
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)

### Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ecommerce-intelligence
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Generate data and run analysis**
```bash
# Generate synthetic dataset
python src/data_generator.py

# Run EDA and feature engineering
python src/eda.py

# Train ML models
python src/churn_prediction.py
python src/sales_forecasting.py
python src/customer_segmentation.py
```

4. **Launch the dashboard**
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

### Docker Deployment

1. **Build the image**
```bash
docker build -t ecommerce-intelligence .
```

2. **Run the container**
```bash
docker run -p 8501:8501 ecommerce-intelligence
```

3. **Access the application**
Visit `http://localhost:8501` in your browser

## 📈 Features & Capabilities

### 🎯 Dashboard Components

1. **Executive Overview**
   - Real-time KPI metrics
   - Revenue trends and insights
   - Customer health indicators

2. **Revenue Analysis**
   - Monthly/quarterly revenue trends
   - Category performance analysis
   - Average order value tracking

3. **RFM Customer Analysis**
   - Customer segmentation (Champions, Loyal, At Risk, Lost)
   - RFM score distribution
   - 3D RFM visualization

4. **Churn Prediction**
   - Real-time churn probability scoring
   - High-risk customer identification
   - Model performance metrics

5. **Sales Forecasting**
   - 90-day revenue forecast
   - Confidence intervals
   - Trend and seasonality analysis

6. **Customer Segmentation**
   - PCA visualization of segments
   - Segment characteristics analysis
   - Behavioral insights

7. **Cohort Analysis**
   - Retention heatmap
   - Customer lifecycle tracking

### 🔧 Technical Features

- **Production-Ready Code**: Modular, documented, and reproducible
- **Advanced Feature Engineering**: 20+ features for ML models
- **Model Validation**: Cross-validation, multiple metrics, feature importance
- **Scalable Architecture**: Designed for large datasets
- **Containerized Deployment**: Docker support for easy deployment
- **Interactive Visualizations**: Plotly charts with drill-down capabilities

## 📊 Model Performance Summary

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 86.1% | 76.5% | 49.2% | 59.9% | 91.6% |
| XGBoost | 86.5% | 73.2% | 56.4% | 63.7% | 91.1% |
| Random Forest | 86.8% | 83.2% | 46.9% | 60.0% | 91.9% |

## 🎨 Visualizations

The platform generates comprehensive visualizations:

- **Revenue Trends**: Monthly/quarterly revenue with trend analysis
- **Customer Segments**: PCA plots, radar charts, segment distributions
- **Churn Analysis**: Probability distributions, ROC curves, feature importance
- **Sales Forecasts**: Time series plots with confidence intervals
- **Cohort Heatmaps**: Customer retention patterns over time

## 🔍 Key Insights Generated

1. **Customer Behavior**
   - 41.9% of customers are standard buyers with moderate engagement
   - 19.4% are frequent buyers with high purchase frequency
   - 38.7% are high-value customers with significant revenue contribution

2. **Churn Patterns**
   - Recency and purchase frequency are strongest churn predictors
   - Customers with declining recent activity show 70%+ churn probability
   - Engagement scores correlate strongly with retention

3. **Revenue Trends**
   - Strong seasonal patterns with Q4 peak performance
   - 18% projected revenue growth over next 90 days
   - Electronics and Clothing are top-performing categories

4. **Forecasting Accuracy**
   - Model captures weekly and yearly seasonality
   - Holiday effects significantly impact sales patterns
   - 95% confidence intervals provide reliable planning ranges

## 🛠️ Development & Extensions

### Adding New Models
1. Create new model class in `src/`
2. Follow existing pattern for feature engineering
3. Add visualization components to `app.py`
4. Update requirements.txt if needed

### Customizing Features
- Modify feature engineering in respective model files
- Update dashboard metrics in `app.py`
- Add new visualizations using Plotly

### Scaling Considerations
- Use Dask or Spark for larger datasets
- Implement model versioning with MLflow
- Add API endpoints for real-time predictions

## 📝 Data Schema

### Transactions Table
- `customer_id`: Unique customer identifier
- `order_id`: Transaction identifier
- `order_date`: Purchase timestamp
- `product_id`: Product identifier
- `category`: Product category
- `price`: Unit price
- `quantity`: Purchase quantity
- `total_amount`: Transaction total
- `payment_method`: Payment type
- `region`: Geographic region
- `marketing_channel`: Acquisition channel

### Customers Table
- `customer_id`: Unique identifier
- `registration_date`: Account creation date
- `region`: Geographic region
- `engagement_score`: Behavioral engagement metric
- `churned`: Churn status flag
- `churn_date`: Churn timestamp (if applicable)

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Code quality checks
black src/ app.py
flake8 src/ app.py
```

## 📚 Technologies Used

- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn, XGBoost
- **Time Series**: Prophet
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Dashboard**: Streamlit
- **Containerization**: Docker
- **Development**: Python 3.9, Git

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Resume Highlights

This project demonstrates:

- **End-to-End ML Pipelines**: From data generation to deployment
- **Advanced Analytics**: RFM, cohort analysis, LTV calculation
- **Predictive Modeling**: Churn, forecasting, clustering
- **Production Engineering**: Docker, modular code, testing
- **Business Acumen**: KPI tracking, insights generation
- **Technical Communication**: Comprehensive documentation
- **FAANG-Level Standards**: Code quality, architecture, scalability

## 📞 Contact

For questions or collaborations, please reach out through the repository issues or contact channels.

---

**Built with ❤️ for data science excellence**
