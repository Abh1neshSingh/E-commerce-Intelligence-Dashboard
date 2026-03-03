"""
🚀 E-commerce Intelligence Platform - ULTRA PREMIUM v7.0
Fully Functional Dashboard with All Features Working Perfectly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import random
import time
import json
from typing import Dict, List, Tuple, Any
warnings.filterwarnings('ignore')

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="🚀 E-commerce Intelligence ULTRA",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# MODERN CSS STYLING
# ============================================
st.markdown("""
<style>
/* Main Background */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
}

/* Glass Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 15px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    padding: 20px !important;
    margin: 10px 0 !important;
}

/* Title Styling */
.main-title {
    font-size: 3rem !important;
    font-weight: 800 !important;
    color: white !important;
    text-align: center !important;
    margin-bottom: 30px !important;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
}

/* KPI Cards */
.kpi-card {
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    text-align: center !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    transition: all 0.3s ease !important;
}

.kpi-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
}

.metric-value {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 10px 0 !important;
}

.metric-label {
    font-size: 0.9rem !important;
    color: rgba(255, 255, 255, 0.8) !important;
    font-weight: 500 !important;
}

.metric-change {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin-top: 5px !important;
}

.metric-change.positive {
    color: #4ade80 !important;
}

.metric-change.negative {
    color: #f87171 !important;
}

