import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Global Constants
CSV_FILE = 'bookkeeping_data.csv'
CATEGORY_LIST = ['Salary', 'Other_Income', 'Eat', 'Wear', 'Transportation', 
                 'Supermarket', 'Groceries', 'Living', 'Water/Electricity', 'Others']
PAYMENT_LIST = ['Esun-Ubear', 'CTBC-LinePay', 'SC-LineBank', 'Cash', 'Post']

# Define a consistent color palette for categories
CATEGORY_COLORS = {
    'Salary': '#D4CEFF',
    'Other_Income': '#E8DEFF',
    'Eat': '#2E8B57',
    'Wear': '#439A6D',
    'Transportation': '#58A983',
    'Supermarket': '#6DB899',
    'Groceries': '#82C7AF',
    'Living': '#97D6C5',
    'Water/Electricity': '#ACD5DB',
    'Others': '#C1E4F1'
}

# Define colors for Income/Expense types
TYPE_COLORS = {
    'Income': '#2E8B57',  # Teal color for income
    'Expense': '#EBFFFF'  # Red color for expense
}

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Bookkeeping App")

# ---Database Utility Functions---
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
        df['Date'] = pd.to_datetime(df['Date'])
        df['Amount'] = df['Amount'].astype(int)
        return df
    else:
        return pd.DataFrame(columns=['Date', 'Category', 'Payment', 'Amount', 'Details'])

