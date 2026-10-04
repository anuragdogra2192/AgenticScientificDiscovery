# Experiment Agent 🧪

**Status**: ✅ **LIVE with Claude Haiku 4.5**

The Experiment Agent transforms hypotheses into rigorous BSL-3 experimental protocols for Mycobacterium tuberculosis drug discovery. Uses Claude Haiku to design protocols, estimate budgets, and assess feasibility—all focused on Mtb targets (DprE1, InhA, MmpL3) with in vitro and cellular assays.

## Features

### 🎯 Experiment Design
- **7 Experiment Types**: RCT, Observational, Quasi-experimental, Simulation, Lab, A/B Test, Meta-analysis
- **Automatic Type Selection**: Matches hypothesis type to optimal experiment design
- **Procedural Generation**: Step-by-step experimental procedures
- **Variable Operationalization**: Clear measurement definitions

### 📊 Resource Estimation
- **Personnel Planning**: Roles, hours, and costs
- **Equipment Requirements**: Lab, computing, software needs
- **Budget Calculation**: Personnel, equipment, services costs
- **Timeline**: Duration, milestones, critical path

### 🗂️ Dataset Identification
- **Source Discovery**: Open datasets, domain-specific repositories
- **Requirements Definition**: Variables, sample size, access level
- **Preprocessing Planning**: Data preparation time estimates

### 📈 Success Prediction
- **Probability Estimation**: Success likelihood based on hypothesis strength
- **Power Analysis**: Statistical power considerations
- **Success Factors**: Elements supporting success
- **Failure Factors**: Potential pitfalls

### ✅ Quality Assurance
- **Protocol Validation**: Check hypothesis match, power, variables, confounds
- **Rigor Checklist**: Preregistration, blinding, replication
- **Risk Assessment**: Potential problems and mitigation
- **Document Generation**: Formal protocol document

## Installation

```bash
# Dependencies already installed
pip install -r ../../requirements.txt
```

## Usage

### Basic Experiment Design

```python
import asyncio
from agents.hypothesis_agent import HypothesisAgent
from agents.experiment_agent import ExperimentAgent

async def design_experiment():
    # Get hypothesis from Hypothesis Agent
    hyp_agent = HypothesisAgent()
    hypotheses = await hyp_agent.generate_hypotheses(...)
    
    # Design experiment
    exp_agent = ExperimentAgent()
    design = await exp_agent.design_experiment(
        hypothesis=hypotheses[0].to_dict()
    )
    
    print(f"✓ {design.title}")
    print(f"  Type: {design.experiment_type.value}")
    print(f"  Sample Size: {design.sample_size}")
    print(f"  Duration: {design.duration_weeks} weeks")
    print(f"  Cost: ${design.total_cost:,.0f}")
    print(f"  Success Probability: {design.success_prediction.probability_success:.1%}")
    
    await exp_agent.close()

asyncio.run(design_experiment())
```

### Examine Design Details

```python
# Procedures
print("Procedures:")
for proc in design.procedures:
    print(f"{proc.step_number}. {proc.description} ({proc.duration_minutes} min)")

# Measurements
print("\nPrimary Measurements:")
for measure in design.primary_measures:
    print(f"• {measure.name}: {measure.method}")

# Personnel
print("\nPersonnel Requirements:")
for role, hours in design.personnel_needed.items():
    print(f"• {role}: {hours}")

# Budget
print(f"\nTotal Budget: ${design.total_cost:,.0f}")
```

### Validate Design

```python
validation = await exp_agent.validate_design(design)

print(f"Valid: {validation['valid']}")
if validation['issues']:
    print("Critical Issues:")
    for issue in validation['issues']:
        print(f"  • {issue}")

if validation['warnings']:
    print("Warnings:")
    for warning in validation['warnings']:
        print(f"  • {warning}")
```

### Generate Protocol Document

```python
protocol = await exp_agent.generate_protocol_document(design)

# Save to file
with open("protocol.md", "w") as f:
    f.write(protocol)

print("✓ Protocol saved to protocol.md")
```

### Export to JSON

```python
import json

design_dict = design.to_dict()

with open("design.json", "w") as f:
    json.dump(design_dict, f, indent=2)
```

