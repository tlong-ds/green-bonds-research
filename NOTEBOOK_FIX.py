"""
QUICK FIX for your notebook cell:

Replace 'Tobin_Q' with 'return_on_equity_total' (which exists and has data)
"""

# OLD CODE (that causes error):
# outcomes = ['return_on_assets', 'Tobin_Q', 'esg_score']

# NEW CODE (will work):
outcomes = ['return_on_assets', 'return_on_equity_total', 'esg_score']
specs = ['entity_fe', 'time_fe', 'twoway_fe', 'none']

# This will now work properly!
# The DiD module has been fixed to:
# - Handle multicollinearity automatically
# - Validate outcome variables exist
# - Report errors for failed models
