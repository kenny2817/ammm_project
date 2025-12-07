import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import io
import re

# 1. Data
df = pd.read_csv('ignored/results.csv')

# 2. New Data
new_data = """test_8_opl_S772_K5_N40,928.00,928,928,64.3691,64.3691,64.3691,33%
test_9_opl_S806_K20_N30,726.00,726,726,69.6201,69.6201,69.6201,33%
test_5_opl_S3279_K20_N40,1610.00,1610,1610,77.0154,77.0154,77.0154,33%"""

# Columns must match existing
columns = ["TestID","AvgCost","MinCost","MaxCost","AvgTime","MinTime","MaxTime","SuccessRate"]
df_new = pd.read_csv(io.StringIO(new_data), names=columns)

# 3. Process Original Data
def parse_testid(row):
    match = re.search(r'test_(\d+)_([a-zA-Z]+)_.*_K(\d+)_N(\d+)', row['TestID'])
    if match:
        return pd.Series({
            'TestNum': int(match.group(1)),
            'Algorithm': match.group(2).upper(),
            'K': int(match.group(3)),
            'N': int(match.group(4)),
            'Label': f"Test {match.group(1)}\n(N={match.group(4)}, K={match.group(3)})"
        })
    return pd.Series([None, None, None, None, None])

df[['TestNum', 'Algorithm', 'K', 'N', 'Label']] = df.apply(parse_testid, axis=1)

# 4. Process New Data
# We parse it similarly, but then override the Algorithm name
df_new[['TestNum', 'Algorithm', 'K', 'N', 'Label']] = df_new.apply(parse_testid, axis=1)
df_new['Algorithm'] = 'OPL (Early)'

# 5. Combine
df_final = pd.concat([df, df_new], ignore_index=True)
df_final.sort_values(by=['TestNum', 'K', 'N', 'Algorithm'], inplace=True)

# 6. Plot
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 1, figsize=(14, 12))

# Define Order
hue_order = ['GREEDY', 'GRASP', 'OPL', 'OPL (Early)']
# Define colors? Seaborn default 'viridis' or 'deep' or 'Set2' usually distinguishes 4 items well.
# Let's use a specific palette to ensure OPL and OPL (Early) look distinct but nice.
# 'tab10' is good for distinct categorical data.
palette = 'tab10'

# Plot 1: Cost
sns.barplot(
    data=df_final, 
    x='Label', 
    y='AvgCost', 
    hue='Algorithm', 
    hue_order=hue_order, 
    ax=axes[0], 
    palette=palette,
    edgecolor='black',
    errorbar=None
)
axes[0].set_title('Average Cost Comparison', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Average Cost')
axes[0].set_xlabel('')
axes[0].legend(title='Algorithm', loc='upper left', bbox_to_anchor=(1, 1))

# Plot 2: Time
sns.barplot(
    data=df_final, 
    x='Label', 
    y='AvgTime', 
    hue='Algorithm', 
    hue_order=hue_order, 
    ax=axes[1], 
    palette=palette,
    edgecolor='black',
    errorbar=None
)
axes[1].set_yscale('log')
axes[1].set_title('Average Execution Time (Log Scale)', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Time (Seconds) - Log Scale')
axes[1].set_xlabel('Test Case')
axes[1].legend(title='Algorithm', loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.savefig('ignored/results.png')