"""
Synthetic E-commerce Data Generator
Generates realistic e-commerce transaction data for ML modeling and analysis.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Tuple, Dict, Any

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class EcommerceDataGenerator:
    """Generates synthetic e-commerce data with realistic patterns."""
    
    def __init__(self, n_customers: int = 5000, n_products: int = 200, n_transactions: int = 50000):
        """
        Initialize the data generator.
        
        Args:
            n_customers: Number of unique customers
            n_products: Number of unique products
            n_transactions: Number of transactions to generate
        """
        self.n_customers = n_customers
        self.n_products = n_products
        self.n_transactions = n_transactions
        self.start_date = datetime(2022, 1, 1)
        self.end_date = datetime(2023, 12, 31)
        
        # Define realistic categories and their price ranges
        self.categories = {
            'Electronics': {'price_range': (50, 1000), 'weight': 0.25},
            'Clothing': {'price_range': (20, 200), 'weight': 0.20},
            'Home & Garden': {'price_range': (30, 500), 'weight': 0.15},
            'Sports & Outdoors': {'price_range': (25, 300), 'weight': 0.12},
            'Books & Media': {'price_range': (10, 100), 'weight': 0.10},
            'Toys & Games': {'price_range': (15, 150), 'weight': 0.08},
            'Beauty & Personal Care': {'price_range': (10, 200), 'weight': 0.06},
            'Food & Beverages': {'price_range': (5, 100), 'weight': 0.04}
        }
        
        # Define regions
        self.regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa']
        
        # Define marketing channels
        self.marketing_channels = ['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Direct', 'Referral']
        
        # Define payment methods
        self.payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Apple Pay', 'Google Pay', 'Bank Transfer']
    
    def generate_products(self) -> pd.DataFrame:
        """Generate product catalog with realistic attributes."""
        products = []
        
        for i in range(self.n_products):
            # Select category based on weights
            category = np.random.choice(
                list(self.categories.keys()),
                p=[self.categories[cat]['weight'] for cat in self.categories.keys()]
            )
            
            price_range = self.categories[category]['price_range']
            base_price = np.random.uniform(price_range[0], price_range[1])
            
            # Add some price variation
            price = round(base_price * np.random.uniform(0.8, 1.2), 2)
            
            products.append({
                'product_id': f'PROD_{i+1:04d}',
                'category': category,
                'price': price,
                'base_price': base_price
            })
        
        return pd.DataFrame(products)
    
    def generate_customers(self) -> pd.DataFrame:
        """Generate customer profiles with realistic attributes."""
        customers = []
        
        for i in range(self.n_customers):
            # Generate customer registration date
            days_since_start = np.random.randint(0, 730)  # Within 2 years
            registration_date = self.start_date + timedelta(days=days_since_start)
            
            # Assign region
            region = np.random.choice(self.regions, p=[0.35, 0.30, 0.20, 0.10, 0.05])
            
            # Generate customer characteristics that affect churn
            # Customers with higher engagement are less likely to churn
            engagement_score = np.random.beta(2, 5)  # Skewed towards lower engagement
            
            # Determine churn probability based on engagement and registration date
            recent_customer = days_since_start < 180  # Less than 6 months
            if recent_customer:
                churn_prob = 0.05  # New customers less likely to churn
            else:
                churn_prob = 0.15 + (1 - engagement_score) * 0.25  # 15% to 40% based on engagement
            
            churned = np.random.random() < churn_prob
            
            # If churned, determine churn date
            if churned:
                # Churn typically happens after some activity
                min_days_active = 30
                max_days_active = min(730 - days_since_start, 365)
                if max_days_active > min_days_active:
                    days_active = np.random.randint(min_days_active, max_days_active)
                    churn_date = registration_date + timedelta(days=days_active)
                else:
                    churn_date = None
                    churned = False
            else:
                churn_date = None
            
            customers.append({
                'customer_id': f'CUST_{i+1:05d}',
                'registration_date': registration_date,
                'region': region,
                'engagement_score': engagement_score,
                'churned': churned,
                'churn_date': churn_date
            })
        
        return pd.DataFrame(customers)
    
    def generate_transactions(self, products_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Generate transaction data with realistic patterns."""
        transactions = []
        
        # Create date range for transactions
        date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        
        # Generate transactions with realistic temporal patterns
        for i in range(self.n_transactions):
            # Select date with seasonal patterns (higher sales in Q4)
            date_idx = np.random.choice(len(date_range))
            selected_date = date_range[date_idx]
            
            # Boost Q4 sales (October-December)
            if selected_date.month in [10, 11, 12]:
                if np.random.random() < 0.3:  # 30% chance to add extra transaction
                    transactions.extend(self._create_single_transaction(
                        selected_date, products_df, customers_df, i
                    ))
                    i += 1
            
            transactions.extend(self._create_single_transaction(
                selected_date, products_df, customers_df, i
            ))
        
        # Trim to exact number of transactions
        transactions = transactions[:self.n_transactions]
        
        return pd.DataFrame(transactions)
    
    def _create_single_transaction(self, date, products_df: pd.DataFrame, customers_df: pd.DataFrame, order_idx: int) -> list:
        """Create a single transaction (could be multiple items)."""
        # Select active customer (not churned or churned after this date)
        active_customers = customers_df[
            (customers_df['registration_date'] <= date) & 
            ((customers_df['churn_date'].isna()) | (customers_df['churn_date'] > date))
        ]
        
        if len(active_customers) == 0:
            return []
        
        customer = active_customers.sample(1).iloc[0]
        
        # Number of items in this transaction (1-5 items)
        n_items = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.25, 0.15, 0.07, 0.03])
        
        transaction_items = []
        
        for item_idx in range(n_items):
            # Select product (popular products have higher chance)
            product = products_df.sample(1).iloc[0]
            
            # Quantity (usually 1, sometimes more)
            quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.7, 0.2, 0.07, 0.02, 0.01])
            
            # Apply small discount sometimes
            if np.random.random() < 0.15:  # 15% discount chance
                discount = np.random.uniform(0.05, 0.30)
                final_price = round(product['price'] * (1 - discount), 2)
            else:
                final_price = product['price']
            
            # Select payment method
            payment_method = np.random.choice(self.payment_methods, p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05])
            
            # Select marketing channel
            marketing_channel = np.random.choice(self.marketing_channels, p=[0.25, 0.20, 0.15, 0.15, 0.15, 0.10])
            
            transaction_items.append({
                'order_id': f'ORDER_{order_idx+1:06d}_{item_idx+1}',
                'customer_id': customer['customer_id'],
                'order_date': date,
                'product_id': product['product_id'],
                'category': product['category'],
                'price': final_price,
                'quantity': quantity,
                'total_amount': round(final_price * quantity, 2),
                'payment_method': payment_method,
                'region': customer['region'],
                'marketing_channel': marketing_channel
            })
        
        return transaction_items
    
    def generate_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate complete e-commerce dataset.
        
        Returns:
            Tuple of (transactions_df, customers_df, products_df)
        """
        print("Generating products catalog...")
        products_df = self.generate_products()
        
        print("Generating customer profiles...")
        customers_df = self.generate_customers()
        
        print("Generating transactions...")
        transactions_df = self.generate_transactions(products_df, customers_df)
        
        print(f"Generated {len(transactions_df)} transactions, {len(customers_df)} customers, {len(products_df)} products")
        
        return transactions_df, customers_df, products_df
    
    def save_dataset(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame, products_df: pd.DataFrame, 
                    output_dir: str = "data"):
        """Save generated datasets to CSV files."""
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save datasets
        transactions_df.to_csv(f"{output_dir}/transactions.csv", index=False)
        customers_df.to_csv(f"{output_dir}/customers.csv", index=False)
        products_df.to_csv(f"{output_dir}/products.csv", index=False)
        
        print(f"Datasets saved to {output_dir}/")
        print(f"- transactions.csv: {len(transactions_df)} rows")
        print(f"- customers.csv: {len(customers_df)} rows")
        print(f"- products.csv: {len(products_df)} rows")

if __name__ == "__main__":
    # Generate the dataset
    generator = EcommerceDataGenerator(
        n_customers=5000,
        n_products=200,
        n_transactions=50000
    )
    
    transactions_df, customers_df, products_df = generator.generate_dataset()
    
    # Save the dataset
    generator.save_dataset(transactions_df, customers_df, products_df, "../data")
