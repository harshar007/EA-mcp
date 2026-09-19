# Power MOSFET Gate Driver Design and Switching Dynamics

## Overview of Power MOSFET Switching
Power MOSFETs are voltage-controlled devices, but rapid switching requires sourcing and sinking significant transient currents to charge and discharge internal parasitic capacitances ($C_{gs}$, $C_{gd}$, $C_{ds}$).

## Key Dynamic Parameters
1. **Total Gate Charge ($Q_g$)**: The total charge required to raise the gate voltage to a given $V_{GS}$.
2. **Miller Plateau ($V_{plateau}$)**: The flat region during turn-on where the gate voltage remains constant while drain-to-source voltage ($V_{DS}$) falls. $Q_{gd}$ (Miller charge) is charged during this interval.
3. **Peak Gate Drive Current**:
   $$I_{peak} = \frac{V_{driver} - V_{plateau}}{R_{driver} + R_{gate,ext} + R_{gate,int}}$$

## High-Side Gate Driving (Bootstrap Technique)
When using an N-channel MOSFET as a high-side switch in half-bridge or buck topologies:
- The source terminal swings between GND and $V_{in}$.
- A bootstrap circuit provides a floating supply ($V_{boot} = V_{sw} + V_{cc} - V_{diode}$).

### Bootstrap Capacitor Sizing Formula:
$$C_{boot} \ge \frac{2 \cdot \left( 2 \cdot Q_g + \frac{I_{leakage}}{f_{sw}} + Q_{reverse\_recovery} \right)}{\Delta V_{boot,allowable}}$$
Where $\Delta V_{boot,allowable}$ is typically $0.5\text{V}$ to $1.0\text{V}$.

## Snubber Circuit Design (R-C Snubber)
Parasitic PCB loop inductance ($L_p$) and MOSFET output capacitance ($C_{oss}$) cause high-frequency voltage ringing during turn-off:
- Resonance frequency: $f_0 = \frac{1}{2 \pi \sqrt{L_p C_{oss}}}$.
- Snubber resistor: $R_{snub} \approx \sqrt{\frac{L_p}{C_{oss}}}$.
- Snubber capacitor: $C_{snub} \approx 2 \text{ to } 3 \times C_{oss}$.
- Power dissipated in snubber resistor: $P_{snub} = C_{snub} \cdot V_{in}^2 \cdot f_{sw}$.
