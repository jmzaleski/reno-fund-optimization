import pandas as pd
import numpy as np

def calculate_tax_impact(capital_gain, province='BC'):
    # 2024 Tax rates for BC
    federal_brackets = [0, 53359, 106717, 165430, 235675]
    federal_rates = [0.15, 0.205, 0.26, 0.29, 0.33]
    bc_brackets = [0, 45654, 91310, 104835, 127299, 172602, 240716]
    bc_rates = [0.0506, 0.077, 0.105, 0.1229, 0.147, 0.168, 0.205]
    
    # Only 50% of capital gains are taxable in Canada
    taxable_gain = capital_gain * 0.5
    
    def calculate_bracket_tax(amount, brackets, rates):
        tax = 0
        remaining = amount
        for i in range(len(brackets)-1):
            bracket_size = brackets[i+1] - brackets[i]
            if remaining > bracket_size:
                tax += bracket_size * rates[i]
                remaining -= bracket_size
            else:
                tax += remaining * rates[i]
                break
        if remaining > 0:
            tax += remaining * rates[-1]
        return tax
    
    federal_tax = calculate_bracket_tax(taxable_gain, federal_brackets, federal_rates)
    provincial_tax = calculate_bracket_tax(taxable_gain, bc_brackets, bc_rates)
    
    return federal_tax + provincial_tax

def optimize_funding_mix(total_amount, stock_value, capital_gain, interest_rate, years=5):
    df = pd.DataFrame(columns=['Year', 'Stock_Sold', 'LOC_Used', 'Tax_Paid', 'Interest_Paid', 'Total_Cost'])
    
    # Create scenarios with different stock sale distributions
    scenarios = []
    step = stock_value / 10  # Test 10 different distribution patterns
    
    for first_year_sale in np.arange(0, stock_value + step, step):
        remaining = stock_value - first_year_sale
        yearly_sale = remaining / (years - 1) if years > 1 else 0
        
        scenario_cost = 0
        scenario_detail = []
        loc_balance = total_amount
        
        for year in range(years):
            if year == 0:
                stock_sold = first_year_sale
            else:
                stock_sold = min(yearly_sale, remaining)
                remaining -= stock_sold
            
            # Calculate proportional capital gain
            year_capital_gain = (stock_sold / stock_value) * capital_gain if stock_value > 0 else 0
            
            # Calculate taxes
            tax_paid = calculate_tax_impact(year_capital_gain)
            
            # Update LOC balance and calculate interest
            loc_used = total_amount - stock_sold
            interest_paid = loc_balance * interest_rate
            loc_balance = loc_used
            
            total_year_cost = tax_paid + interest_paid
            scenario_cost += total_year_cost
            
            scenario_detail.append({
                'Year': year + 1,
                'Stock_Sold': stock_sold,
                'LOC_Used': loc_used,
                'Tax_Paid': tax_paid,
                'Interest_Paid': interest_paid,
                'Total_Cost': total_year_cost
            })
            
        scenarios.append((scenario_cost, scenario_detail))
    
    # Find optimal scenario
    optimal_scenario = min(scenarios, key=lambda x: x[0])
    df = pd.DataFrame(optimal_scenario[1])
    
    return df

# Example usage
renovation_cost = 1000000
stock_value = 350000
capital_gain = 300000
interest_rate = 0.07  # 7% prime rate

result = optimize_funding_mix(
    total_amount=renovation_cost,
    stock_value=stock_value,
    capital_gain=capital_gain,
    interest_rate=interest_rate,
    years=5
)