## Experiment Types

### 1. Randomized Controlled Trial (RCT)
**Rigor**: High | **Sample Size**: 100+ | **Duration**: 8 weeks

Best for causal hypotheses with intervention testing.
- Random assignment to conditions
- Blinded outcome assessment
- Intent-to-treat analysis

### 2. Laboratory Experiment
**Rigor**: High | **Sample Size**: 50+ | **Duration**: 6 weeks

Best for mechanism testing in controlled environments.
- Precise measurements
- Controlled conditions
- Repeated measurement

### 3. Quasi-Experimental Design
**Rigor**: Medium | **Sample Size**: 150+ | **Duration**: 10 weeks

Field interventions without random assignment.
- Matched groups
- Baseline measurement
- Post-intervention assessment

### 4. Observational Study
**Rigor**: Medium | **Sample Size**: 200+ | **Duration**: 12 weeks

Measure variables without intervention.
- Representative sampling
- Multiple measurements
- Confound adjustment

### 5. Computational Simulation
**Rigor**: Medium | **Sample Size**: 1000+ | **Duration**: 4 weeks

Test hypothesis using models and simulations.
- Formal model specification
- Parameter manipulation
- Validation

### 6. A/B Test
**Rigor**: Medium | **Sample Size**: 1000+ | **Duration**: 2 weeks

Rapid testing with continuous data collection.
- Online platform
- Random assignment
- Real-time monitoring

### 7. Meta-Analysis
**Rigor**: High | **Sample Size**: N/A | **Duration**: 16 weeks

Synthesize results across studies.
- Study selection
- Quality assessment
- Statistical synthesis

## Resource Planning

### Personnel Roles

| Role | Hours/Week | Rate | Purpose |
|------|-----------|------|---------|
| Principal Investigator | 5 | $150/hr | Study oversight |
| Postdoc/Senior | 30 | $75/hr | Primary execution |
| Graduate Student | 25 | $25/hr | Data collection |
| Research Assistant | 20 | $20/hr | Administration |

### Budget Categories

**Personnel**: Research team costs
**Equipment**: Lab instruments, computing, software
**Services**: Cloud hosting, platforms, data collection
**Other**: Travel, materials, analysis

## Measurement & Validation

### Validity Types

1. **Internal Validity**: Can we infer causality?
2. **External Validity**: Can we generalize?
3. **Construct Validity**: Are we measuring what we claim?
4. **Statistical Conclusion Validity**: Are stats correct?

### Strategies

- Random assignment
- Blinded assessment
- Multiple measures
- Validated instruments
- Confound control
- Preregistration

## Sample Size Determination

Based on:
- Hypothesis complexity
- Expected effect size
- Statistical power (80%)
- Type I error rate (α = 0.05)

**Minimum by Complexity**:
- Simple: 64-80 participants
- Moderate: 128-160 participants
- Complex: 200-250 participants

## Timeline & Critical Path

### Typical Milestones
1. Protocol finalization and approval
2. Participant recruitment
3. Baseline assessment
4. Intervention delivery
5. Outcome assessment
6. Data analysis

### Critical Path
Items that must complete on schedule:
- Regulatory approval
- Recruitment targets
- Intervention fidelity
- Outcome measurement
- Data analysis

## Risk Assessment

### Common Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Insufficient power | High | Increase sample size |
| Measurement error | High | Validate instruments |
| Attrition | High | Retention strategies |
| Confounding | High | Experimental design |
| Low compliance | Medium | Protocol adherence |

### Mitigation Strategies

- Pilot testing
- Rigorous protocols
- Quality monitoring
- Alternative designs
- Early stopping rules
- Fallback datasets

## Success Prediction

The agent estimates probability of confirming hypothesis based on:
- Hypothesis strength (novelty, feasibility, impact)
- Experimental design rigor
- Measurement quality
- Expected effect size
- Sample size adequacy

**Interpretation**:
- 0.70+: Likely to succeed
- 0.50-0.70: Moderate probability
- <0.50: Risky; may need design refinement

## Common Patterns

