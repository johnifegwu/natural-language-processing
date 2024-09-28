import pandas as pd
import numpy as np

# Simulating A/B test data
np.random.seed(42)
group_a = np.random.normal(50, 10, 1000)
group_b = np.random.normal(52, 10, 1000)

# Comparing means
diff = np.mean(group_b) - np.mean(group_a)
print("Difference in means:", diff)
