import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

# Standard Pricing for the lab
GPU_PRICING = {
    "T4": {"on_demand": 0.35, "spot": 0.11},
    "A100": {"on_demand": 3.67, "spot": 1.10},
    "V100": {"on_demand": 2.48, "spot": 0.74},
    "K80": {"on_demand": 0.90, "spot": 0.27}
}

# --- Exercise 8.5.1: Multi-GPU Cost Analysis ---
def analyze_multi_gpu_cost(base_time_hours, gpu_type, gpu_counts, scaling_factors=None):
    price_per_hr = GPU_PRICING.get(gpu_type, {}).get("on_demand", 0)
    
    results = []
    for count in gpu_counts:
        # Realistic scaling: efficiency drops as we add GPUs
        # e.g., 2 GPUs -> 1.8x, 4 GPUs -> 3.2x, 8 GPUs -> 5.6x
        if scaling_factors and count in scaling_factors:
            efficiency = scaling_factors[count]
        else:
            # Simple model: efficiency = 1.0 - (log2(count) * 0.1)
            efficiency = 1.0 - (np.log2(count) * 0.08) if count > 1 else 1.0
            efficiency = max(0.6, efficiency) # Floor at 60%
        
        speedup = count * efficiency
        time_hours = base_time_hours / speedup
        total_cost = time_hours * price_per_hr * count
        
        results.append({
            "gpu_count": count,
            "efficiency": efficiency,
            "time_hours": time_hours,
            "total_cost": total_cost,
            "cost_per_performance": total_cost / speedup
        })
    
    return pd.DataFrame(results)

# --- Exercise 8.5.2: Project Cost Forecasting ---
def forecast_project_cost(phases, contingency_pct=20, confidence_level=0.95):
    forecasts = []
    total_base_cost = 0
    total_uncertainty_sq = 0
    
    for p in phases:
        price = GPU_PRICING.get(p['gpu_type'], {}).get("on_demand", 0)
        base_cost = price * p['gpu_count'] * p['duration_hours']
        uncertainty_range = base_cost * p['uncertainty_pct']
        
        total_base_cost += base_cost
        # Using root sum of squares for independent uncertainties
        total_uncertainty_sq += (uncertainty_range) ** 2
        
        forecasts.append({
            "phase": p['name'],
            "base_cost": base_cost,
            "uncertainty": uncertainty_range
        })
    
    total_uncertainty = np.sqrt(total_uncertainty_sq)
    contingency = total_base_cost * (contingency_pct / 100)
    
    # Simple normal distribution approximation for confidence interval
    # 0.95 confidence level ~ 1.96 standard deviations
    z_score = 1.96 if confidence_level == 0.95 else 1.645 # 0.90
    margin = z_score * total_uncertainty
    
    return {
        "phases": pd.DataFrame(forecasts),
        "total_base_cost": total_base_cost,
        "contingency": contingency,
        "expected_total": total_base_cost + contingency,
        "lower_bound": (total_base_cost + contingency) - margin,
        "upper_bound": (total_base_cost + contingency) + margin
    }

# --- Exercise 8.5.3: Optimization Opportunity Analysis ---
def analyze_optimization_opportunities(current_config, optimization_strategies):
    price = GPU_PRICING.get(current_config['gpu_type'], {}).get("on_demand", 0)
    base_cost = price * current_config['gpu_count'] * current_config['duration_hours']
    
    results = []
    effort_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    
    for s in optimization_strategies:
        savings = base_cost * s['savings_pct']
        priority_score = s['savings_pct'] / effort_map[s['implementation_effort']]
        
        results.append({
            "strategy": s['name'],
            "potential_savings": savings,
            "savings_pct": s['savings_pct'],
            "effort": s['implementation_effort'],
            "risk": s['risk_level'],
            "priority_score": priority_score
        })
    
    df = pd.DataFrame(results).sort_values(by="priority_score", ascending=False)
    
    # Calculate cumulative savings (careful: percentages are often multiplicative not additive)
    # 1 - (1-p1)*(1-p2)...
    rem_factor = 1.0
    cumulative_pcts = []
    for p in df['savings_pct']:
        rem_factor *= (1 - p)
        cumulative_pcts.append(1 - rem_factor)
    
    df['cumulative_savings_pct'] = cumulative_pcts
    df['cumulative_savings_usd'] = df['cumulative_savings_pct'] * base_cost
    
    return df

# --- Exercise 8.5.4: Integrated Cost Dashboard ---
def create_advanced_finops_dashboard(multi_gpu, project_forecast, optimization):
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    
    # 1. Multi-GPU Cost Curve
    axes[0, 0].plot(multi_gpu['gpu_count'], multi_gpu['total_cost'], marker='o', color='blue')
    axes[0, 0].set_title("Multi-GPU Total Cost Analysis")
    axes[0, 0].set_xlabel("GPU Count")
    axes[0, 0].set_ylabel("Total Cost (USD)")
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Project Forecast
    f = project_forecast
    categories = ['Base', 'Contingency', 'Forecast Range']
    values = [f['total_base_cost'], f['contingency'], 0]
    axes[0, 1].bar(categories[:2], values[:2], color=['gray', 'orange'])
    axes[0, 1].errorbar('Forecast Range', f['expected_total'], 
                       yerr=[[f['expected_total'] - f['lower_bound']], [f['upper_bound'] - f['expected_total']]], 
                       fmt='o', color='red', capsize=10, label='95% Confidence Range')
    axes[0, 1].set_title("Project Cost Forecast")
    axes[0, 1].set_ylabel("Cost (USD)")
    axes[0, 1].legend()
    
    # 3. Optimization Strategy Priority
    axes[1, 0].barh(optimization['strategy'], optimization['priority_score'], color='green')
    axes[1, 0].set_title("Optimization Strategy Priority (Savings/Effort)")
    axes[1, 0].set_xlabel("Priority Score")
    
    # 4. Cumulative Savings Roadmap
    axes[1, 1].step(range(len(optimization)), optimization['cumulative_savings_pct'] * 100, where='post', color='purple', marker='s')
    axes[1, 1].set_title("Cumulative Savings Roadmap (%)")
    axes[1, 1].set_xlabel("Strategies Applied (Ranked)")
    axes[1, 1].set_ylabel("Total Savings (%)")
    axes[1, 1].set_ylim(0, 100)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle("Advanced GPU FinOps Dashboard", fontsize=16, fontweight='bold')
    return fig

