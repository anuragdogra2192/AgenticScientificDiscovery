# Analysis Agent 📊

The Analysis Agent evaluates experimental results, performs statistical significance testing, interprets findings against hypotheses, and contextualizes results for the research narrative. It transforms raw experimental data into validated scientific findings.

## Features

### 📈 Data Assessment
- **Data Quality Checks**: Missing values, outliers, completeness
- **Descriptive Statistics**: Mean, median, SD, skewness, kurtosis
- **Assumption Testing**: Normality, homogeneity, independence, linearity
- **Quality Issues Report**: Identification and severity assessment

### 🔬 Statistical Testing
- **Parametric Tests**:
  * Independent samples t-test
  * Paired samples t-test
  * ANOVA with post-hoc tests
  * Linear regression with diagnostics
  
- **Non-Parametric Tests**:
  * Mann-Whitney U test
  * Wilcoxon signed-rank test
  * Kruskal-Wallis H test
  * Chi-square test

- **Advanced Analyses**:
  * Secondary outcome analysis
  * Subgroup analysis
  * Mediation analysis
  * Sensitivity analyses

### 📊 Effect Sizes & Confidence Intervals
- **Continuous Outcomes**: Cohen's d, η², ω², R²
- **Categorical Outcomes**: Cramér's V, φ, odds ratio
- **95% Confidence Intervals** with alternative levels
- **Effect Size Interpretation**: Negligible to very large

### 💡 Finding Extraction
- **Primary Findings**: Main hypothesis test results
- **Secondary Findings**: Additional discovered effects
- **Anomalies**: Unexpected patterns or contradictions
- **Consistency Assessment**: Agreement with hypotheses

### 📚 Literature Contextualization
- **Effect Size Comparison**: Against similar studies
- **Direction Matching**: Does result align with theory?
- **Novelty Assessment**: What's new here?
- **Generalization Evaluation**: When does this apply?

### 🎯 Implications & Recommendations
- **Practical Implications**: Real-world applications
- **Theoretical Implications**: Theory advancement
- **Limitations**: What we can't conclude
- **Future Directions**: Next research steps
- **Actionable Recommendations**: What to do next

### 📋 Comprehensive Reporting
- **Structured Analysis Report**: JSON, Markdown, HTML
- **Executive Summary**: For decision-makers
- **Technical Details**: For methodologists
- **Visualization Specs**: Diagrams and figures needed

## Installation

```bash
# Dependencies already included
pip install -r ../../requirements.txt
```

## Usage

### Basic Result Analysis

```python
import asyncio
from agents.analysis_agent import AnalysisAgent

async def analyze_results():
    agent = AnalysisAgent()
    
    # Prepare your results data
    results = {
        "n": 120,
        "simulated_effect_size": 0.55,
        "missing_count": 2,
        "outlier_count": 1,
        "variables": {
            "outcome": [4.2, 5.1, 4.9, ...],  # Your data
            "group": [0, 0, 0, ..., 1, 1, 1, ...],  # Group assignments
        }
    }
    
    # Design and hypothesis from previous phases
    design = {
        "id": "exp_001",
        "title": "Treatment vs Control",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }
    
    hypothesis = {
        "id": "hyp_001",
        "title": "Treatment improves outcomes",
    }
    
    # Analyze
    report = await agent.analyze_results(design, hypothesis, results)
    
    print(f"Hypothesis Confirmed: {report.hypothesis_confirmed}")
    print(f"Effect Size: {report.primary_finding.effect_size:.3f}")
    print(f"P-value: {report.primary_analysis.p_value:.4f}")
    
    await agent.close()

asyncio.run(analyze_results())
```

### Examine Statistical Results

```python
# Primary analysis details
print(f"Test Used: {report.primary_analysis.test_name.value}")
print(f"Test Statistic: {report.primary_analysis.test_statistic:.3f}")
print(f"P-value: {report.primary_analysis.p_value:.4f}")
print(f"Significance: {report.primary_analysis.significance_level.value}")

# Effect size interpretation
print(f"Effect Size: {report.primary_analysis.effect_size:.3f}")
print(f"Interpretation: {report.primary_analysis.effect_size_interpretation.value}")

# Confidence interval
ci = report.primary_analysis.confidence_interval
print(f"95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
```

### Review Assumptions