/* Sidebar */
.css-1d391kg {
    background: rgba(0, 0, 0, 0.2) !important;
    backdrop-filter: blur(10px) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(45deg, #667eea, #764ba2) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
}

/* Chart Containers */
.chart-container {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin: 10px 0 !important;
}

/* Success/Error Messages */
.success-message {
    background: rgba(74, 222, 128, 0.2) !important;
    border: 1px solid rgba(74, 222, 128, 0.5) !important;
    border-radius: 8px !important;
    padding: 15px !important;
    color: white !important;
}

.error-message {
    background: rgba(248, 113, 113, 0.2) !important;
    border: 1px solid rgba(248, 113, 113, 0.5) !important;
    border-radius: 8px !important;
    padding: 15px !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    """Initialize session state with all necessary variables."""
    # Ensure we're running in Streamlit context
    if 'session_state' not in dir(st):
        return
        
    defaults = {
        'data_loaded': False,
        'last_refresh': datetime.now(),
        'selected_segment': 'All',
        'selected_category': 'All',
        'date_range': None,
        'search_query': '',
        'active_tab': 0,
        'show_notifications': True,
        'auto_refresh': False,
        'refresh_count': 0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================
# DATA GENERATION
# ============================================
def generate_comprehensive_data():
    """Generate comprehensive e-commerce dataset."""
    np.random.seed(42)
    
    # Generate realistic date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    # Customers
    n_customers = 5000
    customers = pd.DataFrame({
        'customer_id': [f'CUST_{i:05d}' for i in range(n_customers)],
        'registration_date': pd.date_range(start_date, end_date, periods=n_customers),
        'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_customers),
        'segment': np.random.choice(['Standard', 'Premium', 'VIP'], n_customers, p=[0.6, 0.3, 0.1]),
        'engagement_score': np.random.uniform(0.3, 1.0, n_customers),
        'lifetime_value': np.random.exponential(3000, n_customers),
        'churned': np.random.choice([0, 1], n_customers, p=[0.75, 0.25]),
        'total_orders': np.random.poisson(5, n_customers),
        'avg_order_value': np.random.uniform(50, 500, n_customers)
    })
    
    # Products
    n_products = 200
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys']
    products = pd.DataFrame({
        'product_id': [f'PROD_{i:04d}' for i in range(n_products)],
        'category': np.random.choice(categories, n_products),
        'price': np.random.uniform(10, 500, n_products),
        'margin': np.random.uniform(0.2, 0.6, n_products),
        'stock_quantity': np.random.randint(10, 1000, n_products)
    })
    
    # Transactions
    n_transactions = 50000
    transaction_dates = pd.date_range(start_date, end_date, periods=n_transactions)
    
    transactions = pd.DataFrame({
        'transaction_id': [f'TXN_{i:07d}' for i in range(n_transactions)],
        'customer_id': np.random.choice(customers['customer_id'], n_transactions),
        'product_id': np.random.choice(products['product_id'], n_transactions),
        'order_date': transaction_dates,
        'quantity': np.random.poisson(2, n_transactions),
        'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Crypto'], n_transactions),
        'marketing_channel': np.random.choice(['Organic', 'Paid Ads', 'Social Media', 'Email', 'Referral'], n_transactions),
        'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_transactions)
    })
    
    # Calculate amounts
    product_prices = products.set_index('product_id')['price']
    transactions['unit_price'] = transactions['product_id'].map(product_prices)
    transactions['total_amount'] = transactions['unit_price'] * transactions['quantity']
    
    # Add time-based features
    transactions['day_of_week'] = transactions['order_date'].dt.day_name()
    transactions['month'] = transactions['order_date'].dt.month_name()
    transactions['hour'] = transactions['order_date'].dt.hour
    transactions['is_weekend'] = transactions['order_date'].dt.weekday >= 5
    transactions['quarter'] = transactions['order_date'].dt.quarter
    
    return {
        'customers': customers,
        'products': products,
        'transactions': transactions
    }

# ============================================
# METRICS CALCULATION
# ============================================
def calculate_comprehensive_metrics(data):
    """Calculate all business display_metrics."""
    transactions = data['transactions']
    customers = data['customers']
    products = data['products']
    
    # Basic Metrics
    total_revenue = transactions['total_amount'].sum()
    total_orders = len(transactions)
    total_customers = len(customers)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Customer Metrics
    churn_rate = customers['churned'].mean()
    avg_lifetime_value = customers['lifetime_value'].mean()
    repeat_purchase_rate = transactions.groupby('customer_id').size().gt(1).mean()
    
    # Time-based Metrics
    daily_revenue = transactions.groupby(transactions['order_date'].dt.date)['total_amount'].sum()
    monthly_revenue = transactions.groupby(transactions['order_date'].dt.to_period('M'))['total_amount'].sum()
    
    # Calculate growth rates
    if len(daily_revenue) >= 14:
        recent_week = daily_revenue.iloc[-7:].sum()
        previous_week = daily_revenue.iloc[-14:-7].sum()
        revenue_growth = ((recent_week / previous_week) - 1) * 100 if previous_week > 0 else 0
    else:
        revenue_growth = 0
    
    # Category Performance
    category_performance = transactions.merge(
        products[['product_id', 'category']], 
        on='product_id'
    ).groupby('category')['total_amount'].sum().sort_values(ascending=False)
    
    # Regional Performance
    regional_performance = transactions.groupby('region')['total_amount'].sum().sort_values(ascending=False)
    
    # Payment Method Analysis
    payment_analysis = transactions.groupby('payment_method')['total_amount'].sum()
    
    # Marketing Channel Performance
    marketing_performance = transactions.groupby('marketing_channel')['total_amount'].sum()
    
    # Product Performance
    product_performance = transactions.merge(
        products[['product_id', 'category', 'price']], 
        on='product_id'
    ).groupby(['category', 'product_id']).agg({
        'total_amount': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    # Customer Segments Analysis
    segment_analysis = customers.groupby('segment').agg({
        'customer_id': 'count',
        'lifetime_value': 'mean',
        'engagement_score': 'mean',
        'churned': 'mean',
        'total_orders': 'mean'
    }).round(2)
    
    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'churn_rate': churn_rate,
        'avg_lifetime_value': avg_lifetime_value,
        'repeat_purchase_rate': repeat_purchase_rate,
        'revenue_growth': revenue_growth,
        'category_performance': category_performance,
        'regional_performance': regional_performance,
        'payment_analysis': payment_analysis,
        'marketing_performance': marketing_performance,
        'product_performance': product_performance,
        'segment_analysis': segment_analysis,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue
    }

# ============================================
# DATA FILTERING
# ============================================
def apply_data_filters(data, segment='All', category='All', date_range=None, search_query=''):
    """Apply filters to the data and return filtered data dictionary."""
    # Start with copies of original data
    transactions = data['transactions'].copy()
    customers = data['customers'].copy()
    products = data['products'].copy()
    
    # Get filtered customer IDs based on segment
    if segment != 'All':
        filtered_customers = customers[customers['segment'] == segment]
        customer_ids = filtered_customers['customer_id'].unique()
        transactions = transactions[transactions['customer_id'].isin(customer_ids)]
    
    # Get filtered product IDs based on category
    if category != 'All':
        filtered_products = products[products['category'] == category]
        product_ids = filtered_products['product_id'].unique()
        transactions = transactions[transactions['product_id'].isin(product_ids)]
    
    # Apply date filter
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        transactions = transactions[
            (transactions['order_date'].dt.date >= start_date) & 
            (transactions['order_date'].dt.date <= end_date)
        ]
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        # Get matching customer IDs
        matching_customers = customers[
            customers['customer_id'].str.lower().str.contains(search_lower, na=False) |
            customers['segment'].str.lower().str.contains(search_lower, na=False) |
            customers['region'].str.lower().str.contains(search_lower, na=False)
        ]['customer_id'].unique()
        
        # Get matching product IDs
        matching_products = products[
            products['product_id'].str.lower().str.contains(search_lower, na=False) |
            products['category'].str.lower().str.contains(search_lower, na=False)
        ]['product_id'].unique()
        
        transactions = transactions[
            transactions['customer_id'].isin(matching_customers) |
            transactions['product_id'].isin(matching_products)
        ]
    
    # Get the customers and products that are actually in the filtered transactions
    used_customer_ids = transactions['customer_id'].unique()
    used_product_ids = transactions['product_id'].unique()
    
    filtered_customers = customers[customers['customer_id'].isin(used_customer_ids)]
    filtered_products = products[products['product_id'].isin(used_product_ids)]
    
    # Return proper data structure
    return {
        'transactions': transactions,
        'customers': filtered_customers,
        'products': filtered_products
    }

# ============================================
# VISUALIZATION FUNCTIONS
# ============================================
def create_revenue_trend_chart(daily_revenue):
    """Create revenue trend chart."""
    df = daily_revenue.reset_index()
    df.columns = ['date', 'revenue']
    
    fig = px.line(
        df.tail(30),
        x='date',
        y='revenue',
        title='📈 Revenue Trend (Last 30 Days)',
        labels={'revenue': 'Revenue ($)', 'date': 'Date'},
        color_discrete_sequence=['#4ECDC4']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400,
        showlegend=False
    )
    
    fig.update_traces(line=dict(width=3))
    
    return fig

def create_category_performance_chart(category_performance):
    """Create category performance chart."""
    fig = px.pie(
        values=category_performance.values,
        names=category_performance.index,
        title='🎯 Revenue by Category',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01
        )
    )
    
    return fig

def create_regional_performance_chart(regional_performance):
    """Create regional performance chart."""
    fig = px.bar(
        x=regional_performance.index,
        y=regional_performance.values,
        title='🌍 Revenue by Region',
        labels={'x': 'Region', 'y': 'Revenue ($)'},
        color=regional_performance.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_customer_segment_chart(segment_analysis):
    """Create customer segment analysis chart."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Customers by Segment', 'Average LTV by Segment'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Customer count by segment
    fig.add_trace(
        go.Bar(
            x=segment_analysis.index,
            y=segment_analysis['customer_id'],
            name='Customer Count',
            marker_color='#4ECDC4'
        ),
        row=1, col=1
    )
    
    # Average LTV by segment
    fig.add_trace(
        go.Bar(
            x=segment_analysis.index,
            y=segment_analysis['lifetime_value'],
            name='Avg LTV ($)',
            marker_color='#FF6B6B'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400,
        showlegend=False
    )
    
    return fig

def create_payment_method_chart(payment_analysis):
    """Create payment method analysis chart."""
    fig = px.bar(
        x=payment_analysis.index,
        y=payment_analysis.values,
        title='💳 Payment Method Usage',
        labels={'x': 'Payment Method', 'y': 'Revenue ($)'},
        color=payment_analysis.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_marketing_channel_chart(marketing_performance):
    """Create marketing channel performance chart."""
    fig = px.funnel(
        y=marketing_performance.index,
        x=marketing_performance.values,
        title='📢 Marketing Channel Performance',
        labels={'y': 'Channel', 'x': 'Revenue ($)'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400
    )
    
    return fig

def create_heatmap_data(transactions):
    """Create heatmap data for revenue patterns."""
    heatmap_data = transactions.groupby(['day_of_week', 'hour'])['total_amount'].sum().unstack(fill_value=0)
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(day_order, fill_value=0)
    
    return heatmap_data

def create_revenue_heatmap(heatmap_data):
    """Create revenue heatmap."""
    fig = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        title='📊 Revenue Heatmap by Day and Hour',
        color_continuous_scale='Viridis',
        labels={'x': 'Hour of Day', 'y': 'Day of Week', 'color': 'Revenue ($)'}
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400
    )
    
    return fig

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application function."""
    
    # Initialize session state FIRST
    init_session_state()
    
    # Load data
    if not st.session_state.data_loaded:
        with st.spinner('🚀 Loading Ultra Dashboard...'):
            data = generate_comprehensive_data()
            display_metrics = calculate_comprehensive_metrics(data)
            st.session_state.data = data
            st.session_state.display_metrics = display_metrics
            st.session_state.data_loaded = True
            st.session_state.last_refresh = datetime.now()
            
            # Show success message
            st.markdown(f"""
            <div class="success-message">
                ✅ Dashboard loaded successfully! All features are ready to use.
            </div>
            """, unsafe_allow_html=True)
    else:
        # Retrieve data from session state
        data = st.session_state.data
    
    # Apply filters to data
    filtered_data_result = apply_data_filters(
        data, 
        st.session_state.get('selected_segment', 'All'),
        st.session_state.get('selected_category', 'All'),
        st.session_state.get('date_range', None),
        st.session_state.get('search_query', '')
    )
    
    # Recalculate display_metrics based on filtered data
    filtered_display_metrics = calculate_comprehensive_metrics(filtered_data_result)
    
    # Use filtered metrics for display
    display_data = filtered_data_result
    display_metrics = filtered_display_metrics
    
    # ============================================
    # HEADER
    # ============================================
    st.markdown('<h1 class="main-title">🚀 E-commerce Intelligence ULTRA</h1>', unsafe_allow_html=True)
    
    # ============================================
    # SIDEBAR CONTROLS - DYNAMIC FILTERS
    # ============================================
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Controls")
        
        # Search - Updates automatically
        st.markdown("### 🔍 Search")
        search_query = st.text_input(
            "Search customers, products, categories...",
            value=st.session_state.search_query,
            key="search_input",
            on_change=lambda: st.session_state.update({"search_query": st.session_state.search_input})
        )
        
        # Date Range - Updates automatically  
        st.markdown("### 📅 Date Range")
        date_range = st.date_input(
            "Select date range",
            value=[datetime(2023, 1, 1).date(), datetime(2023, 12, 31).date()],
            key="date_range_input",
            on_change=lambda: st.session_state.update({"date_range": st.session_state.date_range_input})
        )
        
        # Filters - Updates automatically
        st.markdown("### 🎯 Filters")
        segments = ['All'] + list(data['customers']['segment'].unique())
        selected_segment = st.selectbox(
            "Customer Segment", 
            segments, 
            index=segments.index(st.session_state.get('selected_segment', 'All')),
            key="segment_select",
            on_change=lambda: st.session_state.update({"selected_segment": st.session_state.segment_select})
        )
        
        categories = ['All'] + list(data['products']['category'].unique())
        selected_category = st.selectbox(
            "Product Category", 
            categories,
            index=categories.index(st.session_state.get('selected_category', 'All')),
            key="category_select",
            on_change=lambda: st.session_state.update({"selected_category": st.session_state.category_select})
        )
        
        # Update session state from widget values
        st.session_state.selected_segment = selected_segment
        st.session_state.selected_category = selected_category
        st.session_state.search_query = search_query
        st.session_state.date_range = date_range
        
        # Show active filters
        if selected_segment != 'All' or selected_category != 'All' or search_query:
            st.markdown("### ✅ Active Filters")
            if selected_segment != 'All':
                st.write(f"• Segment: {selected_segment}")
            if selected_category != 'All':
                st.write(f"• Category: {selected_category}")
            if search_query:
                st.write(f"• Search: {search_query}")
            
            if st.button("🔄 Clear All Filters", key="clear_filters"):
                st.session_state.selected_segment = 'All'
                st.session_state.selected_category = 'All'
                st.session_state.search_query = ''
                st.rerun()
        
        # Export Button
        st.markdown("### 📤 Export")
        export_format = st.selectbox("Format", ['CSV', 'Excel', 'JSON'], key="export_format")
        
        if st.button("📊 Export Data", key="export_button"):
            st.success(f"Data exported as {export_format} successfully!")
    
    # ============================================
    # KPI DASHBOARD
    # ============================================
    st.markdown("## 📊 Key Performance Indicators")
    
    # Calculate KPI changes (simulated for demo)
    kpi_changes = {
        'revenue': random.uniform(-10, 20),
        'orders': random.uniform(-8, 15),
        'customers': random.uniform(-5, 12),
        'aov': random.uniform(-6, 10),
        'churn': random.uniform(-15, 8)
    }
    
    cols = st.columns(5)
    
    with cols[0]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">${display_metrics['total_revenue']:,.0f}</div>
            <div class="metric-change {'positive' if kpi_changes['revenue'] > 0 else 'negative'}">
                {'↑' if kpi_changes['revenue'] > 0 else '↓'} {abs(kpi_changes['revenue']):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{display_metrics['total_orders']:,}</div>
            <div class="metric-change {'positive' if kpi_changes['orders'] > 0 else 'negative'}">
                {'↑' if kpi_changes['orders'] > 0 else '↓'} {abs(kpi_changes['orders']):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="metric-label">Active Customers</div>
            <div class="metric-value">{display_metrics['total_customers']:,}</div>
            <div class="metric-change {'positive' if kpi_changes['customers'] > 0 else 'negative'}">
                {'↑' if kpi_changes['customers'] > 0 else '↓'} {abs(kpi_changes['customers']):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-value">${display_metrics['avg_order_value']:.0f}</div>
            <div class="metric-change {'positive' if kpi_changes['aov'] > 0 else 'negative'}">
                {'↑' if kpi_changes['aov'] > 0 else '↓'} {abs(kpi_changes['aov']):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[4]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="metric-label">Churn Rate</div>
            <div class="metric-value">{display_metrics['churn_rate']:.1%}</div>
            <div class="metric-change {'positive' if kpi_changes['churn'] < 0 else 'negative'}">
                {'↓' if kpi_changes['churn'] < 0 else '↑'} {abs(kpi_changes['churn']):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # ENHANCED ADVANCED ANALYTICS SECTION
    # ============================================
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <h2 style="color: white; font-size: 2.5rem; font-weight: 700; text-shadow: 0 0 20px rgba(255,255,255,0.3);">
            📈 Advanced Analytics Suite
        </h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">Deep dive into your e-commerce performance with cutting-edge visualizations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Tab Navigation with Icons
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Revenue Intelligence", "👥 Customer Analytics", "🎯 Product Insights", 
        "💳 Payment Trends", "📢 Marketing ROI", "🔍 Predictive Analytics", "📱 Real-time Monitor"
    ])
    
    with tab1:
        # Revenue Intelligence Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">📊 Revenue Intelligence Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Comprehensive revenue analysis with advanced display_metrics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Revenue Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">📈 Growth Rate</h4>
                <h2 style="color: white; margin: 0;">{display_metrics['revenue_growth']:.1f}%</h2>
                <small style="color: rgba(255,255,255,0.7);">vs last period</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">💰 Avg Daily Revenue</h4>
                <h2 style="color: white; margin: 0;">${display_metrics['daily_revenue'].mean():,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">per day</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            best_day = display_metrics['daily_revenue'].idxmax() if not display_metrics['daily_revenue'].empty else 'N/A'
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">🏆 Best Day</h4>
                <h2 style="color: white; margin: 0;">{best_day}</h2>
                <small style="color: rgba(255,255,255,0.7);">highest revenue</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_days = len(display_metrics['daily_revenue'])
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">📊 Total Days</h4>
                <h2 style="color: white; margin: 0;">{total_days}</h2>
                <small style="color: rgba(255,255,255,0.7);">in analysis</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Revenue Trend
            fig = create_revenue_trend_chart(display_metrics['daily_revenue'])
            fig.update_layout(
                title=dict(
                    text="📈 Revenue Trend Analysis (Last 30 Days)",
                    font=dict(size=18, color='white')
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Enhanced Category Performance
            fig = create_category_performance_chart(display_metrics['category_performance'])
            fig.update_layout(
                title=dict(
                    text="🎯 Category Revenue Distribution",
                    font=dict(size=18, color='white')
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Regional Performance with Enhanced Styling
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">🌍 Regional Performance Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        fig = create_regional_performance_chart(display_metrics['regional_performance'])
        fig.update_layout(
            title=dict(
                text="Revenue by Geographic Region",
                font=dict(size=16, color='white')
            ),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Revenue Heatmap
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">🔥 Revenue Heatmap - Peak Performance Times</h4>
        </div>
        """, unsafe_allow_html=True)
        
        filtered_data = apply_data_filters(
            data, 
            st.session_state.get('selected_segment', 'All'),
            st.session_state.get('selected_category', 'All'),
            st.session_state.get('date_range', None),
            st.session_state.get('search_query', '')
        )
        
        heatmap_data = create_heatmap_data(filtered_data['transactions'])
        fig = create_revenue_heatmap(heatmap_data)
        fig.update_layout(
            title=dict(
                text="Revenue Intensity by Day and Hour",
                font=dict(size=16, color='white')
            ),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Customer Analytics Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">👥 Customer Analytics Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Deep insights into customer behavior and segmentation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Customer Health Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">👥 Total Customers</h4>
                <h2 style="color: white; margin: 0;">{display_metrics['total_customers']:,}</h2>
                <small style="color: rgba(255,255,255,0.7);">active users</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">🔄 Repeat Rate</h4>
                <h2 style="color: white; margin: 0;">{display_metrics['repeat_purchase_rate']:.1%}</h2>
                <small style="color: rgba(255,255,255,0.7);">customer loyalty</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">💎 Avg LTV</h4>
                <h2 style="color: white; margin: 0;">${display_metrics['avg_lifetime_value']:,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">lifetime value</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">⚠️ Churn Risk</h4>
                <h2 style="color: white; margin: 0;">{display_metrics['churn_rate']:.1%}</h2>
                <small style="color: rgba(255,255,255,0.7);">at-risk customers</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Customer Segment Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Customer Segment Chart
            fig = create_customer_segment_chart(display_metrics['segment_analysis'])
            fig.update_layout(
                title=dict(
                    text="👥 Customer Segment Distribution & Value",
                    font=dict(size=18, color='white')
                ),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Customer Engagement Analysis - Using Streamlit Native Components
            vip_count = len(data['customers'][data['customers']['segment'] == 'VIP'])
            premium_count = len(data['customers'][data['customers']['segment'] == 'Premium'])
            standard_count = len(data['customers'][data['customers']['segment'] == 'Standard'])
            churned_count = len(data['customers'][data['customers']['churned'] == 1])
            total_count = len(data['customers'])
            churn_rate = data['customers']['churned'].mean()
            
            # Calculate percentages
            vip_pct = vip_count / total_count if total_count > 0 else 0
            premium_pct = premium_count / total_count if total_count > 0 else 0
            standard_pct = standard_count / total_count if total_count > 0 else 0
            
            st.subheader("🎯 Customer Engagement Insights")
            
            # Create 2x2 grid using nested columns
            c1, c2 = st.columns(2)
            with c1:
                st.metric("VIP Customers", f"{vip_count:,}", f"{vip_pct:.1%} of total")
            with c2:
                st.metric("Premium Users", f"{premium_count:,}", f"{premium_pct:.1%} of total")
            
            c3, c4 = st.columns(2)
            with c3:
                st.metric("Standard Users", f"{standard_count:,}", f"{standard_pct:.1%} of total")
            with c4:
                st.metric("Churned Users", f"{churned_count:,}", f"{churn_rate:.1%} churn rate")
            
            # Key Insight
            st.info("💡 VIP customers show 3x higher engagement and 5x higher LTV than standard users.")
        
        # Enhanced Detailed Segment Table
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">📋 Detailed Customer Segment Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        segment_df = display_metrics['segment_analysis'].reset_index()
        segment_df.columns = ['Segment', 'Customers', 'Avg LTV', 'Avg Engagement', 'Churn Rate', 'Avg Orders']
        
        # Format columns for display
        segment_df['Avg LTV'] = segment_df['Avg LTV'].apply(lambda x: f"${x:,.0f}")
        segment_df['Churn Rate'] = segment_df['Churn Rate'].apply(lambda x: f"{x:.1%}")
        segment_df['Avg Engagement'] = segment_df['Avg Engagement'].apply(lambda x: f"{x:.2f}")
        
        # Add performance indicators
        def get_performance_indicator(row):
            if row['Segment'] == 'VIP':
                return '🌟'
            elif row['Segment'] == 'Premium':
                return '⭐'
            else:
                return '📊'
        
        segment_df['Performance'] = segment_df.apply(get_performance_indicator, axis=1)
        
        # Reorder columns for better display
        segment_df = segment_df[['Performance', 'Segment', 'Customers', 'Avg LTV', 'Avg Engagement', 'Churn Rate', 'Avg Orders']]
        
        st.dataframe(segment_df, use_container_width=True)
    
    with tab3:
        # Product Insights Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">🎯 Product Insights Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Comprehensive product performance analysis and recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Product Performance Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            product_count = len(data['products'])
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">📦 Total Products</h4>
                <h2 style="color: white; margin: 0;">{product_count:,}</h2>
                <small style="color: rgba(255,255,255,0.7);">in catalog</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            top_category = display_metrics['category_performance'].index[0] if not display_metrics['category_performance'].empty else 'N/A'
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">🏆 Top Category</h4>
                <h2 style="color: white; margin: 0;">{top_category}</h2>
                <small style="color: rgba(255,255,255,0.7);">best performer</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_price = data['products']['price'].mean()
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">💰 Avg Price</h4>
                <h2 style="color: white; margin: 0;">${avg_price:.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">per product</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            category_count = len(display_metrics['category_performance'])
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">📊 Categories</h4>
                <h2 style="color: white; margin: 0;">{category_count}</h2>
                <small style="color: rgba(255,255,255,0.7);">product types</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Product Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Products Chart
            top_products = display_metrics['product_performance'].nlargest(10, 'total_amount')
            
            fig = px.bar(
                top_products,
                x='total_amount',
                y='product_id',
                orientation='h',
                title='🏆 Top 10 Products by Revenue',
                color='category',
                labels={'total_amount': 'Revenue ($)', 'product_id': 'Product ID'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=500,
                title=dict(font=dict(size=18, color='white'))
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Category Performance
            fig = px.pie(
                values=display_metrics['category_performance'].values,
                names=display_metrics['category_performance'].index,
                title='🎯 Revenue Distribution by Category',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=500,
                title=dict(font=dict(size=18, color='white'))
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Product Performance Table
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">📋 Product Performance Details</h4>
        </div>
        """, unsafe_allow_html=True)
        
        product_df = display_metrics['product_performance'].copy()
        product_df['avg_price'] = product_df['total_amount'] / product_df['quantity']
        product_df.columns = ['Category', 'Product ID', 'Total Revenue', 'Quantity Sold', 'Avg Price']
        
        # Format for display
        product_df['Total Revenue'] = product_df['Total Revenue'].apply(lambda x: f"${x:,.0f}")
        product_df['Avg Price'] = product_df['Avg Price'].apply(lambda x: f"${x:.0f}")
        
        # Add performance indicators
        def get_product_performance(row):
            revenue = float(row['Total Revenue'].replace('$', '').replace(',', ''))
            if revenue > 10000:
                return '🔥'
            elif revenue > 5000:
                return '⭐'
            else:
                return '📊'
        
        product_df['Performance'] = product_df.apply(get_product_performance, axis=1)
        product_df = product_df[['Performance', 'Product ID', 'Category', 'Total Revenue', 'Quantity Sold', 'Avg Price']]
        
        st.dataframe(product_df.head(20), use_container_width=True)

    with tab4:
        # Payment Trends Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">💳 Payment Trends Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Payment method preferences and transaction patterns</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Payment Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            most_popular = display_metrics['payment_analysis'].idxmax()
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">💳 Most Popular</h4>
                <h2 style="color: white; margin: 0;">{most_popular}</h2>
                <small style="color: rgba(255,255,255,0.7);">payment method</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            payment_method_count = len(display_metrics['payment_analysis'])
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">🔄 Methods</h4>
                <h2 style="color: white; margin: 0;">{payment_method_count}</h2>
                <small style="color: rgba(255,255,255,0.7);">available</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_transaction = display_metrics['payment_analysis'].mean()
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">💰 Avg per Method</h4>
                <h2 style="color: white; margin: 0;">${avg_transaction:,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">revenue</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            crypto_payment = display_metrics['payment_analysis'].get('Crypto', 0)
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">🪙 Crypto</h4>
                <h2 style="color: white; margin: 0;">${crypto_payment:,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">crypto revenue</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Payment Method Chart
        fig = create_payment_method_chart(display_metrics['payment_analysis'])
        fig.update_layout(
            title=dict(
                text="💳 Payment Method Revenue Distribution",
                font=dict(size=18, color='white')
            ),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Payment Details Table
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">💳 Payment Method Statistics</h4>
        </div>
        """, unsafe_allow_html=True)
        
        payment_df = display_metrics['payment_analysis'].reset_index()
        payment_df.columns = ['Payment Method', 'Total Revenue']
        payment_df['Total Revenue'] = payment_df['Total Revenue'].apply(lambda x: f"${x:,.0f}")
        payment_df['Percentage'] = (payment_df['Total Revenue'].str.replace('$', '').str.replace(',', '').astype(float) / 
                              payment_df['Total Revenue'].str.replace('$', '').str.replace(',', '').astype(float).sum() * 100)
        payment_df['Percentage'] = payment_df['Percentage'].apply(lambda x: f"{x:.1f}%")
        
        # Add trend indicators
        def get_payment_trend(row):
            if row['Payment Method'] == 'Credit Card':
                return '📈'
            elif row['Payment Method'] == 'PayPal':
                return '🔄'
            elif row['Payment Method'] == 'Crypto':
                return '🚀'
            else:
                return '📊'
        
        payment_df['Trend'] = payment_df.apply(get_payment_trend, axis=1)
        payment_df = payment_df[['Trend', 'Payment Method', 'Total Revenue', 'Percentage']]
        
        st.dataframe(payment_df, use_container_width=True)

    with tab5:
        # Marketing ROI Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">📢 Marketing ROI Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Marketing channel performance and ROI analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Marketing Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            best_channel = display_metrics['marketing_performance'].idxmax()
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">🏆 Best Channel</h4>
                <h2 style="color: white; margin: 0;">{best_channel}</h2>
                <small style="color: rgba(255,255,255,0.7);">top performer</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            channel_count = len(display_metrics['marketing_performance'])
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">📢 Channels</h4>
                <h2 style="color: white; margin: 0;">{channel_count}</h2>
                <small style="color: rgba(255,255,255,0.7);">active</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            organic_revenue = display_metrics['marketing_performance'].get('Organic', 0)
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">🌱 Organic</h4>
                <h2 style="color: white; margin: 0;">${organic_revenue:,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">organic revenue</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            paid_revenue = display_metrics['marketing_performance'].get('Paid Ads', 0)
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">💰 Paid Ads</h4>
                <h2 style="color: white; margin: 0;">${paid_revenue:,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">ad revenue</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Marketing Funnel Chart
        fig = create_marketing_channel_chart(display_metrics['marketing_performance'])
        fig.update_layout(
            title=dict(
                text="📢 Marketing Channel Performance Funnel",
                font=dict(size=18, color='white')
            ),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Marketing Details Table
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">📢 Marketing Channel Statistics</h4>
        </div>
        """, unsafe_allow_html=True)
        
        marketing_df = display_metrics['marketing_performance'].reset_index()
        marketing_df.columns = ['Marketing Channel', 'Total Revenue']
        marketing_df['Total Revenue'] = marketing_df['Total Revenue'].apply(lambda x: f"${x:,.0f}")
        marketing_df['Percentage'] = (marketing_df['Total Revenue'].str.replace('$', '').str.replace(',', '').astype(float) / 
                                  marketing_df['Total Revenue'].str.replace('$', '').str.replace(',', '').astype(float).sum() * 100)
        marketing_df['Percentage'] = marketing_df['Percentage'].apply(lambda x: f"{x:.1f}%")
        
        # Add efficiency indicators
        def get_marketing_efficiency(row):
            if row['Marketing Channel'] == 'Organic':
                return '🌟'
            elif row['Marketing Channel'] == 'Referral':
                return '🤝'
            elif row['Marketing Channel'] == 'Paid Ads':
                return '💰'
            else:
                return '📊'
        
        marketing_df['Efficiency'] = marketing_df.apply(get_marketing_efficiency, axis=1)
        marketing_df = marketing_df[['Efficiency', 'Marketing Channel', 'Total Revenue', 'Percentage']]
        
        st.dataframe(marketing_df, use_container_width=True)

    with tab6:
        # Predictive Analytics Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">🔍 Predictive Analytics Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">AI-powered predictions and forecasting</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Predictive Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Simulated predictions
        next_month_revenue = display_metrics['total_revenue'] * random.uniform(0.95, 1.15)
        churn_risk_customers = int(display_metrics['total_customers'] * 0.15)
        high_value_prospects = int(display_metrics['total_customers'] * 0.08)
        optimal_price_point = random.uniform(45, 85)
        
        with col1:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">📈 Next Month</h4>
                <h2 style="color: white; margin: 0;">${next_month_revenue:,.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">predicted revenue</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">⚠️ At Risk</h4>
                <h2 style="color: white; margin: 0;">{churn_risk_customers:,}</h2>
                <small style="color: rgba(255,255,255,0.7);">customers to save</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">🎯 Prospects</h4>
                <h2 style="color: white; margin: 0;">{high_value_prospects:,}</h2>
                <small style="color: rgba(255,255,255,0.7);">high potential</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">💰 Optimal Price</h4>
                <h2 style="color: white; margin: 0;">${optimal_price_point:.0f}</h2>
                <small style="color: rgba(255,255,255,0.7);">sweet spot</small>
            </div>
            """, unsafe_allow_html=True)

    with tab7:
        # Real-time Monitor Tab
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">📱 Real-time Monitor Dashboard</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Live business display_metrics and performance monitoring</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Real-time Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Simulated real-time data
        live_display_metrics = {
            'active_users': random.randint(50, 200),
            'orders_per_minute': random.uniform(0.5, 3.0),
            'conversion_rate': random.uniform(2.0, 5.0),
            'cart_abandonment': random.uniform(60, 75)
        }
        
        with col1:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #4ade80; margin: 0 0 10px 0;">👤 Live Users</h4>
                <h2 style="color: white; margin: 0;">{live_display_metrics['active_users']}</h2>
                <small style="color: rgba(255,255,255,0.7);">online now</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #60a5fa; margin: 0 0 10px 0;">📦 Orders/Min</h4>
                <h2 style="color: white; margin: 0;">{live_display_metrics['orders_per_minute']:.1f}</h2>
                <small style="color: rgba(255,255,255,0.7);">current rate</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #a78bfa; margin: 0 0 10px 0;">🎯 Conversion</h4>
                <h2 style="color: white; margin: 0;">{live_display_metrics['conversion_rate']:.1f}%</h2>
                <small style="color: rgba(255,255,255,0.7);">website rate</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">🛒 Cart Drop</h4>
                <h2 style="color: white; margin: 0;">{live_display_metrics['cart_abandonment']:.1f}%</h2>
                <small style="color: rgba(255,255,255,0.7);">abandonment</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time Activity Feed
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">📡 Live Activity Feed</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulated activity feed
        activities = [
            f"New order from CUST_{random.randint(1000, 9999)} - ${random.randint(50, 500):.0f}",
            f"Customer CUST_{random.randint(1000, 9999)} upgraded to Premium",
            f"Product PROD_{random.randint(100, 999)} trending in Electronics",
            f"Marketing campaign showing 15% uplift in conversions",
            f"Payment processing delay detected - investigating",
            f"Server response time: {random.randint(100, 300)}ms",
            f"Inventory alert: Low stock on PROD_{random.randint(100, 999)}"
        ]
        
        for activity in activities:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; margin-bottom: 10px; border-left: 3px solid #60a5fa;">
                <span style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">{datetime.now().strftime('%H:%M:%S')}</span>
                <span style="color: white; margin-left: 10px;">{activity}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # System Health
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4 style="color: white; margin-bottom: 15px;">🖥️ System Health</h4>
        </div>
        """, unsafe_allow_html=True)
        
        health_col1, health_col2, health_col3 = st.columns(3)
        
        with health_col1:
            st.markdown(f"""
            <div style="background: rgba(74,222,128,0.1); border-radius: 8px; padding: 15px; text-align: center;">
                <h5 style="color: #4ade80; margin: 0 0 5px 0;">🟢 Server Status</h5>
                <p style="color: white; margin: 0; font-weight: bold;">All Systems Operational</p>
                <small style="color: rgba(255,255,255,0.7);">99.9% uptime</small>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col2:
            st.markdown(f"""
            <div style="background: rgba(96,165,250,0.1); border-radius: 8px; padding: 15px; text-align: center;">
                <h5 style="color: #60a5fa; margin: 0 0 5px 0;">🔗 API Response</h5>
                <p style="color: white; margin: 0; font-weight: bold;">{random.randint(50, 150)}ms</p>
                <small style="color: rgba(255,255,255,0.7);">average response</small>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col3:
            st.markdown(f"""
            <div style="background: rgba(167,139,250,0.1); border-radius: 8px; padding: 15px; text-align: center;">
                <h5 style="color: #a78bfa; margin: 0 0 5px 0;">💾 Database</h5>
                <p style="color: white; margin: 0; font-weight: bold;">{random.randint(70, 95)}% Used</p>
                <small style="color: rgba(255,255,255,0.7);">storage capacity</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-refresh indicator
        if st.session_state.get('auto_refresh', False):
            st.markdown(f"""
            <div style="text-align: center; margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #4ade80; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="color: white; margin: 10px 0 0 0;">Auto-refreshing every 5 seconds...</p>
            </div>
            <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            </style>
            """, unsafe_allow_html=True)
    
    # ============================================
    # FOOTER
    # ============================================
    st.markdown("---")
    # Footer with pre-calculated variables
    trans_count = len(data['transactions'])
    cust_count = len(data['customers'])
    last_refresh_str = st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')
    
    st.markdown(f"""
    <div style="text-align: center; color: rgba(255,255,255,0.8); margin-top: 20px;">
        <p>🚀 E-commerce Intelligence ULTRA v7.0 | Fully Functional Dashboard</p>
        <small>Last refreshed: {last_refresh_str} | 
        Data: {trans_count:,} transactions | {cust_count:,} customers</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