### Pattern 1: Quick Feasibility Check
```python
design = await exp_agent.design_experiment(hypothesis)
print(f"Probability: {design.success_prediction.probability_success:.0%}")
print(f"Cost: ${design.total_cost:,.0f}")
print(f"Duration: {design.duration_weeks} weeks")
```

### Pattern 2: Compare Multiple Designs
```python
hypotheses = await hyp_agent.generate_hypotheses(...)
designs = [
    await exp_agent.design_experiment(h.to_dict())
    for h in hypotheses[:3]
]
```

### Pattern 3: Export for Team Review
```python
design_dict = design.to_dict()
protocol = await exp_agent.generate_protocol_document(design)

with open("design.json", "w") as f:
    json.dump(design_dict, f, indent=2)

with open("protocol.md", "w") as f:
    f.write(protocol)
```

### Pattern 4: Risk Assessment
```python
validation = await exp_agent.validate_design(design)
risks = design.potential_risks
mitigations = design.mitigation_strategies
```

## Configuration

Edit `config.yaml` to customize:

**Experiment types and defaults**:
```yaml
experiment_types:
  randomized_controlled_trial:
    min_sample_size: 100
    typical_duration_weeks: 8
```

**Resource costs**:
```yaml
resources:
  personnel:
    principal_investigator:
      hourly_rate: 150
```

**Sample size parameters**:
```yaml
sample_size_estimation:
  defaults:
    alpha: 0.05      # Type I error
    beta: 0.20       # Type II error
```

## Running Examples

```bash
# Run all 8 examples
python agents/experiment_agent/examples.py

# Or specific example in Python
from agents.experiment_agent.examples import example_1_basic_experiment_design
asyncio.run(example_1_basic_experiment_design())
```

## Output Formats

### JSON Export
```python
design_dict = design.to_dict()
# Contains all design information in structured format
```

### Markdown Protocol
```python
protocol = await exp_agent.generate_protocol_document(design)
# Human-readable protocol document
```

### Console Summary
```python
print(f"Type: {design.experiment_type.value}")
print(f"Sample: {design.sample_size}")
print(f"Cost: ${design.total_cost:,.0f}")
```

## Integration with Other Agents

### Input from Hypothesis Agent
```python
hypotheses = await hyp_agent.generate_hypotheses(papers, gaps, query)
design = await exp_agent.design_experiment(hypotheses[0].to_dict())
```

### Output for Analysis Agent (Phase 4)
```python
# Design defines:
# - What to measure
# - How to measure it
# - What data to collect
# - How to analyze it
# → Feeds into Analysis Agent
```

## Troubleshooting

### Design shows low success probability
- Review hypothesis quality
- Consider simpler hypothesis
- Increase sample size budget
- Improve measurement reliability

### Budget exceeds resources
- Reduce sample size (if power allows)
- Simplify design
- Use simulation instead of empirical
- Consider multi-site study

### Timeline too long
- Parallel data collection
- Simplified procedures
- Simulation instead of lab
- A/B test instead of RCT

## Advanced Features

### Custom Scoring
Override scoring methods for domain-specific considerations:
```python
class CustomExperimentAgent(ExperimentAgent):
    def _calculate_sample_size(self, hypothesis):
        # Custom logic
        return custom_size
```

### Design Refinement
Iteratively improve designs based on feedback:
```python
design1 = await exp_agent.design_experiment(hyp1)
validation1 = await exp_agent.validate_design(design1)
# Refine hypothesis
design2 = await exp_agent.design_experiment(hyp2)
```

## Future Enhancements

- [ ] Automated cost optimization
- [ ] Multi-site design support
- [ ] Adaptive/sequential designs
- [ ] Power analysis visualization
- [ ] Regulatory compliance checking
- [ ] Equipment availability checking
- [ ] Weather/environment considerations
- [ ] Participant recruitment modeling
- [ ] Data monitoring planning
- [ ] CONSORT/STROBE compliance

## References

- Campbell & Stanley (1963): Experimental design classics
- Kraemer & Blasey (2016): How to design better intervention studies
- Cohen (1988): Statistical power analysis
- FDA Guidance: Study design principles
- NIH Grant writing: Research design section

---

Built for Phase 3 of Agentic Scientific Discovery Lab 🚀