def save_data(data):
    data_to_save = data.copy()
    data_to_save['Date'] = data_to_save['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    data_to_save.to_csv(CSV_FILE, index=False)

def add_new_entry(data, date, category, payment, amount, details):
    formatted_date = pd.to_datetime(date)
    new_entry = pd.DataFrame({
        'Date': [formatted_date],
        'Category': [category],
        'Payment': [payment],
        'Amount': [int(amount)],
        'Details': [details]
    })
    return pd.concat([data, new_entry], ignore_index=True)

def filter_data_by_date(data, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return data[(data['Date'] >= start_date) & 
                (data['Date'] <= end_date)]

# ---Visualization Functions---
def display_pivot_table(data):
    # Create a copy of data to avoid SettingWithCopyWarning
    data_copy = data.copy()
    data_copy['Month-Year'] = pd.to_datetime(data_copy['Date']).dt.to_period('M')
    pivot_table = data_copy.pivot_table(
        index='Category',
        columns='Month-Year',
        values='Amount',
        aggfunc='sum',
        fill_value=0
    )

    pivot_table.columns = pivot_table.columns.strftime('%b-%y')
    ordered_categories = CATEGORY_LIST
    pivot_table = pivot_table.reindex(ordered_categories)
    st.table(pivot_table)
    csv = pivot_table.to_csv().encode('utf-8')
    st.download_button("Download Pivot Table as CSV", data=csv, file_name='pivot_table.csv', mime='text/csv')

def display_expense_charts(data):
    """
    Displays the monthly expenses by category and category summary charts in two columns.
    Includes checkboxes to filter categories for both charts.
    """
    # Create a copy of data to avoid SettingWithCopyWarning
    data_copy = data.copy()
    
    # Define expense categories (excluding income categories)
    expense_categories = [cat for cat in CATEGORY_LIST if cat not in ['Salary', 'Other_Income']]
    
    # Add category filter using checkboxes
    st.subheader("Category Filters")
    
    # Create a columns layout for the checkboxes (4 columns to fit all categories)
    filter_cols = st.columns(4)
    
    # Dictionary to store the checkbox states
    selected_categories = {}
    
    # Create checkboxes for each category distributed across the columns
    for i, category in enumerate(expense_categories):
        col_idx = i % 4  # Distribute across 4 columns
        with filter_cols[col_idx]:
            selected_categories[category] = st.checkbox(category, value=True)
    
    # Filter data based on selected categories
    filtered_categories = [cat for cat in expense_categories if selected_categories[cat]]
    
    if not filtered_categories:
        st.warning("Please select at least one category to display charts.")
        return
    
    # Apply category filter to data - create explicit copy to avoid the warning
    filtered_data = data_copy[data_copy['Category'].isin(filtered_categories)].copy()
    
    # Group and summarize data for filtered view
    category_summary = filtered_data.groupby('Category')['Amount'].sum().reset_index()
    
    # Create proper datetime objects for month-year to ensure chronological sorting
    filtered_data.loc[:, 'Month-Year-Obj'] = pd.to_datetime(filtered_data['Date']).dt.to_period('M').dt.to_timestamp()
    filtered_data.loc[:, 'Month-Year'] = filtered_data['Month-Year-Obj'].dt.strftime('%b-%y')
    
    # Sort by the actual datetime objects, then summarize
    monthly_category_summary = filtered_data.sort_values('Month-Year-Obj').groupby(['Month-Year', 'Category'])['Amount'].sum().reset_index()
    
    # Get unique month-years in chronological order
    sorted_months = filtered_data.sort_values('Month-Year-Obj')['Month-Year'].unique()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Monthly Expenses by Category')
        
        if monthly_category_summary.empty:
            st.info("No data available for selected categories")
        else:
            # Create the bar chart with fixed color scheme and proper ordering
            fig = px.bar(
                monthly_category_summary, 
                x='Month-Year', 
                y='Amount', 
                color='Category',
                title='Monthly Expense Distribution by Category', 
                barmode='stack',
                color_discrete_map={cat: CATEGORY_COLORS[cat] for cat in filtered_categories},
                category_orders={
                    "Category": filtered_categories,
                    "Month-Year": sorted_months
                }
            )
            st.plotly_chart(fig)
        
    with col2:
        st.subheader('Category Summary')
        
        if category_summary.empty:
            st.info("No data available for selected categories")
        else:
            # Create the pie chart with fixed color scheme
            fig = px.pie(
                category_summary, 
                values='Amount', 
                names='Category', 
                title='Category Distribution',
                color='Category',
                color_discrete_map={cat: CATEGORY_COLORS[cat] for cat in filtered_categories},
                category_orders={"Category": filtered_categories}
            )
            st.plotly_chart(fig)

def display_income_expense_chart(data):
    """
    Displays the monthly income vs expenses chart.
    """
    # Create a copy of data to avoid SettingWithCopyWarning
    data_copy = data.copy()
    
    # Create proper datetime objects for month-year to ensure chronological sorting
    data_copy.loc[:, 'Month-Year-Obj'] = pd.to_datetime(data_copy['Date']).dt.to_period('M').dt.to_timestamp()
    data_copy.loc[:, 'Month-Year'] = data_copy['Month-Year-Obj'].dt.strftime('%b-%y')
    
    # Set income/expense type
    data_copy['Type'] = data_copy['Category'].apply(
        lambda x: 'Income' if x in ['Salary', 'Other_Income'] else 'Expense'
    )
    
    # Sort by the actual datetime objects, then summarize
    monthly_income_expense = data_copy.sort_values('Month-Year-Obj').groupby(['Month-Year', 'Type'])['Amount'].sum().reset_index()
    
    # Get unique month-years in chronological order
    sorted_months = data_copy.sort_values('Month-Year-Obj')['Month-Year'].unique()
    
    st.subheader('Monthly Income vs Expenses')
    
    # Create the income/expense bar chart with fixed color scheme and proper ordering
    fig = px.bar(
        monthly_income_expense, 
        x='Month-Year', 
        y='Amount', 
        color='Type',
        title='Monthly Income vs Expenses', 
        barmode='group',
        color_discrete_map=TYPE_COLORS,
        category_orders={
            'Type': ['Income', 'Expense'],
            'Month-Year': sorted_months
        },
        text='Amount'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="Month-Year",
        yaxis_title="Amount",
        legend_title="Type"
    )
    st.plotly_chart(fig)

def display_recent_entries(data):
    """Display the five most recent entries added to the bookkeeping app."""
    st.subheader('Recent Entries')
    
    if data.empty:
        st.info('No entries available.')
        return
        
    # Sort data by date in descending order and get the 5 most recent entries
    recent_data = data.sort_values('Date', ascending=False).head(5)
    
    # Format date for display - create a copy to avoid warning
    recent_data_display = recent_data.copy()
    recent_data_display['Date'] = recent_data_display['Date'].dt.strftime('%Y-%m-%d')
    
    # Display in a nice table with better column formatting
    st.dataframe(
        recent_data_display[['Date', 'Category', 'Payment', 'Amount', 'Details']],
        column_config={
            "Date": "Date",
            "Category": "Category",
            "Payment": "Payment Method",
            "Amount": st.column_config.NumberColumn("Amount", format="%d"),
            "Details": "Description"
        },
        hide_index=True
    )

# ---Main Application---
def main():
    st.title('Bookkeeping App')
    
    # Load data
    data = load_data()
    
    # Sidebar Input Form
    st.sidebar.header('Add New Entry')
    date = st.sidebar.date_input('Date')
    category = st.sidebar.selectbox('Category', CATEGORY_LIST)
    amount = st.sidebar.number_input('Amount', min_value=0, step=1, format="%d")
    payment = st.sidebar.selectbox('Payment', PAYMENT_LIST)
    details = st.sidebar.text_area('Details')
    add_entry = st.sidebar.button('Add Entry')
    st.sidebar.markdown('---')
    
    if add_entry:
        data = add_new_entry(data, date, category, payment, amount, details)
        save_data(data)
        st.sidebar.success('Entry added successfully!')
    
    if not data.empty:
        # Date Range Filter - Moved earlier so filtered data is available for all visualizations
        st.sidebar.header('Filter Data by Date Range')
        min_date = pd.to_datetime(data['Date']).min()
        max_date = pd.to_datetime(data['Date']).max()
        start_date = st.sidebar.date_input('Start Date', value=min_date)
        end_date = st.sidebar.date_input('End Date', value=max_date)
        
        filtered_data = filter_data_by_date(data, start_date, end_date)
        
        if not filtered_data.empty:
            # Display Pivot Table with filtered data
            st.subheader('Data Summary')
            date_range_text = f"({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
            st.caption(f"Showing data for selected date range {date_range_text}")
            display_pivot_table(filtered_data)
            
            # Display Charts with filtered data - now using separate functions
            display_expense_charts(filtered_data)
            display_income_expense_chart(filtered_data)
            
            # Display recent entries (always show the most recent 5 entries from the full dataset)
            display_recent_entries(data)
        else:
            st.warning('No data available for the selected date range.')
    else:
        st.info('No data available. Please add some entries to get started.')

if __name__ == "__main__":
    main()