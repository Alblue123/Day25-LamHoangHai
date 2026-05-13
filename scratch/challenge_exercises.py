import requests
import json
import pandas as pd

GATEWAY_URL = "http://localhost:8000"

def print_challenge_header(num, title):
    print(f"\n--- Challenge {num}: {title} ---")

def challenge_8_5_1_spot_savings():
    print_challenge_header("8.5.1", "Calculate Potential Monthly Spot Savings")
    # Get current workloads and pricing
    workloads_resp = requests.get(f"{GATEWAY_URL}/cluster/workloads").json()
    pricing = requests.get(f"{GATEWAY_URL}/spot/pricing").json()
    
    total_batch_ondemand_cost = 0
    total_batch_spot_cost = 0
    
    # Handle both list and dict response
    workload_list = []
    if isinstance(workloads_resp, dict):
        for w_id, w_data in workloads_resp.items():
            if isinstance(w_data, dict):
                w_data['workload_id'] = w_id
                workload_list.append(w_data)
            else:
                workload_list.append({'workload_id': w_id})
    else:
        workload_list = workloads_resp

    # Simulate for a month (720 hours)
    for wl in workload_list:
        # Assuming 'train' or 'batch' in ID means it can be spot
        w_id = wl.get('workload_id', '')
        if 'train' in w_id or 'batch' in w_id:
            gpu_type = wl.get('gpu_type_assigned', 'T4')
            if gpu_type in pricing:
                on_demand_rate = pricing[gpu_type]['on_demand_price']
                spot_rate = pricing[gpu_type]['current_spot_price']
                
                total_batch_ondemand_cost += on_demand_rate * 720
                total_batch_spot_cost += spot_rate * 720
                
    savings = total_batch_ondemand_cost - total_batch_spot_cost
    print(f"Current Monthly Batch On-Demand: ${total_batch_ondemand_cost:.2f}")
    print(f"Current Monthly Batch Spot:      ${total_batch_spot_cost:.2f}")
    print(f"Potential Monthly Savings:       ${savings:.2f}")

def challenge_8_5_2_gpu_availability():
    print_challenge_header("8.5.2", "GPU Spot Availability Check")
    def is_gpu_available_on_spot(gpu_type):
        pricing = requests.get(f"{GATEWAY_URL}/spot/pricing").json()
        if gpu_type in pricing:
            availability = pricing[gpu_type]['availability']
            return availability == 'high'
        return False

    for gpu in ['T4', 'A100', 'V100']:
        available = is_gpu_available_on_spot(gpu)
        status = "HIGH" if available else "LOW/MED"
        print(f"GPU {gpu:<5} Spot Availability: {status}")

def challenge_8_5_3_node_efficiency():
    print_challenge_header("8.5.3", "Node Efficiency Score")
    nodes = requests.get(f"{GATEWAY_URL}/cluster/nodes").json()
    
    for node_id, gpus in nodes.items():
        # Score = (Avg Util * 0.7) + (Memory Util * 0.3)
        total_util = sum(g['utilization'] for g in gpus) / len(gpus)
        total_mem = sum(g['memory_used_gb'] / g['memory_total_gb'] for g in gpus) / len(gpus) * 100
        
        efficiency_score = (total_util * 0.7) + (total_mem * 0.3)
        print(f"Node {node_id}: Efficiency Score = {efficiency_score:.1f}/100")

def challenge_8_5_4_budget_alert():
    print_challenge_header("8.5.4", "Budget Alert Simulation")
    MONTHLY_BUDGET = 50.0  # Example low budget
    summary = requests.get(f"{GATEWAY_URL}/billing/summary").json()
    total_spend = summary['total_cost_usd']
    
    print(f"Monthly Budget: ${MONTHLY_BUDGET:.2f}")
    print(f"Current Spend:  ${total_spend:.4f}")
    
    if total_spend > MONTHLY_BUDGET:
        print("[ALERT] ALERT: Budget Exceeded!")
    elif total_spend > MONTHLY_BUDGET * 0.8:
        print("[WARNING] WARNING: 80% of budget reached.")
    else:
        print("[OK] Spend within budget.")

def challenge_8_5_5_exec_summary():
    print_challenge_header("8.5.5", "FinOps Executive Summary")
    summary = requests.get(f"{GATEWAY_URL}/billing/summary").json()
    metrics = requests.get(f"{GATEWAY_URL}/cluster/metrics").json()
    waste = requests.get(f"{GATEWAY_URL}/cost/waste-report").json()
    
    print("==========================================")
    print("      FINOPS EXECUTIVE SUMMARY")
    print("==========================================")
    print(f"Total Spend (Real-time):   ${summary['total_cost_usd']:.4f}")
    print(f"Cluster Utilization:       {metrics['avg_utilization']:.1f}%")
    print(f"Cost Waste (Potential):    {waste['avg_waste_pct']:.1f}%")
    print(f"Est. Monthly Savings:      ${waste['potential_monthly_savings']:.2f}")
    print("------------------------------------------")
    print("Top Recommendation: Move training jobs to Spot.")
    print("==========================================")

def main():
    print("Running Part 8.5: Challenge Exercises Implementation")
    challenge_8_5_1_spot_savings()
    challenge_8_5_2_gpu_availability()
    challenge_8_5_3_node_efficiency()
    challenge_8_5_4_budget_alert()
    challenge_8_5_5_exec_summary()

if __name__ == "__main__":
    main()
