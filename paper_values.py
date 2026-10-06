"""Numbers reported in the paper (single source of truth for every deliverable)."""
PAPER = {
  "n": 100, "reps": 60, "fail_threshold": 0.5,
  "standard_med_abs_err": {
      "clean":      {"RAShR": 0.033, "MM": 0.024, "RANSAC": 0.022},
      "vertical20": {"RAShR": 0.040, "MM": 0.027, "RANSAC": 0.037},
      "leverage10": {"RAShR": 0.041, "MM": 0.020, "RANSAC": 0.021}},
  # failure rates reported in the text (fractions)
  "compact": {0.36: {"RAShR": 0.00, "LMS": 0.02, "LTS": 0.23, "MM": 0.23, "RANSAC": 0.50},
              0.40: {"RAShR": 0.00, "LMS": 0.58, "LTS": 1.00, "MM": 1.00, "RANSAC": 0.77},
              0.44: {"RAShR": 0.60, "LMS": None, "LTS": None, "MM": None, "RANSAC": None},  # RAShR succeeds 40%; others >=97%
              0.46: {"RAShR": None}},  # all methods fail at 46% (paper)
  "line":    {0.46: {"RAShR": 0.00, "LMS": 0.60, "LTS": 0.93, "MM": 0.93, "RANSAC": 0.12}},
  "funnel":  {0.40: {"RAShR": 0.00, "LMS": 0.25, "LTS": 0.62, "MM": 0.60, "RANSAC": 0.05},
              0.44: {"RAShR": 0.03, "LMS": 0.83, "LTS": 1.00, "MM": 0.98, "RANSAC": 0.40},
              0.46: {"RAShR": 0.08}},
  "directions_difficult_deg": [30, -150],
  "difficult_fail_at_distance_30": {"30deg": 0.78, "-150deg": 0.75},
  "spread": {"0.05": {"RAShR": 0.0, "LMS": 0.25, "LTS": 0.98, "MM": 0.98},
             "1_or_3": "LMS, LTS, MM and RAShR all fail in at most 2% of samples"},
  "plateau_slope": 2.058,
  "fig1": {"RAShR": 2.02, "OLS": -0.53, "LMS": -0.20, "MM": -0.26, "true": 2.00},
}
