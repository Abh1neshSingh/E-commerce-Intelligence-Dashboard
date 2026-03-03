"""
Sales Forecasting Model
Time series forecasting using Prophet for e-commerce sales prediction.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    print("Prophet not available. Using alternative forecasting method.")
    PROPHET_AVAILABLE = False

class SalesForecastingModel:
    """Sales forecasting using Prophet or alternative time series methods."""
    
    def __init__(self, transactions_df: pd.DataFrame):
        """
        Initialize sales forecasting model.
        
        Args:
            transactions_df: Transaction data
        """
        self.transactions = transactions_df.copy()
        self.model = None
        self.forecast = None
        self.daily_sales = None
        
        # Convert date columns
        self.transactions['order_date'] = pd.to_datetime(self.transactions['order_date'])
        
    def prepare_daily_sales_data(self) -> pd.DataFrame:
        """Aggregate transaction data to daily sales."""
        print("Preparing daily sales data...")
        
        # Aggregate sales by date
        daily_sales = self.transactions.groupby('order_date').agg({
            'total_amount': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        daily_sales.columns = ['ds', 'y', 'orders', 'unique_customers', 'total_quantity']
        
        # Add additional features
        daily_sales['avg_order_value'] = daily_sales['y'] / daily_sales['orders']
        daily_sales['avg_quantity_per_order'] = daily_sales['total_quantity'] / daily_sales['orders']
        
        # Add time-based features
        daily_sales['day_of_week'] = daily_sales['ds'].dt.dayofweek
        daily_sales['month'] = daily_sales['ds'].dt.month
        daily_sales['quarter'] = daily_sales['ds'].dt.quarter
        daily_sales['year'] = daily_sales['ds'].dt.year
        daily_sales['is_weekend'] = (daily_sales['day_of_week'] >= 5).astype(int)
        
        # Sort by date
        daily_sales = daily_sales.sort_values('ds').reset_index(drop=True)
        
        self.daily_sales = daily_sales
        return daily_sales
    
    def add_prophet_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Prophet-specific features for better forecasting."""
        # Add holiday effects (simplified - major holidays)
        holidays = df.copy()
        
        # Define major holidays (simplified for demo)
        holiday_dates = [
            ('2022-12-25', 'Christmas'),
            ('2023-12-25', 'Christmas'),
            ('2022-01-01', 'New Year'),
            ('2023-01-01', 'New Year'),
            ('2022-07-04', 'Independence Day'),
            ('2023-07-04', 'Independence Day'),
            ('2022-11-24', 'Thanksgiving'),
            ('2023-11-23', 'Thanksgiving'),
            ('2022-02-14', 'Valentine\'s Day'),
            ('2023-02-14', 'Valentine\'s Day'),
            ('2022-10-31', 'Halloween'),
            ('2023-10-31', 'Halloween'),
            ('2022-11-25', 'Black Friday'),
            ('2023-11-24', 'Black Friday'),
            ('2022-12-24', 'Christmas Eve'),
            ('2023-12-24', 'Christmas Eve')
        ]
        
        holiday_df = pd.DataFrame(holiday_dates, columns=['ds', 'holiday'])
        holiday_df['ds'] = pd.to_datetime(holiday_df['ds'])
        
        return holiday_df
    
    def train_prophet_model(self, daily_sales: pd.DataFrame, forecast_periods: int = 90) -> Dict[str, Any]:
        """Train Prophet model for sales forecasting."""
        if not PROPHET_AVAILABLE:
            return self.train_alternative_model(daily_sales, forecast_periods)
        
        print("Training Prophet model...")
        
        # Prepare data for Prophet
        prophet_data = daily_sales[['ds', 'y']].copy()
        
        # Add holidays
        holidays = self.add_prophet_features(daily_sales)
        
        # Initialize and train Prophet model
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            holidays=holidays,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            holidays_prior_scale=10,
            mcmc_samples=0,
            interval_width=0.8,
            uncertainty_samples=1000
        )
        
        # Add custom seasonality for monthly patterns
        self.model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Fit the model
        self.model.fit(prophet_data)
        
        # Create future dataframe for forecasting
        future = self.model.make_future_dataframe(periods=forecast_periods)
        
        # Generate forecast
        self.forecast = self.model.predict(future)
        
        # Calculate model performance metrics
        # Use last 30 days as validation set
        validation_days = 30
        train_data = prophet_data[:-validation_days]
        val_data = prophet_data[-validation_days:]
        
        # Train model on training data
        val_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10
        )
        val_model.fit(train_data)
        
        # Predict on validation period
        val_future = val_model.make_future_dataframe(periods=validation_days)
        val_forecast = val_model.predict(val_future)
        
        # Calculate validation metrics
        val_predictions = val_forecast.iloc[-validation_days:]['yhat'].values
        val_actual = val_data['y'].values
        
        # Calculate metrics
        mae = np.mean(np.abs(val_actual - val_predictions))
        mape = np.mean(np.abs((val_actual - val_predictions) / val_actual)) * 100
        rmse = np.sqrt(np.mean((val_actual - val_predictions) ** 2))
        
        metrics = {
            'mae': mae,
            'mape': mape,
            'rmse': rmse,
            'validation_days': validation_days
        }
        
        print(f"Model trained successfully. Validation metrics:")
        print(f"  MAE: ${mae:,.2f}")
        print(f"  MAPE: {mape:.2f}%")
        print(f"  RMSE: ${rmse:,.2f}")
        
        return {
            'model': self.model,
            'forecast': self.forecast,
            'metrics': metrics,
            'validation_predictions': val_predictions,
            'validation_actual': val_actual
        }
    
    def train_alternative_model(self, daily_sales: pd.DataFrame, forecast_periods: int = 90) -> Dict[str, Any]:
        """Alternative forecasting method using moving averages and trend analysis."""
        print("Training alternative forecasting model...")
        
        # Simple exponential smoothing with trend
        data = daily_sales.copy()
        
        # Calculate moving averages
        data['ma_7'] = data['y'].rolling(window=7).mean()
        data['ma_30'] = data['y'].rolling(window=30).mean()
        
        # Calculate trend
        data['trend'] = data['y'].rolling(window=30).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        
        # Seasonal decomposition (simplified)
        data['day_of_week'] = data['ds'].dt.dayofweek
        seasonal_pattern = data.groupby('day_of_week')['y'].mean()
        data['seasonal_factor'] = data['day_of_week'].map(seasonal_pattern)
        data['seasonal_factor'] = data['seasonal_factor'] / data['seasonal_factor'].mean()
        
        # Generate forecast
        last_date = data['ds'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_periods, freq='D')
        
        forecast_data = []
        for i, date in enumerate(forecast_dates):
            # Use last available trend and seasonal patterns
            last_trend = data['trend'].iloc[-1] if not pd.isna(data['trend'].iloc[-1]) else 0
            last_ma = data['ma_30'].iloc[-1] if not pd.isna(data['ma_30'].iloc[-1]) else data['y'].mean()
            
            # Day of week for seasonal adjustment
            dow = date.dayofweek
            seasonal_adj = seasonal_pattern[dow] / seasonal_pattern.mean() if dow in seasonal_pattern.index else 1.0
            
            # Forecast calculation
            forecast_value = (last_ma + last_trend * (i + 1)) * seasonal_adj
            
            forecast_data.append({
                'ds': date,
                'yhat': forecast_value,
                'yhat_lower': forecast_value * 0.8,
                'yhat_upper': forecast_value * 1.2
            })
        
        self.forecast = pd.DataFrame(forecast_data)
        
        # Combine historical data with forecast
        historical_forecast = data[['ds', 'y']].copy()
        historical_forecast['yhat'] = data['y']
        historical_forecast['yhat_lower'] = data['y'] * 0.95
        historical_forecast['yhat_upper'] = data['y'] * 1.05
        
        self.forecast = pd.concat([historical_forecast, self.forecast], ignore_index=True)
        
        # Calculate simple validation metrics
        validation_days = min(30, len(data) // 4)
        if validation_days > 0:
            val_actual = data['y'].iloc[-validation_days:].values
            val_pred = data['ma_7'].iloc[-validation_days:].values
            val_pred = val_pred[~np.isnan(val_pred)]
            val_actual = val_actual[:len(val_pred)]
            
            if len(val_pred) > 0:
                mae = np.mean(np.abs(val_actual - val_pred))
                mape = np.mean(np.abs((val_actual - val_pred) / val_actual)) * 100
                rmse = np.sqrt(np.mean((val_actual - val_pred) ** 2))
            else:
                mae = mape = rmse = 0
        else:
            mae = mape = rmse = 0
        
        metrics = {
            'mae': mae,
            'mape': mape,
            'rmse': rmse,
            'validation_days': validation_days
        }
        
        print(f"Alternative model trained. Validation metrics:")
        print(f"  MAE: ${mae:,.2f}")
        print(f"  MAPE: {mape:.2f}%")
        print(f"  RMSE: ${rmse:,.2f}")
        
        return {
            'model': 'alternative',
            'forecast': self.forecast,
            'metrics': metrics
        }
    
    def analyze_forecast_components(self) -> Dict[str, pd.DataFrame]:
        """Analyze forecast components (trend, seasonality, holidays)."""
        if not PROPHET_AVAILABLE or self.model is None:
            return {}
        
        print("Analyzing forecast components...")
        
        # Get forecast components
        components = self.model.predict(self.model.make_future_dataframe(periods=0))
        
        # Extract components
        trend = components[['ds', 'trend']]
        weekly = components[['ds', 'weekly']]
        yearly = components[['ds', 'yearly']]
        
        # Holiday effects if available
        holiday_cols = [col for col in components.columns if col.startswith('holidays')]
        holidays = components[['ds'] + holiday_cols] if holiday_cols else pd.DataFrame({'ds': components['ds']})
        
        return {
            'trend': trend,
            'weekly': weekly,
            'yearly': yearly,
            'holidays': holidays
        }
    
    def plot_forecast_results(self, output_dir: str = "notebooks"):
        """Create comprehensive forecast visualizations."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if self.forecast is None:
            print("No forecast available. Run train_prophet_model first.")
            return
        
        # 1. Main forecast plot
        plt.figure(figsize=(15, 8))
        
        # Plot historical data
        historical_data = self.daily_sales[self.daily_sales['ds'] <= self.forecast['ds'].max()]
        plt.plot(historical_data['ds'], historical_data['y'], 'b-', label='Historical Sales', linewidth=2)
        
        # Plot forecast
        forecast_data = self.forecast[self.forecast['ds'] > historical_data['ds'].max()]
        plt.plot(forecast_data['ds'], forecast_data['yhat'], 'r-', label='Forecast', linewidth=2)
        plt.fill_between(forecast_data['ds'], forecast_data['yhat_lower'], forecast_data['yhat_upper'], 
                         alpha=0.3, color='red', label='Uncertainty Interval')
        
        plt.title('Sales Forecast - Next 90 Days', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Sales ($)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/sales_forecast.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Forecast components (if Prophet available)
        if PROPHET_AVAILABLE and self.model is not None:
            fig = self.model.plot_components(self.forecast, figsize=(15, 12))
            plt.suptitle('Forecast Components Analysis', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/forecast_components.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Recent performance focus
        plt.figure(figsize=(15, 8))
        
        # Focus on last 90 days historical + 90 days forecast
        recent_date = self.daily_sales['ds'].max() - timedelta(days=90)
        recent_historical = self.daily_sales[self.daily_sales['ds'] >= recent_date]
        
        plt.plot(recent_historical['ds'], recent_historical['y'], 'b-', label='Recent Historical', linewidth=2)
        plt.plot(forecast_data['ds'], forecast_data['yhat'], 'r-', label='Forecast', linewidth=2)
        plt.fill_between(forecast_data['ds'], forecast_data['yhat_lower'], forecast_data['yhat_upper'], 
                         alpha=0.3, color='red')
        
        plt.title('Recent Sales & 90-Day Forecast', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Sales ($)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/recent_forecast.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Forecast plots saved to {output_dir}/")
    
    def generate_forecast_summary(self, output_dir: str = "notebooks") -> Dict[str, Any]:
        """Generate summary statistics and insights from the forecast."""
        if self.forecast is None:
            print("No forecast available. Run train_prophet_model first.")
            return {}
        
        # Separate forecast from historical
        historical_data = self.daily_sales[self.daily_sales['ds'] <= self.forecast['ds'].max()]
        forecast_data = self.forecast[self.forecast['ds'] > historical_data['ds'].max()]
        
        # Calculate summary statistics
        summary = {
            'historical_stats': {
                'total_revenue': historical_data['y'].sum(),
                'avg_daily_sales': historical_data['y'].mean(),
                'median_daily_sales': historical_data['y'].median(),
                'std_daily_sales': historical_data['y'].std(),
                'min_daily_sales': historical_data['y'].min(),
                'max_daily_sales': historical_data['y'].max()
            },
            'forecast_stats': {
                'forecast_period_days': len(forecast_data),
                'total_forecast_revenue': forecast_data['yhat'].sum(),
                'avg_forecast_daily_sales': forecast_data['yhat'].mean(),
                'median_forecast_daily_sales': forecast_data['yhat'].median(),
                'std_forecast_daily_sales': forecast_data['yhat'].std(),
                'min_forecast_daily_sales': forecast_data['yhat'].min(),
                'max_forecast_daily_sales': forecast_data['yhat'].max()
            },
            'growth_analysis': {
                'revenue_growth_rate': ((forecast_data['yhat'].mean() - historical_data['y'].mean()) / 
                                       historical_data['y'].mean() * 100),
                'total_growth_amount': forecast_data['yhat'].sum() - (historical_data['y'].mean() * len(forecast_data))
            }
        }
        
        # Save summary and forecast data
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save forecast data
        self.forecast.to_csv(f"{output_dir}/sales_forecast_data.csv", index=False)
        
        # Save summary statistics
        summary_df = pd.DataFrame({
            'Metric': ['Historical Total Revenue', 'Historical Avg Daily Sales', 'Forecast Total Revenue', 
                     'Forecast Avg Daily Sales', 'Revenue Growth Rate (%)', 'Revenue Growth Amount ($)'],
            'Value': [summary['historical_stats']['total_revenue'], summary['historical_stats']['avg_daily_sales'],
                     summary['forecast_stats']['total_forecast_revenue'], summary['forecast_stats']['avg_forecast_daily_sales'],
                     summary['growth_analysis']['revenue_growth_rate'], summary['growth_analysis']['total_growth_amount']]
        })
        summary_df.to_csv(f"{output_dir}/forecast_summary.csv", index=False)
        
        print(f"Forecast summary saved to {output_dir}/")
        print(f"Key Insights:")
        print(f"  Forecast Period: {summary['forecast_stats']['forecast_period_days']} days")
        print(f"  Expected Revenue Growth: {summary['growth_analysis']['revenue_growth_rate']:.2f}%")
        print(f"  Total Growth Amount: ${summary['growth_analysis']['total_growth_amount']:,.2f}")
        
        return summary
    
    def run_forecasting_pipeline(self, forecast_periods: int = 90, output_dir: str = "notebooks") -> Dict[str, Any]:
        """Run complete sales forecasting pipeline."""
        print("Running Sales Forecasting Pipeline...")
        
        # Prepare data
        daily_sales = self.prepare_daily_sales_data()
        
        # Train model
        model_results = self.train_prophet_model(daily_sales, forecast_periods)
        
        # Analyze components
        components = self.analyze_forecast_components()
        
        # Create visualizations
        self.plot_forecast_results(output_dir)
        
        # Generate summary
        summary = self.generate_forecast_summary(output_dir)
        
        return {
            'daily_sales': daily_sales,
            'model_results': model_results,
            'components': components,
            'summary': summary
        }

if __name__ == "__main__":
    # Load data and run sales forecasting
    transactions_df = pd.read_csv("../data/transactions.csv")
    
    # Run forecasting pipeline
    forecasting_model = SalesForecastingModel(transactions_df)
    results = forecasting_model.run_forecasting_pipeline(forecast_periods=90, output_dir="../notebooks")