```python
print("Assumptions Checked:")
for assumption, met in report.assumptions_checked.items():
    status = "✓" if met else "✗"
    print(f"  {status} {assumption}")

if report.violated_assumptions:
    print("\nViolated Assumptions:")
    for violation in report.violated_assumptions:
        print(f"  ⚠ {violation}")
```

### Examine Findings

```python
print(f"Total Findings: {len(report.findings)}")

# Primary finding
pf = report.primary_finding
print(f"\nPrimary Finding: {pf.title}")
print(f"  Effect Size: {pf.effect_size:.3f}")
print(f"  Hypothesis: {pf.consistency_with_hypothesis}")
print(f"  Practical Significance: {pf.practical_significance}")

# All findings
for finding in report.findings:
    print(f"\n{finding.title}")
    print(f"  Type: {finding.finding_type}")
    print(f"  Evidence: {finding.supporting_evidence}")
```

### Get Implications

```python
print("Practical Implications:")
for impl in report.practical_implications:
    print(f"  • {impl}")

print("\nTheoretical Implications:")
for impl in report.theoretical_implications:
    print(f"  • {impl}")

print("\nFuture Research:")
for future in report.future_research_directions:
    print(f"  • {future}")
```

### Generate Summary

```python
summary = await agent.generate_analysis_summary(report)
print(summary)

# Save to file
with open("analysis_summary.md", "w") as f:
    f.write(summary)
```

## Statistical Tests Guide

### When to Use Each Test

| Hypothesis | Data | Groups | Test |
|-----------|------|--------|------|
| Difference in means | Continuous | 2 | t-test |
| Difference in means | Continuous | 3+ | ANOVA |
| Same participants | Continuous | 2 | Paired t-test |
| Non-normal data | Continuous | 2 | Mann-Whitney U |
| Non-normal data | Continuous | 3+ | Kruskal-Wallis |
| Paired non-normal | Continuous | 2 | Wilcoxon |
| Categories | Categorical | Any | Chi-square |

### T-Test Example

```python
report.primary_analysis.test_name == StatisticalTest.T_TEST
# Gives:
# - t-statistic
# - p-value
# - Cohen's d effect size
# - 95% confidence interval
# - Assumption checks (normality, homogeneity)
```

### ANOVA Example

```python
report.primary_analysis.test_name == StatisticalTest.ANOVA
# Gives:
# - F-statistic
# - p-value
# - Eta-squared effect size
# - Post-hoc pairwise comparisons (Tukey, Bonferroni)
# - Assumption checks
```

## Effect Size Interpretation

### Cohen's d (Continuous Outcomes)
| Effect Size | Cohen's d |
|-------------|-----------|
| Negligible | < 0.1 |
| Small | 0.1 - 0.3 |
| Medium | 0.3 - 0.5 |
| Large | 0.5 - 0.8 |
| Very Large | > 0.8 |

### Eta-squared (ANOVA)
| Effect Size | η² |
|-------------|-----|
| Small | 0.01 |
| Medium | 0.06 |
| Large | 0.14 |

### Odds Ratio (Categorical)
| Effect Size | OR |
|-------------|-----|
| Small | ~1.5 |
| Medium | ~3.5 |
| Large | ~9.0 |

## Hypothesis Interpretation Rules

### Confirmation Criteria
- **Strong**: p < 0.05 AND effect size ≥ 0.5 AND direction correct
- **Moderate**: p < 0.05 AND direction correct
- **Weak**: Direction correct but p > 0.05
- **Not Confirmed**: Direction incorrect or p > 0.10

### Consistency Assessment
- **Confirms**: Results strongly support hypothesis
- **Qualifies**: Results support with conditions/boundaries
- **Contradicts**: Results oppose hypothesis
- **Neutral**: No clear relationship to hypothesis

## Data Quality Standards

### Acceptable Missing Data
- < 5%: Minimal impact
- 5-10%: Manageable with methods
- > 10%: Requires special handling

### Outlier Detection
- Flagged if > 3 SD from mean
- Influential if > 3 Cook's distance
- Report with/without outliers

### Sample Size Adequacy
- n > 30: Large-sample assumptions justified
- n = 20-30: Borderline; check assumptions
- n < 20: Small sample; consider limitations

## Visualization Planning

The agent recommends visualizations for:
- **Descriptive**: Means, distributions, relationships
- **Inferential**: Confidence intervals, significance
- **Comparative**: Effect sizes, group differences
- **Temporal**: Trends, trajectories, learning curves

## Configuration

Edit `config.yaml` to customize:

