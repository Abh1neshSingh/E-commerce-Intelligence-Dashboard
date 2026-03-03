"""
Exploratory Data Analysis for E-commerce Intelligence Platform
Comprehensive analysis including revenue trends, RFM analysis, cohort analysis, and LTV calculation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class EcommerceEDA:
    """Comprehensive EDA for e-commerce data."""
    
    def __init__(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame, products_df: pd.DataFrame):
        """
        Initialize EDA with dataframes.
        
        Args:
            transactions_df: Transaction data
            customers_df: Customer data  
            products_df: Product data
        """
        self.transactions = transactions_df.copy()
        self.customers = customers_df.copy()
        self.products = products_df.copy()
        
        # Convert date columns
        self.transactions['order_date'] = pd.to_datetime(self.transactions['order_date'])
        self.customers['registration_date'] = pd.to_datetime(self.customers['registration_date'])
        if 'churn_date' in self.customers.columns:
            self.customers['churn_date'] = pd.to_datetime(self.customers['churn_date'])
        
        # Add time-based features
        self.transactions['year'] = self.transactions['order_date'].dt.year
        self.transactions['month'] = self.transactions['order_date'].dt.month
        self.transactions['quarter'] = self.transactions['order_date'].dt.quarter
        self.transactions['day_of_week'] = self.transactions['order_date'].dt.day_name()
    
    def revenue_trends(self) -> Dict[str, Any]:
        """Analyze revenue trends over time."""
        print("Analyzing Revenue Trends...")
        
        # Monthly revenue
        monthly_revenue = self.transactions.groupby(['year', 'month']).agg({
            'total_amount': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        
        monthly_revenue['date'] = pd.to_datetime(monthly_revenue[['year', 'month']].assign(day=1))
        monthly_revenue['avg_order_value'] = monthly_revenue['total_amount'] / monthly_revenue['order_id']
        
        # Quarterly revenue
        quarterly_revenue = self.transactions.groupby(['year', 'quarter']).agg({
            'total_amount': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        
        quarterly_revenue['period'] = quarterly_revenue['year'].astype(str) + '-Q' + quarterly_revenue['quarter'].astype(str)
        quarterly_revenue['avg_order_value'] = quarterly_revenue['total_amount'] / quarterly_revenue['order_id']
        
        # Daily patterns
        daily_revenue = self.transactions.groupby('day_of_week').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        # Reorder days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_revenue['day_of_week'] = pd.Categorical(daily_revenue['day_of_week'], categories=days_order, ordered=True)
        daily_revenue = daily_revenue.sort_values('day_of_week')
        
        return {
            'monthly': monthly_revenue,
            'quarterly': quarterly_revenue,
            'daily': daily_revenue
        }
    
    def top_categories_analysis(self) -> Dict[str, Any]:
        """Analyze top performing categories."""
        print("Analyzing Top Categories...")
        
        # Category performance
        category_performance = self.transactions.groupby('category').agg({
            'total_amount': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        category_performance['avg_order_value'] = category_performance['total_amount'] / category_performance['order_id']
        category_performance['avg_quantity_per_order'] = category_performance['quantity'] / category_performance['order_id']
        category_performance = category_performance.sort_values('total_amount', ascending=False)
        
        # Category trends over time
        category_monthly = self.transactions.groupby(['category', 'year', 'month']).agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        category_monthly['date'] = pd.to_datetime(category_monthly[['year', 'month']].assign(day=1))
        
        return {
            'performance': category_performance,
            'trends': category_monthly
        }
    
    def rfm_analysis(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Perform RFM (Recency, Frequency, Monetary) analysis."""
        print("Performing RFM Analysis...")
        
        # Calculate RFM metrics
        current_date = self.transactions['order_date'].max() + timedelta(days=1)
        
        rfm = self.transactions.groupby('customer_id').agg({
            'order_date': lambda x: (current_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'total_amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Create RFM scores (1-5, where 5 is best)
        rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['M_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        # Convert to numeric
        rfm['R_score'] = rfm['R_score'].astype(int)
        rfm['F_score'] = rfm['F_score'].astype(int)
        rfm['M_score'] = rfm['M_score'].astype(int)
        
        # Calculate RFM score
        rfm['RFM_score'] = rfm['R_score'] * 100 + rfm['F_score'] * 10 + rfm['M_score']
        
        # Segment customers
        def segment_customers(row):
            if row['R_score'] >= 4 and row['F_score'] >= 4:
                return 'Champions'
            elif row['R_score'] >= 3 and row['F_score'] >= 3:
                return 'Loyal Customers'
            elif row['R_score'] >= 4 and row['F_score'] <= 2:
                return 'New Customers'
            elif row['R_score'] <= 2 and row['F_score'] >= 3:
                return 'At Risk'
            elif row['R_score'] <= 2 and row['F_score'] <= 2:
                return 'Lost'
            else:
                return 'Others'
        
        rfm['segment'] = rfm.apply(segment_customers, axis=1)
        
        # Segment statistics
        segment_stats = rfm.groupby('segment').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean'
        }).reset_index()
        segment_stats.columns = ['segment', 'count', 'avg_recency', 'avg_frequency', 'avg_monetary']
        
        return rfm, {'segment_stats': segment_stats}
    
    def cohort_analysis(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Perform cohort retention analysis."""
        print("Performing Cohort Analysis...")
        
        # Get customer's first purchase date
        customer_first_purchase = self.transactions.groupby('customer_id')['order_date'].min().reset_index()
        customer_first_purchase.columns = ['customer_id', 'first_purchase_date']
        
        # Merge with transactions
        cohort_data = self.transactions.merge(customer_first_purchase, on='customer_id')
        
        # Calculate cohort period (in months)
        cohort_data['order_period'] = (cohort_data['order_date'].dt.year - cohort_data['first_purchase_date'].dt.year) * 12 + \
                                     (cohort_data['order_date'].dt.month - cohort_data['first_purchase_date'].dt.month)
        
        # Create cohort groups based on first purchase month
        cohort_data['cohort_group'] = cohort_data['first_purchase_date'].dt.to_period('M')
        
        # Build cohort table
        cohort_counts = cohort_data.groupby(['cohort_group', 'order_period'])['customer_id'].nunique().reset_index()
        cohort_sizes = cohort_data.groupby('cohort_group')['customer_id'].nunique().reset_index()
        cohort_sizes.columns = ['cohort_group', 'cohort_size']
        
        # Merge and calculate retention rates
        cohort_table = cohort_counts.merge(cohort_sizes, on='cohort_group')
        cohort_table['retention_rate'] = cohort_table['customer_id'] / cohort_table['cohort_size']
        
        # Pivot for heatmap
        cohort_pivot = cohort_table.pivot(index='cohort_group', columns='order_period', values='retention_rate')
        
        # Calculate average retention by period
        avg_retention = cohort_table.groupby('order_period')['retention_rate'].mean().reset_index()
        
        return cohort_pivot, {'avg_retention': avg_retention, 'cohort_sizes': cohort_sizes}
    
    def customer_lifetime_value(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Calculate Customer Lifetime Value (LTV)."""
        print("Calculating Customer Lifetime Value...")
        
        # Calculate basic customer metrics
        customer_metrics = self.transactions.groupby('customer_id').agg({
            'order_date': ['min', 'max', 'count'],
            'total_amount': ['sum', 'mean'],
            'quantity': 'sum'
        }).reset_index()
        
        # Flatten column names
        customer_metrics.columns = ['customer_id', 'first_order', 'last_order', 'order_count', 
                                  'total_revenue', 'avg_order_value', 'total_quantity']
        
        # Calculate customer lifespan in days
        customer_metrics['lifespan_days'] = (customer_metrics['last_order'] - customer_metrics['first_order']).dt.days + 1
        
        # Calculate average order frequency (orders per month)
        customer_metrics['avg_order_frequency'] = customer_metrics['order_count'] / (customer_metrics['lifespan_days'] / 30)
        
        # Calculate LTV using different methods
        # Method 1: Simple LTV (total revenue)
        customer_metrics['ltv_simple'] = customer_metrics['total_revenue']
        
        # Method 2: Predictive LTV (avg_order_value * avg_order_frequency * predicted_lifespan)
        # Using historical average lifespan as prediction
        avg_lifespan_months = customer_metrics['lifespan_days'].mean() / 30
        customer_metrics['ltv_predictive'] = customer_metrics['avg_order_value'] * \
                                            customer_metrics['avg_order_frequency'] * avg_lifespan_months
        
        # Merge with customer data
        customer_ltv = customer_metrics.merge(self.customers, on='customer_id')
        
        # LTV statistics by segment
        ltv_stats = customer_ltv.groupby('region').agg({
            'ltv_simple': ['mean', 'median', 'std'],
            'ltv_predictive': ['mean', 'median', 'std'],
            'customer_id': 'count'
        }).reset_index()
        
        ltv_stats.columns = ['region', 'ltv_simple_mean', 'ltv_simple_median', 'ltv_simple_std',
                            'ltv_predictive_mean', 'ltv_predictive_median', 'ltv_predictive_std', 'customer_count']
        
        return customer_ltv, {'ltv_stats': ltv_stats}
    
    def generate_eda_report(self, output_dir: str = "notebooks") -> Dict[str, Any]:
        """Generate comprehensive EDA report."""
        print("Generating Comprehensive EDA Report...")
        
        # Perform all analyses
        revenue_analysis = self.revenue_trends()
        category_analysis = self.top_categories_analysis()
        rfm_data, rfm_stats = self.rfm_analysis()
        cohort_pivot, cohort_stats = self.cohort_analysis()
        ltv_data, ltv_stats = self.customer_lifetime_value()
        
        # Calculate key metrics
        total_revenue = self.transactions['total_amount'].sum()
        total_orders = len(self.transactions)
        unique_customers = self.transactions['customer_id'].nunique()
        avg_order_value = total_revenue / total_orders
        churn_rate = self.customers['churned'].mean() if 'churned' in self.customers.columns else 0
        
        key_metrics = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'unique_customers': unique_customers,
            'avg_order_value': avg_order_value,
            'churn_rate': churn_rate,
            'revenue_per_customer': total_revenue / unique_customers,
            'orders_per_customer': total_orders / unique_customers
        }
        
        # Compile report
        report = {
            'key_metrics': key_metrics,
            'revenue_analysis': revenue_analysis,
            'category_analysis': category_analysis,
            'rfm_analysis': {'data': rfm_data, 'stats': rfm_stats},
            'cohort_analysis': {'pivot': cohort_pivot, 'stats': cohort_stats},
            'ltv_analysis': {'data': ltv_data, 'stats': ltv_stats}
        }
        
        # Save processed data for dashboard
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save key datasets
        rfm_data.to_csv(f"{output_dir}/rfm_analysis.csv", index=False)
        cohort_pivot.to_csv(f"{output_dir}/cohort_analysis.csv")
        ltv_data.to_csv(f"{output_dir}/ltv_analysis.csv", index=False)
        revenue_analysis['monthly'].to_csv(f"{output_dir}/monthly_revenue.csv", index=False)
        category_analysis['performance'].to_csv(f"{output_dir}/category_performance.csv", index=False)
        
        print(f"EDA report generated and saved to {output_dir}/")
        print(f"Key Metrics:")
        for metric, value in key_metrics.items():
            print(f"  {metric}: {value:,.2f}")
        
        return report

if __name__ == "__main__":
    # Load data and run EDA
    transactions_df = pd.read_csv("../data/transactions.csv")
    customers_df = pd.read_csv("../data/customers.csv")
    products_df = pd.read_csv("../data/products.csv")
    
    # Run EDA
    eda = EcommerceEDA(transactions_df, customers_df, products_df)
    report = eda.generate_eda_report("../notebooks")
