import pandas as pd # type: ignore
import re
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

# Load data
df = pd.read_csv('ignored/tuning.csv')

# Parse TestID
pattern_tuning = r'tuning_(\d+)_(\d+)_(\d+)'
pattern_baseline = r'tuning_bl_(\d+)'

def parse_row(testid):
    match = re.search(pattern_tuning, testid)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3)) / 10.0, 'tuning'
    
    match_bl = re.search(pattern_baseline, testid)
    if match_bl:
        return int(match_bl.group(1)), None, None, 'baseline'
        
    return None, None, None, None

df[['TestCase', 'Exponent', 'Alpha', 'Type']] = df['TestID'].apply(lambda x: pd.Series(parse_row(x)))

# Extract Baselines
baseline_df = df[df['Type'] == 'baseline'][['TestCase', 'AvgCost']].set_index('TestCase')
baselines = baseline_df['AvgCost'].to_dict()

# Filter for tuning data
tuning_data = df[df['Type'] == 'tuning'].copy()

# Calculate % Diff from Baseline
def calc_diff(row):
    tc = row['TestCase']
    if tc in baselines:
        base_cost = baselines[tc]
        return ((row['AvgCost'] - base_cost) / base_cost) * 100
    return None

tuning_data['CostDiffPct'] = tuning_data.apply(calc_diff, axis=1)

# Plotting
vmin = tuning_data['CostDiffPct'].min()
vmax = tuning_data['CostDiffPct'].max()

unique_cases = sorted(tuning_data['TestCase'].unique())
num_cases = len(unique_cases)

fig, axes = plt.subplots(1, num_cases, figsize=(4 * num_cases, 6), sharey=True, squeeze=False)
axes = axes.flatten()

for i, tc in enumerate(unique_cases):
    ax = axes[i]
    subset = tuning_data[tuning_data['TestCase'] == tc]
    
    # Pivot for heatmap
    pivot = subset.pivot(index='Alpha', columns='Exponent', values='CostDiffPct').sort_index(ascending=False)
    
    # Plot heatmap without green highlights
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap='RdBu_r', center=0, 
                vmin=vmin, vmax=vmax, ax=ax, cbar=(i == num_cases - 1),
                cbar_kws={'label': '% Diff from Baseline Cost'})
    
    base_val = baselines.get(tc, 'N/A')
    ax.set_title(f'Test Case {tc}')
    ax.set_xlabel('Exponent')
    if i > 0:
        ax.set_ylabel('')

plt.suptitle('Cost % Difference from Baseline across Test Cases', fontsize=16)
plt.tight_layout()
plt.savefig('multicase_comparison_no_green.png')