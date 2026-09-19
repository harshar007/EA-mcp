# Step-Down (Buck) DC-DC Converter SMPS Design and Calculation Guide

## Introduction
A Buck converter is a switch-mode power supply (SMPS) topology used to step down DC voltage efficiently from a higher level ($V_{in}$) to a lower level ($V_{out}$). Typical efficiencies range between 85% and 96%.

## Key Equations and Design Rules

### 1. Duty Cycle (D)
For continuous conduction mode (CCM):
$$D = \frac{V_{out}}{V_{in} \cdot \eta}$$
Where $\eta$ is the estimated efficiency (typically 0.90).

### 2. Inductor Selection ($L$)
The inductor value is determined based on the acceptable ripple current $\Delta I_L$ (usually chosen as 20% to 40% of maximum output current $I_{out}$):
$$L = \frac{(V_{in} - V_{out}) \cdot D}{\Delta I_L \cdot f_{sw}}$$
Where $f_{sw}$ is the switching frequency (typically 200 kHz to 2.2 MHz).
- **Inductor Saturation Current**: Ensure $I_{sat} > I_{out,max} + \frac{\Delta I_L}{2}$ with at least 20-30% safety margin.

### 3. Output Capacitor Selection ($C_{out}$)
The output capacitor must filter the inductor ripple current and maintain output voltage stability during load transients:
$$\Delta V_{out} = \Delta I_L \cdot \left( ESR + \frac{1}{8 \cdot f_{sw} \cdot C_{out}} \right)$$
Using ceramic multilayer capacitors (MLCC with X7R or X5R dielectric) minimizes Equivalent Series Resistance (ESR).

### 4. Freewheeling Diode or Synchronous MOSFET
- In nonsynchronous converters: Use a Schottky diode with reverse voltage rating $> 1.3 \cdot V_{in,max}$.
- In synchronous buck converters: Use low $R_{DS(on)}$ logic-level N-channel MOSFETs for high efficiency.

## PCB Layout Best Practices
1. **High di/dt Power Loop**: Keep the input capacitor ($C_{in}$), high-side MOSFET, and low-side switch/diode loop as tight and small as possible.
2. **Switch Node (SW)**: Minimize copper trace area on the switch node to prevent radiated electromagnetic interference (EMI).
3. **Feedback Trace**: Route the sensitive feedback divider trace away from inductor magnetic flux and switch nodes.
