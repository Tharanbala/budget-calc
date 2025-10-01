import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Monthly Budget Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better mobile responsiveness
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'income_sources' not in st.session_state:
    st.session_state.income_sources = []

# Header
st.markdown('<div class="main-header">💰 Monthly Budget Calculator</div>', unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("📊 Financial Inputs")
    
    # Income Section
    st.subheader("💵 Income Sources")
    income_name = st.text_input("Income Source Name", placeholder="e.g., Salary, Freelance")
    income_amount = st.number_input("Amount ($)", min_value=0.0, step=100.0, key="income_input")
    
    if st.button("➕ Add Income"):
        if income_name and income_amount > 0:
            st.session_state.income_sources.append({
                'name': income_name,
                'amount': income_amount
            })
            st.success(f"Added {income_name}!")
            st.rerun()
    
    st.divider()
    
    # Expenses Section
    st.subheader("💳 Monthly Expenses")
    expense_categories = [
        "Housing (Rent/Mortgage)",
        "Utilities",
        "Transportation",
        "Food & Groceries",
        "Insurance",
        "Debt Payments",
        "Entertainment",
        "Subscriptions",
        "Healthcare",
        "Savings",
        "Other"
    ]
    
    expense_category = st.selectbox("Category", expense_categories)
    expense_name = st.text_input("Expense Name", placeholder="e.g., Rent, Netflix")
    expense_amount = st.number_input("Amount ($)", min_value=0.0, step=10.0, key="expense_input")
    expense_priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Critical"])
    
    if st.button("➕ Add Expense"):
        if expense_name and expense_amount > 0:
            st.session_state.expenses.append({
                'category': expense_category,
                'name': expense_name,
                'amount': expense_amount,
                'priority': expense_priority
            })
            st.success(f"Added {expense_name}!")
            st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear All Data"):
        st.session_state.expenses = []
        st.session_state.income_sources = []
        st.rerun()

# Main content area
col1, col2, col3 = st.columns(3)

# Calculate totals
total_income = sum(item['amount'] for item in st.session_state.income_sources)
total_expenses = sum(item['amount'] for item in st.session_state.expenses)
remaining_balance = total_income - total_expenses

# Display key metrics
with col1:
    st.metric("💰 Total Income", f"${total_income:,.2f}")

with col2:
    st.metric("💳 Total Expenses", f"${total_expenses:,.2f}")

with col3:
    delta_color = "normal" if remaining_balance >= 0 else "inverse"
    st.metric("💵 Remaining Balance", f"${remaining_balance:,.2f}", 
              delta=f"{(remaining_balance/total_income*100):.1f}% of income" if total_income > 0 else "N/A")

st.divider()

# Main dashboard content
if total_income == 0 and len(st.session_state.expenses) == 0:
    st.info("👈 Start by adding your income sources and monthly expenses using the sidebar!")
else:
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Budget Breakdown", "📊 Visualizations", "💡 Recommendations", "📝 Details"])
    
    with tab1:
        st.subheader("Budget Breakdown")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("**Income Sources**")
            if st.session_state.income_sources:
                income_df = pd.DataFrame(st.session_state.income_sources)
                for idx, row in income_df.iterrows():
                    st.write(f"• {row['name']}: ${row['amount']:,.2f}")
            else:
                st.write("No income sources added yet")
        
        with col_b:
            st.write("**Expense Summary by Priority**")
            if st.session_state.expenses:
                expenses_df = pd.DataFrame(st.session_state.expenses)
                priority_summary = expenses_df.groupby('priority')['amount'].sum().sort_values(ascending=False)
                for priority, amount in priority_summary.items():
                    percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                    st.write(f"• {priority}: ${amount:,.2f} ({percentage:.1f}%)")
            else:
                st.write("No expenses added yet")
    
    with tab2:
        st.subheader("Financial Visualizations")
        
        if st.session_state.expenses:
            expenses_df = pd.DataFrame(st.session_state.expenses)
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Pie chart by category
                category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
                fig_pie = px.pie(category_summary, values='amount', names='category', 
                                title='Expenses by Category',
                                hole=0.4)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_chart2:
                # Bar chart by priority
                priority_summary = expenses_df.groupby('priority')['amount'].sum().reset_index()
                priority_order = ['Critical', 'High', 'Medium', 'Low']
                priority_summary['priority'] = pd.Categorical(priority_summary['priority'], 
                                                              categories=priority_order, 
                                                              ordered=True)
                priority_summary = priority_summary.sort_values('priority')
                
                fig_bar = px.bar(priority_summary, x='priority', y='amount',
                               title='Expenses by Priority',
                               color='priority',
                               color_discrete_map={
                                   'Critical': '#d62728',
                                   'High': '#ff7f0e',
                                   'Medium': '#2ca02c',
                                   'Low': '#1f77b4'
                               })
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Income vs Expenses gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=total_expenses,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Expenses vs Income"},
                delta={'reference': total_income},
                gauge={
                    'axis': {'range': [None, max(total_income * 1.2, total_expenses * 1.2)]},
                    'bar': {'color': "darkred" if total_expenses > total_income else "darkgreen"},
                    'steps': [
                        {'range': [0, total_income * 0.5], 'color': "lightgreen"},
                        {'range': [total_income * 0.5, total_income * 0.8], 'color': "yellow"},
                        {'range': [total_income * 0.8, total_income], 'color': "orange"},
                        {'range': [total_income, total_income * 1.5], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': total_income
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with tab3:
        st.subheader("💡 Budget Recommendations")
        
        if total_income > 0:
            # Calculate recommended allocations (50/30/20 rule)
            needs_budget = total_income * 0.50
            wants_budget = total_income * 0.30
            savings_budget = total_income * 0.20
            
            st.write("### 50/30/20 Budget Rule")
            st.write("A popular budgeting guideline:")
            
            rec_col1, rec_col2, rec_col3 = st.columns(3)
            
            with rec_col1:
                st.info(f"""
                **50% - Needs**  
                ${needs_budget:,.2f}
                
                Essential expenses like housing, utilities, food, transportation
                """)
            
            with rec_col2:
                st.info(f"""
                **30% - Wants**  
                ${wants_budget:,.2f}
                
                Non-essential expenses like entertainment, dining out, hobbies
                """)
            
            with rec_col3:
                st.info(f"""
                **20% - Savings**  
                ${savings_budget:,.2f}
                
                Emergency fund, retirement, debt repayment, investments
                """)
            
            st.divider()
            
            # Personalized recommendations
            st.write("### Your Budget Analysis")
            
            if remaining_balance < 0:
                st.error(f"""
                ⚠️ **Budget Deficit: ${abs(remaining_balance):,.2f}**
                
                Your expenses exceed your income. Consider:
                - Reviewing and reducing non-essential expenses
                - Looking for ways to increase income
                - Prioritizing critical expenses only
                """)
            elif remaining_balance < savings_budget:
                st.warning(f"""
                ⚠️ **Low Savings Rate**
                
                You have ${remaining_balance:,.2f} remaining, which is less than the recommended 20% (${savings_budget:,.2f}).
                
                Try to reduce expenses or increase income to meet your savings goals.
                """)
            else:
                st.success(f"""
                ✅ **Good Budget Health!**
                
                You have ${remaining_balance:,.2f} remaining after expenses.
                
                Consider allocating this towards:
                - Emergency fund (3-6 months of expenses)
                - Retirement savings
                - Investment accounts
                - Debt repayment
                """)
            
            # Expense ratio analysis
            if total_expenses > 0:
                expense_ratio = (total_expenses / total_income) * 100
                st.write(f"**Your expense ratio:** {expense_ratio:.1f}% of income")
                
                if expense_ratio > 80:
                    st.warning("Your expenses are consuming more than 80% of your income. Try to reduce non-essential spending.")
                elif expense_ratio <= 50:
                    st.success("Great job! You're spending 50% or less of your income.")
        else:
            st.info("Add your income sources to see personalized recommendations!")
    
    with tab4:
        st.subheader("Detailed Breakdown")
        
        col_detail1, col_detail2 = st.columns(2)
        
        with col_detail1:
            st.write("**Income Details**")
            if st.session_state.income_sources:
                income_df = pd.DataFrame(st.session_state.income_sources)
                st.dataframe(income_df, use_container_width=True, hide_index=True)
                
                if st.button("📥 Download Income CSV"):
                    csv = income_df.to_csv(index=False)
                    st.download_button(
                        label="Download",
                        data=csv,
                        file_name=f"income_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("No income data available")
        
        with col_detail2:
            st.write("**Expense Details**")
            if st.session_state.expenses:
                expenses_df = pd.DataFrame(st.session_state.expenses)
                st.dataframe(expenses_df, use_container_width=True, hide_index=True)
                
                if st.button("📥 Download Expenses CSV"):
                    csv = expenses_df.to_csv(index=False)
                    st.download_button(
                        label="Download",
                        data=csv,
                        file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("No expense data available")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <small>💡 Tip: Use the sidebar to add your income and expenses. The dashboard will automatically update with insights and recommendations.</small>
    </div>
""", unsafe_allow_html=True)