**Alpha level**:
```yaml
statistical_tests:
  alpha: 0.05  # Default significance level
```

**Confidence interval level**:
```yaml
confidence_intervals:
  default_level: 0.95  # 95% CI
```

**Effect size thresholds**:
```yaml
effect_sizes:
  continuous_outcomes:
    cohens_d:
      small: 0.2
      medium: 0.5
      large: 0.8
```

## Running Examples

```bash
# Run all 9 examples
python agents/analysis_agent/examples.py

# Run specific example
python -c "
import asyncio
from agents.analysis_agent.examples import example_1_basic_analysis
asyncio.run(example_1_basic_analysis())
"
```

## Output Formats

### JSON Export
```python
report_dict = report.to_dict()
# Contains all analysis information in structured format
```

### Markdown Report
```python
summary = await agent.generate_analysis_summary(report)
# Human-readable narrative report
```

## Integration with Other Agents

### Input from Experiment Agent
```python
design = await exp_agent.design_experiment(hypothesis)
# Specifies what to measure and analyze
```

### Output for Report Agent
```python
report = await ana_agent.analyze_results(design, hypothesis, results)
# Contains all findings and implications for paper
```

## Common Patterns

### Pattern 1: Quick Hypothesis Check
```python
report = await agent.analyze_results(design, hypothesis, results)
print(f"Confirmed: {report.hypothesis_confirmed}")
print(f"Effect: {report.primary_finding.effect_size:.3f}")
```

### Pattern 2: Full Analysis Export
```python
report = await agent.analyze_results(design, hypothesis, results)
summary = await agent.generate_analysis_summary(report)

with open("report.md", "w") as f:
    f.write(summary)

with open("report.json", "w") as f:
    json.dump(report.to_dict(), f, indent=2)
```

### Pattern 3: Assumption-Based Test Selection
```python
# Agent automatically selects parametric vs non-parametric
# based on assumption violations
report = await agent.analyze_results(design, hypothesis, results)
# Uses t-test if assumptions met, Mann-Whitney U if not
```

## Troubleshooting

### Very small p-value reported
- Normal for large samples with small effects
- Check effect size for practical significance
- Don't assume statistical = practical significance

### Missing statistical significance but effect exists
- May be insufficient power
- Consider sample size in context
- Discuss in limitations

### Violated assumptions
- Agent automatically selects robust alternatives
- Report both parametric and non-parametric results
- Discuss implications in findings

### Contradictory secondary findings
- Common in exploratory analyses
- Emphasize primary finding
- Note for future research

## Advanced Features

### Custom Analysis Functions
```python
class CustomAnalysisAgent(AnalysisAgent):
    def _conduct_primary_analysis(self, results_data, design, violations):
        # Custom analysis logic
        return custom_result
```

### Integration with Visualization Tools
```python
# Get visualization specs and create plots
for spec in report.visualization_specs:
    create_plot(spec)  # Your plotting function
```

## Output Report Structure

```
Analysis Report
├── Data Summary
│   ├── Sample size
│   ├── Variables
│   └── Quality issues
├── Descriptive Statistics
│   ├── Means and SDs
│   ├── Ranges
│   └── Distributions
├── Assumption Testing
│   ├── Normality
│   ├── Homogeneity
│   └── Independence
├── Statistical Analyses
│   ├── Primary test
│   ├── Secondary tests
│   └── Sensitivity tests
├── Findings
│   ├── Primary finding
│   ├── Secondary findings
│   └── Anomalies
├── Interpretation
│   ├── Hypothesis confirmation
│   ├── Effect sizes
│   └── Direction matching
├── Contextualization
│   ├── Literature comparison
│   ├── Novel aspects
│   └── Boundaries
└── Implications
    ├── Practical
    ├── Theoretical
    ├── Limitations
    └── Future directions
```

## Future Enhancements

- [ ] Bayesian analysis option
- [ ] Machine learning for pattern discovery
- [ ] Automated visualization generation
- [ ] Interactive analysis dashboard
- [ ] Multi-level modeling support
- [ ] Time series analysis
- [ ] Longitudinal data handling
- [ ] Missing data imputation
- [ ] Publication bias assessment
- [ ] Power analysis retrospective

## References

- Kline, R. B. (2015). Principles and Practice of Structural Equation Modeling
- Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences
- Cumming, G. (2012). Understanding the New Statistics
- APA Publication Manual (7th edition)

---

Built for Phase 4 of Agentic Scientific Discovery Lab 🚀
