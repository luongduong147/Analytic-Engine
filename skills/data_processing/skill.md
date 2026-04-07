# Skill: Data Processing Pipeline

## Overview
This skill provides guidance for processing and transforming data using Python pandas.

## When to Use
- When user needs to clean, transform, or aggregate data
- When performing data preprocessing for analysis
- When handling missing values or outliers

## Data Processing Patterns

### Loading Data
```python
import pandas as pd

# From CSV
df = pd.read_csv('data.csv')

# From Excel
df = pd.read_excel('data.xlsx')

# From database (via semantic actions)
df = fetch_data('sales_table')
```

### Data Cleaning
```python
# Drop duplicates
df = df.drop_duplicates()

# Fill missing values
df = df.fillna(0)  # or df.fillna(method='ffill')

# Remove outliers
df = df[(df['value'] < df['value'].quantile(0.99))]
```

### Transformation
```python
# Add computed column
df['total'] = df['price'] * df['quantity']

# Group and aggregate
summary = df.groupby('category').agg({'sales': 'sum', 'quantity': 'mean'})

# Pivot table
pivot = df.pivot_table(values='sales', index='region', columns='quarter')
```

### Filtering
```python
# Filter by condition
filtered = df[df['sales'] > 1000]

# Multiple conditions
filtered = df[(df['region'] == 'North') & (df['sales'] > 1000)]

# String matching
filtered = df[df['product'].str.contains('premium', case=False)]
```

## Best Practices
1. Always validate data after loading
2. Document transformations applied
3. Preserve original data before modifying
4. Use meaningful column names