# --- Exercise 8.5.5: Integrated Challenge Strategy ---
def solve_integrated_challenge():
    print("\n" + "="*60)
    print("CHALLENGE 8.5.5: LLM Fine-tuning Optimization Strategy")
    print("="*60)
    
    scenario = {
        "gpu_type": "A100",
        "gpu_count": 8,
        "duration_hours": 200,
        "budget": 5000
    }
    
    # 1. Baseline Cost
    base_price = GPU_PRICING["A100"]["on_demand"]
    baseline_cost = base_price * scenario['gpu_count'] * scenario['duration_hours']
    print(f"1. Baseline Cost: ${baseline_cost:,.2f}")
    
    # 2. Multi-GPU Analysis
    # Let's see if 4 GPUs is better than 8
    mgpu = analyze_multi_gpu_cost(scenario['duration_hours'] * scenario['gpu_count'], "A100", [4, 8])
    print(f"2. Multi-GPU Analysis (Total Cost):")
    print(mgpu[['gpu_count', 'total_cost', 'efficiency']])
    
    # 3. Apply Strategies
    strategies = [
        {"name": "Mixed Precision (AMP)", "savings_pct": 0.25, "implementation_effort": "LOW", "risk_level": "LOW"},
        {"name": "Spot Instances", "savings_pct": 0.60, "implementation_effort": "MEDIUM", "risk_level": "HIGH"},
        {"name": "Early Stopping", "savings_pct": 0.15, "implementation_effort": "LOW", "risk_level": "LOW"}
    ]
    opt = analyze_optimization_opportunities({"gpu_type": "A100", "gpu_count": 8, "duration_hours": 200}, strategies)
    max_savings_pct = opt['cumulative_savings_pct'].iloc[-1]
    final_forecast_base = baseline_cost * (1 - max_savings_pct)
    
    print(f"\n3. Optimization Strategy:")
    print(f"   Cumulative Savings: {max_savings_pct*100:.1f}%")
    print(f"   Forecasted Cost:    ${final_forecast_base:,.2f}")
    
    # 4. Verification
    if final_forecast_base <= scenario['budget']:
        print(f"\n[SUCCESS] SUCCESS: Forecasted cost is under budget of ${scenario['budget']}")
    else:
        print(f"\n[FAIL] FAIL: Forecasted cost exceeds budget.")

def main():
    # Execute Analysis
    print("Executing Advanced FinOps Exercises...")
    
    # 8.5.1
    df_mgpu = analyze_multi_gpu_cost(100, "A100", [1, 2, 4, 8])
    print("\n--- 8.5.1 Multi-GPU Analysis ---")
    print(df_mgpu)
    
    # 8.5.2
    phases = [
        {"name": "Data Prep", "gpu_type": "T4", "gpu_count": 1, "duration_hours": 40, "uncertainty_pct": 0.15},
        {"name": "Training", "gpu_type": "A100", "gpu_count": 4, "duration_hours": 120, "uncertainty_pct": 0.25}
    ]
    forecast = forecast_project_cost(phases)
    print("\n--- 8.5.2 Project Forecast ---")
    print(f"Expected: ${forecast['expected_total']:.2f} (Range: ${forecast['lower_bound']:.2f} - ${forecast['upper_bound']:.2f})")
    
    # 8.5.3
    current = {"gpu_type": "A100", "gpu_count": 4, "duration_hours": 120}
    strategies = [
        {"name": "AMP", "savings_pct": 0.25, "implementation_effort": "LOW", "risk_level": "LOW"},
        {"name": "Spot", "savings_pct": 0.60, "implementation_effort": "MEDIUM", "risk_level": "HIGH"}
    ]
    df_opt = analyze_optimization_opportunities(current, strategies)
    print("\n--- 8.5.3 Optimization Priority ---")
    print(df_opt[['strategy', 'priority_score', 'cumulative_savings_pct']])
    
    # 8.5.4
    fig = create_advanced_finops_dashboard(df_mgpu, forecast, df_opt)
    fig.savefig("advanced_finops_dashboard.png")
    
    # Save individual charts for submission
    # 1. Multi-GPU Scaling
    plt.figure(figsize=(10, 6))
    plt.plot(df_mgpu['gpu_count'], df_mgpu['total_cost'], marker='o')
    plt.title("Multi-GPU Total Cost")
    plt.savefig("multi_gpu_scaling.png")
    
    # 2. Project Forecast
    plt.figure(figsize=(10, 6))
    plt.bar(['Base', 'Contingency'], [forecast['total_base_cost'], forecast['contingency']])
    plt.title("Project Cost Forecast")
    plt.savefig("project_forecast.png")
    
    # 3. Optimization Roadmap
    plt.figure(figsize=(10, 6))
    plt.step(range(len(df_opt)), df_opt['cumulative_savings_pct'] * 100, where='post')
    plt.title("Optimization Savings Roadmap")
    plt.savefig("optimization_roadmap.png")
    
    print("\n--- 8.5.4 Individual charts saved for submission ---")
    
    # 8.5.5
    solve_integrated_challenge()

if __name__ == "__main__":
    main()
