#!/usr/bin/env python3
"""
Excel Exporter Module

This module handles the export of scraped reviews to an Excel file.
"""

import logging
import os
import pandas as pd
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Excel exporter for scraped reviews."""
    
    def __init__(self, config):
        """Initialize the Excel exporter.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.excel_file_path = config['excel_file_path']
        self.sheet_names = config.get('excel_sheet_names', {
            'all_reviews': 'All Reviews',
            'tripadvisor': 'TripAdvisor',
            'yelp': 'Yelp',
            'google': 'Google',
            'summary': 'Summary'
        })
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.excel_file_path)), exist_ok=True)
    
    def export(self, reviews):
        """Export reviews to Excel.
        
        Args:
            reviews (list): List of review dictionaries.
        """
        if not reviews:
            logger.warning("No reviews to export!")
            return
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(reviews)
            
            # Ensure all necessary columns exist
            required_columns = ['platform', 'reviewer_name', 'date', 'rating', 'title', 'text', 'category', 'sentiment']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Format sentiment as 'Positive' or 'Negative'
            df['sentiment'] = df['sentiment'].apply(lambda x: 'Positive' if x else 'Negative')
            
            # Create Excel writer
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                # Export all reviews to a single sheet
                self._export_all_reviews(df, writer)
                
                # Export reviews by platform
                self._export_by_platform(df, writer)
                
                # Export summary
                self._export_summary(df, writer)
            
            logger.info(f"Successfully exported {len(reviews)} reviews to '{self.excel_file_path}'")
            
        except Exception as e:
            logger.error(f"Error exporting reviews to Excel: {e}", exc_info=True)
    
    def _export_all_reviews(self, df, writer):
        """Export all reviews to a single sheet.
        
        Args:
            df (DataFrame): Reviews DataFrame.
            writer (ExcelWriter): Excel writer object.
        """
        # Sort by date (newest first)
        df_sorted = df.sort_values('date', ascending=False)
        
        # Export to Excel
        df_sorted.to_excel(
            writer, 
            sheet_name=self.sheet_names['all_reviews'],
            index=False,
            columns=['platform', 'reviewer_name', 'date', 'rating', 'title', 'text', 'category', 'sentiment']
        )
        
        # Auto-adjust column widths
        for column in df_sorted:
            column_width = max(df_sorted[column].astype(str).map(len).max(), len(column))
            col_idx = df_sorted.columns.get_loc(column)
            writer.sheets[self.sheet_names['all_reviews']].column_dimensions[
                chr(65 + col_idx)].width = min(column_width + 2, 50)  # Limit to 50 characters
        
        # Set text column to wrap text
        text_col_idx = df_sorted.columns.get_loc('text')
        for row in range(2, len(df_sorted) + 2):  # +2 for header and 1-indexing
            cell = writer.sheets[self.sheet_names['all_reviews']].cell(
                row=row, column=text_col_idx + 1)
            cell.alignment = cell.alignment.copy(wrapText=True)
    
    def _export_by_platform(self, df, writer):
        """Export reviews grouped by platform.
        
        Args:
            df (DataFrame): Reviews DataFrame.
            writer (ExcelWriter): Excel writer object.
        """
        platforms = df['platform'].unique()
        
        for platform in platforms:
            platform_df = df[df['platform'] == platform].sort_values('date', ascending=False)
            
            sheet_name = self.sheet_names.get(platform.lower(), platform)
            # Truncate sheet name if too long (Excel limit is 31 chars)
            sheet_name = sheet_name[:31]
            
            platform_df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                columns=['reviewer_name', 'date', 'rating', 'title', 'text', 'category', 'sentiment']
            )
            
            # Auto-adjust column widths
            for column in platform_df:
                column_width = max(platform_df[column].astype(str).map(len).max(), len(column))
                col_idx = platform_df.columns.get_loc(column)
                writer.sheets[sheet_name].column_dimensions[
                    chr(65 + col_idx)].width = min(column_width + 2, 50)  # Limit to 50 characters
            
            # Set text column to wrap text
            text_col_idx = platform_df.columns.get_loc('text')
            for row in range(2, len(platform_df) + 2):  # +2 for header and 1-indexing
                cell = writer.sheets[sheet_name].cell(
                    row=row, column=text_col_idx + 1)
                cell.alignment = cell.alignment.copy(wrapText=True)
    
    def _export_summary(self, df, writer):
        """Export summary statistics.
        
        Args:
            df (DataFrame): Reviews DataFrame.
            writer (ExcelWriter): Excel writer object.
        """
        # Create summary sheet
        summary_sheet = writer.book.create_sheet(self.sheet_names['summary'])
        
        # Add title and date
        summary_sheet['A1'] = f"Review Analysis Summary - {self.config['restaurant_name']}"
        summary_sheet['A2'] = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        summary_sheet['A3'] = f"Date range: {self.config['date_range']['start']} to {self.config['date_range']['end']}"
        
        # Format title
        summary_sheet['A1'].font = summary_sheet['A1'].font.copy(size=14, bold=True)
        
        # Add total counts
        row = 5
        summary_sheet[f'A{row}'] = "Total Reviews"
        summary_sheet[f'B{row}'] = len(df)
        row += 1
        
        # Add counts by platform
        summary_sheet[f'A{row}'] = "Reviews by Platform"
        row += 1
        platform_counts = df['platform'].value_counts()
        for platform, count in platform_counts.items():
            summary_sheet[f'A{row}'] = platform
            summary_sheet[f'B{row}'] = count
            row += 1
        
        # Add counts by rating
        row += 1
        summary_sheet[f'A{row}'] = "Reviews by Rating"
        row += 1
        rating_counts = df['rating'].value_counts().sort_index(ascending=False)
        for rating, count in rating_counts.items():
            summary_sheet[f'A{row}'] = f"{rating} Stars"
            summary_sheet[f'B{row}'] = count
            row += 1
        
        # Add counts by category
        row += 1
        summary_sheet[f'A{row}'] = "Reviews by Category"
        row += 1
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            summary_sheet[f'A{row}'] = category
            summary_sheet[f'B{row}'] = count
            row += 1
        
        # Add counts by sentiment
        row += 1
        summary_sheet[f'A{row}'] = "Reviews by Sentiment"
        row += 1
        sentiment_counts = df['sentiment'].value_counts()
        for sentiment, count in sentiment_counts.items():
            summary_sheet[f'A{row}'] = sentiment
            summary_sheet[f'B{row}'] = count
            row += 1
        
        # Add review count by month
        row += 1
        summary_sheet[f'A{row}'] = "Reviews by Month"
        row += 1
        
        # Convert date strings to datetime and extract month
        df['date_obj'] = pd.to_datetime(df['date'])
        df['month'] = df['date_obj'].dt.strftime('%Y-%m')
        month_counts = df['month'].value_counts().sort_index()
        
        for month, count in month_counts.items():
            summary_sheet[f'A{row}'] = month
            summary_sheet[f'B{row}'] = count
            row += 1
        
        # Auto-adjust column widths
        for col in ['A', 'B']:
            max_width = 0
            for cell in summary_sheet[col]:
                if cell.value:
                    max_width = max(max_width, len(str(cell.value)))
            summary_sheet.column_dimensions[col].width = max_width + 2


if __name__ == "__main__":
    # Standalone usage example
    import yaml
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    with open("config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # Sample data for testing
    sample_reviews = [
        {
            'platform': 'TripAdvisor',
            'reviewer_name': 'John D.',
            'date': '2025-03-15',
            'rating': 4.0,
            'title': 'Great experience',
            'text': 'The food was excellent, but service was a bit slow.',
            'category': 'Food Quality',
            'sentiment': True
        },
        {
            'platform': 'Yelp',
            'reviewer_name': 'Alice S.',
            'date': '2025-02-20',
            'rating': 2.0,
            'title': '',
            'text': 'Very disappointing experience. The wait was too long and food was cold.',
            'category': 'Wait Times',
            'sentiment': False
        }
    ]
    
    exporter = ExcelExporter(config)
    exporter.export(sample_reviews)
