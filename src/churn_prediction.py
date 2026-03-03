"""
Customer Churn Prediction Model
Feature engineering, model training, and evaluation for customer churn prediction.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve, precision_recall_curve
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class ChurnPredictionModel:
    """Customer Churn Prediction with comprehensive feature engineering and model evaluation."""
    
    def __init__(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame):
        """
        Initialize churn prediction model.
        
        Args:
            transactions_df: Transaction data
            customers_df: Customer data
        """
        self.transactions = transactions_df.copy()
        self.customers = customers_df.copy()
        
        # Convert date columns
        self.transactions['order_date'] = pd.to_datetime(self.transactions['order_date'])
        self.customers['registration_date'] = pd.to_datetime(self.customers['registration_date'])
        if 'churn_date' in self.customers.columns:
            self.customers['churn_date'] = pd.to_datetime(self.customers['churn_date'])
        
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.label_encoders = {}
        
    def feature_engineering(self) -> pd.DataFrame:
        """Perform comprehensive feature engineering for churn prediction."""
        print("Performing Feature Engineering...")
        
        # Calculate customer-level features from transactions
        customer_features = self.transactions.groupby('customer_id').agg({
            'order_date': ['min', 'max', 'count'],
            'total_amount': ['sum', 'mean', 'std'],
            'quantity': ['sum', 'mean'],
            'category': 'nunique',
            'payment_method': 'nunique',
            'marketing_channel': 'nunique'
        }).reset_index()
        
        # Flatten column names
        customer_features.columns = ['customer_id', 'first_order', 'last_order', 'order_count',
                                  'total_revenue', 'avg_order_value', 'std_order_value',
                                  'total_quantity', 'avg_quantity',
                                  'unique_categories', 'unique_payment_methods', 'unique_channels']
        
        # Calculate recency and frequency features
        current_date = self.transactions['order_date'].max() + timedelta(days=1)
        customer_features['recency_days'] = (current_date - customer_features['last_order']).dt.days
        customer_features['customer_lifespan_days'] = (customer_features['last_order'] - customer_features['first_order']).dt.days + 1
        customer_features['days_since_first_order'] = (current_date - customer_features['first_order']).dt.days
        
        # Calculate purchase frequency (orders per month)
        customer_features['purchase_frequency'] = customer_features['order_count'] / (customer_features['customer_lifespan_days'] / 30)
        
        # Calculate average days between orders
        customer_features['avg_days_between_orders'] = customer_features['customer_lifespan_days'] / customer_features['order_count']
        
        # Fill NaN values for std_order_value (customers with single order)
        customer_features['std_order_value'] = customer_features['std_order_value'].fillna(0)
        
        # Calculate category preferences
        category_preferences = self.transactions.groupby(['customer_id', 'category']).agg({
            'total_amount': 'sum'
        }).reset_index()
        
        # Find most preferred category for each customer
        max_category_idx = category_preferences.groupby('customer_id')['total_amount'].idxmax()
        preferred_categories = category_preferences.loc[max_category_idx][['customer_id', 'category']]
        preferred_categories.columns = ['customer_id', 'preferred_category']
        
        # Calculate category spending ratios
        customer_total_spending = category_preferences.groupby('customer_id')['total_amount'].sum().reset_index()
        category_preferences = category_preferences.merge(customer_total_spending, on='customer_id', suffixes=('', '_total'))
        category_preferences['category_spending_ratio'] = category_preferences['total_amount'] / category_preferences['total_amount_total']
        
        # Get top 3 categories by spending ratio for each customer
        top_categories = category_preferences.sort_values(['customer_id', 'category_spending_ratio'], ascending=[True, False])
        top_categories['rank'] = top_categories.groupby('customer_id').cumcount() + 1
        top_categories = top_categories[top_categories['rank'] <= 3]
        
        # Pivot to create category features
        category_features = top_categories.pivot_table(
            index='customer_id', 
            columns='rank', 
            values='category_spending_ratio',
            fill_value=0
        ).reset_index()
        category_features.columns = ['customer_id', 'top1_category_ratio', 'top2_category_ratio', 'top3_category_ratio']
        
        # Calculate temporal features
        customer_features['orders_last_30_days'] = self.transactions[
            self.transactions['order_date'] >= (current_date - timedelta(days=30))
        ].groupby('customer_id').size().reset_index(name='orders_last_30_days').set_index('customer_id')['orders_last_30_days']
        
        customer_features['orders_last_90_days'] = self.transactions[
            self.transactions['order_date'] >= (current_date - timedelta(days=90))
        ].groupby('customer_id').size().reset_index(name='orders_last_90_days').set_index('customer_id')['orders_last_90_days']
        
        customer_features['revenue_last_30_days'] = self.transactions[
            self.transactions['order_date'] >= (current_date - timedelta(days=30))
        ].groupby('customer_id')['total_amount'].sum().reset_index(name='revenue_last_30_days').set_index('customer_id')['revenue_last_30_days']
        
        customer_features['revenue_last_90_days'] = self.transactions[
            self.transactions['order_date'] >= (current_date - timedelta(days=90))
        ].groupby('customer_id')['total_amount'].sum().reset_index(name='revenue_last_90_days').set_index('customer_id')['revenue_last_90_days']
        
        # Fill NaN values for customers with no recent activity
        customer_features['orders_last_30_days'] = customer_features['orders_last_30_days'].fillna(0)
        customer_features['orders_last_90_days'] = customer_features['orders_last_90_days'].fillna(0)
        customer_features['revenue_last_30_days'] = customer_features['revenue_last_30_days'].fillna(0)
        customer_features['revenue_last_90_days'] = customer_features['revenue_last_90_days'].fillna(0)
        
        # Merge with customer demographic data
        customer_features = customer_features.merge(self.customers, on='customer_id')
        customer_features = customer_features.merge(preferred_categories, on='customer_id', how='left')
        customer_features = customer_features.merge(category_features, on='customer_id', how='left')
        
        # Fill missing values
        customer_features['preferred_category'] = customer_features['preferred_category'].fillna('Unknown')
        customer_features['top1_category_ratio'] = customer_features['top1_category_ratio'].fillna(0)
        customer_features['top2_category_ratio'] = customer_features['top2_category_ratio'].fillna(0)
        customer_features['top3_category_ratio'] = customer_features['top3_category_ratio'].fillna(0)
        
        # Calculate additional derived features
        customer_features['revenue_change_ratio'] = np.where(
            customer_features['revenue_last_90_days'] > 0,
            customer_features['revenue_last_30_days'] / customer_features['revenue_last_90_days'],
            0
        )
        
        customer_features['order_activity_ratio'] = np.where(
            customer_features['orders_last_90_days'] > 0,
            customer_features['orders_last_30_days'] / customer_features['orders_last_90_days'],
            0
        )
        
        # Encode categorical variables
        categorical_columns = ['region', 'preferred_category']
        
        for col in categorical_columns:
            if col in customer_features.columns:
                le = LabelEncoder()
                customer_features[f'{col}_encoded'] = le.fit_transform(customer_features[col].astype(str))
                self.label_encoders[col] = le
        
        return customer_features
    
    def prepare_data(self, features_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Prepare data for modeling."""
        print("Preparing data for modeling...")
        
        # Select features for modeling
        feature_cols = [
            'order_count', 'total_revenue', 'avg_order_value', 'std_order_value',
            'recency_days', 'customer_lifespan_days', 'purchase_frequency',
            'avg_days_between_orders', 'unique_categories', 'unique_payment_methods',
            'unique_channels', 'orders_last_30_days', 'orders_last_90_days',
            'revenue_last_30_days', 'revenue_last_90_days', 'revenue_change_ratio',
            'order_activity_ratio', 'top1_category_ratio', 'top2_category_ratio',
            'top3_category_ratio', 'engagement_score', 'region_encoded',
            'preferred_category_encoded'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_cols if col in features_df.columns]
        self.feature_columns = available_features
        
        X = features_df[available_features].fillna(0)
        y = features_df['churned'].astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrame for feature importance
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=available_features)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=available_features)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_models(self, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series):
        """Train multiple models and compare performance."""
        print("Training models...")
        
        # Logistic Regression
        print("Training Logistic Regression...")
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train, y_train)
        self.models['logistic_regression'] = lr_model
        
        # XGBoost
        print("Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            random_state=42,
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8
        )
        xgb_model.fit(X_train, y_train)
        self.models['xgboost'] = xgb_model
        
        # Random Forest
        print("Training Random Forest...")
        rf_model = RandomForestClassifier(
            random_state=42,
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        rf_model.fit(X_train, y_train)
        self.models['random_forest'] = rf_model
    
    def evaluate_models(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Dict]:
        """Evaluate all models and return performance metrics."""
        print("Evaluating models...")
        
        results = {}
        
        for name, model in self.models.items():
            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba)
            
            results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc_roc': auc,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'model': model
            }
        
        return results
    
    def feature_importance_analysis(self, X_train: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze feature importance for tree-based models."""
        print("Analyzing feature importance...")
        
        importance_results = {}
        
        # XGBoost feature importance
        if 'xgboost' in self.models:
            xgb_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': self.models['xgboost'].feature_importances_
            }).sort_values('importance', ascending=False)
            importance_results['xgboost'] = xgb_importance
        
        # Random Forest feature importance
        if 'random_forest' in self.models:
            rf_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': self.models['random_forest'].feature_importances_
            }).sort_values('importance', ascending=False)
            importance_results['random_forest'] = rf_importance
        
        return importance_results
    
    def plot_model_performance(self, results: Dict[str, Dict], y_test: pd.Series, output_dir: str = "notebooks"):
        """Create visualization plots for model performance."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Model comparison metrics
        metrics_df = pd.DataFrame({
            name: {
                'Accuracy': metrics['accuracy'],
                'Precision': metrics['precision'],
                'Recall': metrics['recall'],
                'F1-Score': metrics['f1_score'],
                'AUC-ROC': metrics['auc_roc']
            }
            for name, metrics in results.items()
        }).T
        
        plt.figure(figsize=(12, 8))
        metrics_df.plot(kind='bar', figsize=(12, 8))
        plt.title('Model Performance Comparison')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/model_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. ROC curves
        plt.figure(figsize=(10, 8))
        for name, metrics in results.items():
            fpr, tpr, _ = roc_curve(y_test, metrics['probabilities'])
            auc = metrics['auc_roc']
            plt.plot(fpr, tpr, label=f'{name} (AUC = {auc:.3f})')
        
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/roc_curves.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Model performance plots saved to {output_dir}/")
    
    def run_churn_prediction_pipeline(self, output_dir: str = "notebooks") -> Dict[str, Any]:
        """Run complete churn prediction pipeline."""
        print("Running Churn Prediction Pipeline...")
        
        # Feature engineering
        features_df = self.feature_engineering()
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(features_df)
        
        # Train models
        self.train_models(X_train, X_test, y_train, y_test)
        
        # Evaluate models
        results = self.evaluate_models(X_test, y_test)
        
        # Feature importance
        importance_results = self.feature_importance_analysis(X_train)
        
        # Create visualizations
        self.plot_model_performance(results, y_test, output_dir)
        
        # Save results
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save feature engineered dataset
        features_df.to_csv(f"{output_dir}/churn_features.csv", index=False)
        
        # Save model predictions
        predictions_df = pd.DataFrame({
            'customer_id': features_df.loc[X_test.index, 'customer_id'],
            'actual_churn': y_test.values,
            'lr_prediction': results['logistic_regression']['predictions'],
            'lr_probability': results['logistic_regression']['probabilities'],
            'xgb_prediction': results['xgboost']['predictions'],
            'xgb_probability': results['xgboost']['probabilities'],
            'rf_prediction': results['random_forest']['predictions'],
            'rf_probability': results['random_forest']['probabilities']
        })
        predictions_df.to_csv(f"{output_dir}/churn_predictions.csv", index=False)
        
        # Save feature importance
        for model_name, importance_df in importance_results.items():
            importance_df.to_csv(f"{output_dir}/feature_importance_{model_name}.csv", index=False)
        
        # Print summary
        print("\n=== CHURN PREDICTION RESULTS ===")
        for name, metrics in results.items():
            print(f"\n{name.upper()}:")
            print(f"  Accuracy: {metrics['accuracy']:.3f}")
            print(f"  Precision: {metrics['precision']:.3f}")
            print(f"  Recall: {metrics['recall']:.3f}")
            print(f"  F1-Score: {metrics['f1_score']:.3f}")
            print(f"  AUC-ROC: {metrics['auc_roc']:.3f}")
        
        return {
            'features': features_df,
            'results': results,
            'importance': importance_results,
            'feature_columns': self.feature_columns
        }

if __name__ == "__main__":
    # Load data and run churn prediction
    transactions_df = pd.read_csv("../data/transactions.csv")
    customers_df = pd.read_csv("../data/customers.csv")
    
    # Run churn prediction pipeline
    churn_model = ChurnPredictionModel(transactions_df, customers_df)
    results = churn_model.run_churn_prediction_pipeline("../notebooks")
