"""
Customer Segmentation Model
KMeans clustering with PCA visualization for customer segmentation analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.manifold import TSNE
from datetime import timedelta
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class CustomerSegmentationModel:
    """Customer segmentation using KMeans clustering with comprehensive analysis."""
    
    def __init__(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame):
        """
        Initialize customer segmentation model.
        
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
        
        self.scaler = StandardScaler()
        self.kmeans = None
        self.pca = None
        self.segment_labels = None
        self.feature_columns = []
        
    def prepare_segmentation_features(self) -> pd.DataFrame:
        """Prepare comprehensive features for customer segmentation."""
        print("Preparing customer segmentation features...")
        
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
        
        # Fill NaN values
        customer_features['std_order_value'] = customer_features['std_order_value'].fillna(0)
        customer_features['avg_days_between_orders'] = customer_features['avg_days_between_orders'].fillna(customer_features['customer_lifespan_days'])
        
        # Calculate category preferences and diversity
        category_stats = self.transactions.groupby(['customer_id', 'category']).agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        # Category concentration (Herfindahl index)
        category_stats['total_spending'] = category_stats.groupby('customer_id')['total_amount'].transform('sum')
        category_stats['spending_share'] = category_stats['total_amount'] / category_stats['total_spending']
        herfindahl_index = category_stats.groupby('customer_id')['spending_share'].apply(lambda x: (x**2).sum()).reset_index()
        herfindahl_index.columns = ['customer_id', 'category_concentration']
        
        # Merge category concentration
        customer_features = customer_features.merge(herfindahl_index, on='customer_id')
        
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
        
        # Calculate activity ratios
        customer_features['recent_activity_ratio'] = np.where(
            customer_features['orders_last_90_days'] > 0,
            customer_features['orders_last_30_days'] / customer_features['orders_last_90_days'],
            0
        )
        
        customer_features['recent_revenue_ratio'] = np.where(
            customer_features['revenue_last_90_days'] > 0,
            customer_features['revenue_last_30_days'] / customer_features['revenue_last_90_days'],
            0
        )
        
        # Merge with customer demographic data
        customer_features = customer_features.merge(self.customers, on='customer_id')
        
        return customer_features
    
    def select_features_for_clustering(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Select and prepare features for clustering."""
        print("Selecting features for clustering...")
        
        # Select relevant features for clustering
        feature_cols = [
            'order_count', 'total_revenue', 'avg_order_value', 'std_order_value',
            'recency_days', 'customer_lifespan_days', 'purchase_frequency',
            'avg_days_between_orders', 'unique_categories', 'unique_payment_methods',
            'unique_channels', 'orders_last_30_days', 'orders_last_90_days',
            'revenue_last_30_days', 'revenue_last_90_days', 'recent_activity_ratio',
            'recent_revenue_ratio', 'category_concentration', 'engagement_score'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_cols if col in features_df.columns]
        self.feature_columns = available_features
        
        # Extract features
        X = features_df[available_features].fillna(0)
        
        # Log transform skewed features
        skewed_features = ['total_revenue', 'avg_order_value', 'revenue_last_30_days', 'revenue_last_90_days']
        for feature in skewed_features:
            if feature in X.columns:
                X[feature] = np.log1p(X[feature])
        
        return X
    
    def find_optimal_clusters(self, X: pd.DataFrame, max_clusters: int = 10) -> Dict[str, Any]:
        """Find optimal number of clusters using elbow method and silhouette analysis."""
        print("Finding optimal number of clusters...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Test different numbers of clusters
        inertias = []
        silhouette_scores = []
        calinski_scores = []
        
        cluster_range = range(2, max_clusters + 1)
        
        for k in cluster_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
            calinski_scores.append(calinski_harabasz_score(X_scaled, cluster_labels))
        
        # Find optimal k based on silhouette score
        optimal_k_silhouette = cluster_range[np.argmax(silhouette_scores)]
        
        # Find optimal k based on elbow method (simplified)
        if len(inertias) > 2:
            # Calculate second derivative to find elbow
            diffs = np.diff(inertias)
            second_diffs = np.diff(diffs)
            if len(second_diffs) > 0:
                optimal_k_elbow = cluster_range[np.argmax(second_diffs) + 2]
            else:
                optimal_k_elbow = optimal_k_silhouette
        else:
            optimal_k_elbow = optimal_k_silhouette
        
        # Choose final optimal k
        optimal_k = max(3, min(optimal_k_silhouette, optimal_k_elbow))
        
        results = {
            'optimal_k': optimal_k,
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'calinski_scores': calinski_scores,
            'cluster_range': list(cluster_range),
            'optimal_k_silhouette': optimal_k_silhouette,
            'optimal_k_elbow': optimal_k_elbow
        }
        
        print(f"Optimal number of clusters: {optimal_k}")
        print(f"Silhouette score for k={optimal_k}: {max(silhouette_scores):.3f}")
        
        return results
    
    def perform_clustering(self, X: pd.DataFrame, n_clusters: int) -> np.ndarray:
        """Perform KMeans clustering."""
        print(f"Performing KMeans clustering with {n_clusters} clusters...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        self.segment_labels = cluster_labels
        
        # Calculate clustering metrics
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        calinski_avg = calinski_harabasz_score(X_scaled, cluster_labels)
        
        print(f"Clustering completed:")
        print(f"  Silhouette Score: {silhouette_avg:.3f}")
        print(f"  Calinski-Harabasz Score: {calinski_avg:.3f}")
        
        return cluster_labels
    
    def perform_pca(self, X: pd.DataFrame, n_components: int = 2) -> Tuple[np.ndarray, PCA]:
        """Perform PCA for dimensionality reduction and visualization."""
        print(f"Performing PCA with {n_components} components...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform PCA
        self.pca = PCA(n_components=n_components, random_state=42)
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Print explained variance
        explained_variance = self.pca.explained_variance_ratio_
        print(f"Explained variance ratio: {explained_variance}")
        print(f"Total explained variance: {sum(explained_variance):.3f}")
        
        return X_pca, self.pca
    
    def analyze_segments(self, features_df: pd.DataFrame, cluster_labels: np.ndarray) -> pd.DataFrame:
        """Analyze and characterize customer segments."""
        print("Analyzing customer segments...")
        
        # Add cluster labels to features
        segmented_data = features_df.copy()
        segmented_data['segment'] = cluster_labels
        
        # Calculate segment statistics
        segment_analysis = segmented_data.groupby('segment').agg({
            'customer_id': 'count',
            'order_count': ['mean', 'median', 'std'],
            'total_revenue': ['mean', 'median', 'std'],
            'avg_order_value': ['mean', 'median'],
            'recency_days': ['mean', 'median'],
            'purchase_frequency': ['mean', 'median'],
            'unique_categories': ['mean', 'median'],
            'engagement_score': ['mean', 'median'],
            'churned': 'mean'
        }).reset_index()
        
        # Flatten column names
        segment_analysis.columns = ['segment', 'count', 'order_count_mean', 'order_count_median', 'order_count_std',
                                  'revenue_mean', 'revenue_median', 'revenue_std',
                                  'avg_order_value_mean', 'avg_order_value_median',
                                  'recency_mean', 'recency_median',
                                  'frequency_mean', 'frequency_median',
                                  'categories_mean', 'categories_median',
                                  'engagement_mean', 'engagement_median',
                                  'churn_rate']
        
        # Calculate segment sizes as percentages
        total_customers = len(segmented_data)
        segment_analysis['segment_size_pct'] = (segment_analysis['count'] / total_customers) * 100
        
        # Create segment names based on characteristics
        segment_names = []
        for _, row in segment_analysis.iterrows():
            segment_id = int(row['segment'])
            
            if row['revenue_mean'] > segment_analysis['revenue_mean'].quantile(0.75):
                if row['frequency_mean'] > segment_analysis['frequency_mean'].quantile(0.75):
                    segment_names.append(f"VIP Champions (Segment {segment_id})")
                else:
                    segment_names.append(f"High Value (Segment {segment_id})")
            elif row['frequency_mean'] > segment_analysis['frequency_mean'].quantile(0.75):
                segment_names.append(f"Frequent Buyers (Segment {segment_id})")
            elif row['recency_mean'] < segment_analysis['recency_mean'].quantile(0.25):
                segment_names.append(f"Recent Customers (Segment {segment_id})")
            elif row['churn_rate'] > 0.5:
                segment_names.append(f"At Risk (Segment {segment_id})")
            else:
                segment_names.append(f"Standard Customers (Segment {segment_id})")
        
        segment_analysis['segment_name'] = segment_names
        
        return segment_analysis, segmented_data
    
    def plot_segmentation_results(self, X: pd.DataFrame, cluster_labels: np.ndarray, 
                                segment_analysis: pd.DataFrame, output_dir: str = "notebooks"):
        """Create comprehensive visualizations for customer segmentation."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. PCA visualization
        X_pca, pca = self.perform_pca(X, n_components=2)
        
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', alpha=0.6, s=50)
        plt.colorbar(scatter, label='Segment')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.3f} variance explained)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.3f} variance explained)')
        plt.title('Customer Segments - PCA Visualization', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/segments_pca.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Cluster analysis plots
        optimal_results = self.find_optimal_clusters(X)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Elbow plot
        axes[0, 0].plot(optimal_results['cluster_range'], optimal_results['inertias'], 'bo-')
        axes[0, 0].axvline(x=optimal_results['optimal_k'], color='r', linestyle='--', label=f'Optimal k={optimal_results["optimal_k"]}')
        axes[0, 0].set_xlabel('Number of Clusters')
        axes[0, 0].set_ylabel('Inertia')
        axes[0, 0].set_title('Elbow Method')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Silhouette scores
        axes[0, 1].plot(optimal_results['cluster_range'], optimal_results['silhouette_scores'], 'go-')
        axes[0, 1].axvline(x=optimal_results['optimal_k'], color='r', linestyle='--', label=f'Optimal k={optimal_results["optimal_k"]}')
        axes[0, 1].set_xlabel('Number of Clusters')
        axes[0, 1].set_ylabel('Silhouette Score')
        axes[0, 1].set_title('Silhouette Analysis')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Calinski-Harabasz scores
        axes[1, 0].plot(optimal_results['cluster_range'], optimal_results['calinski_scores'], 'mo-')
        axes[1, 0].axvline(x=optimal_results['optimal_k'], color='r', linestyle='--', label=f'Optimal k={optimal_results["optimal_k"]}')
        axes[1, 0].set_xlabel('Number of Clusters')
        axes[1, 0].set_ylabel('Calinski-Harabasz Score')
        axes[1, 0].set_title('Calinski-Harabasz Index')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Segment sizes
        segment_sizes = segment_analysis['count'].values
        segment_labels_plot = [f'Segment {i}' for i in range(len(segment_sizes))]
        colors = plt.cm.viridis(np.linspace(0, 1, len(segment_sizes)))
        
        axes[1, 1].pie(segment_sizes, labels=segment_labels_plot, autopct='%1.1f%%', colors=colors)
        axes[1, 1].set_title('Segment Size Distribution')
        
        plt.suptitle('Customer Segmentation Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/segmentation_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Segment characteristics radar chart
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Normalize features for radar chart
        features_for_radar = ['order_count_mean', 'revenue_mean', 'avg_order_value_mean', 
                            'frequency_mean', 'categories_mean', 'engagement_mean']
        
        for i, (_, segment) in enumerate(segment_analysis.iterrows()):
            if i >= 6:  # Limit to 6 segments for visualization
                break
                
            values = [segment[feat] for feat in features_for_radar]
            # Normalize values to 0-1 scale
            max_vals = segment_analysis[features_for_radar].max()
            normalized_values = [val/max_vals[feat] for val, feat in zip(values, features_for_radar)]
            
            # Add first value to close the radar chart
            normalized_values += normalized_values[:1]
            features_for_radar_closed = features_for_radar + [features_for_radar[0]]
            
            angles = np.linspace(0, 2*np.pi, len(features_for_radar_closed), endpoint=False).tolist()
            
            ax = axes[i]
            ax.plot(angles, normalized_values, 'o-', linewidth=2, label=segment['segment_name'])
            ax.fill(angles, normalized_values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(features_for_radar, fontsize=8)
            ax.set_ylim(0, 1)
            ax.set_title(segment['segment_name'], fontsize=10, fontweight='bold')
            ax.grid(True)
        
        # Hide unused subplots
        for i in range(len(segment_analysis), 6):
            axes[i].set_visible(False)
        
        plt.suptitle('Segment Characteristics Radar Charts', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/segment_radar_charts.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Segmentation plots saved to {output_dir}/")
    
    def run_segmentation_pipeline(self, output_dir: str = "notebooks") -> Dict[str, Any]:
        """Run complete customer segmentation pipeline."""
        print("Running Customer Segmentation Pipeline...")
        
        # Prepare features
        features_df = self.prepare_segmentation_features()
        
        # Select features for clustering
        X = self.select_features_for_clustering(features_df)
        
        # Find optimal number of clusters
        optimal_results = self.find_optimal_clusters(X)
        optimal_k = optimal_results['optimal_k']
        
        # Perform clustering
        cluster_labels = self.perform_clustering(X, optimal_k)
        
        # Analyze segments
        segment_analysis, segmented_data = self.analyze_segments(features_df, cluster_labels)
        
        # Create visualizations
        self.plot_segmentation_results(X, cluster_labels, segment_analysis, output_dir)
        
        # Save results
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save segmented data
        segmented_data.to_csv(f"{output_dir}/customer_segments.csv", index=False)
        
        # Save segment analysis
        segment_analysis.to_csv(f"{output_dir}/segment_analysis.csv", index=False)
        
        # Save clustering metrics
        metrics_df = pd.DataFrame({
            'n_clusters': optimal_results['cluster_range'],
            'inertia': optimal_results['inertias'],
            'silhouette_score': optimal_results['silhouette_scores'],
            'calinski_score': optimal_results['calinski_scores']
        })
        metrics_df.to_csv(f"{output_dir}/clustering_metrics.csv", index=False)
        
        print(f"\n=== CUSTOMER SEGMENTATION RESULTS ===")
        print(f"Optimal number of clusters: {optimal_k}")
        print(f"Silhouette Score: {max(optimal_results['silhouette_scores']):.3f}")
        print(f"\nSegment Summary:")
        for _, segment in segment_analysis.iterrows():
            print(f"  {segment['segment_name']}: {segment['count']} customers ({segment['segment_size_pct']:.1f}%)")
        
        return {
            'features': features_df,
            'segmented_data': segmented_data,
            'segment_analysis': segment_analysis,
            'optimal_results': optimal_results,
            'cluster_labels': cluster_labels,
            'feature_columns': self.feature_columns
        }

if __name__ == "__main__":
    # Load data and run customer segmentation
    transactions_df = pd.read_csv("../data/transactions.csv")
    customers_df = pd.read_csv("../data/customers.csv")
    
    # Run segmentation pipeline
    segmentation_model = CustomerSegmentationModel(transactions_df, customers_df)
    results = segmentation_model.run_segmentation_pipeline("../notebooks")
