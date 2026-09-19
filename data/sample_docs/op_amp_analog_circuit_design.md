# Operational Amplifier (Op-Amp) Analog Circuit Design and Analysis

## Fundamental Op-Amp Topologies

### 1. Inverting Amplifier
The output voltage is inverted and scaled relative to the input:
$$V_{out} = -\left( \frac{R_f}{R_{in}} \right) \cdot V_{in}$$
- Input impedance: $Z_{in} = R_{in}$.
- Virtual ground exists at the inverting pin ($V_- = 0\text{V}$).

### 2. Non-Inverting Amplifier
The input signal is applied directly to the non-inverting terminal:
$$V_{out} = \left( 1 + \frac{R_f}{R_1} \right) \cdot V_{in}$$
- Input impedance: Very high ($> 10^{9} \Omega$ for CMOS/JFET op-amps).
- Voltage gain is always $\ge 1$.

### 3. Differential (Difference) Amplifier
Measures the difference between two signals while rejecting common-mode noise:
$$V_{out} = \frac{R_2}{R_1} \cdot (V_2 - V_1) \quad \text{when } \frac{R_2}{R_1} = \frac{R_4}{R_3}$$
- **Common Mode Rejection Ratio (CMRR)**: Measures the op-amp's ability to reject identical noise present on both inputs. A 0.1% resistor tolerance is required for $>60\text{ dB}$ CMRR.

## Critical Op-Amp Parameters
1. **Gain-Bandwidth Product (GBWP)**: The product of open-loop gain and frequency. 
   - $f_{3dB} = \frac{GBWP}{\text{Closed Loop Gain}}$.
2. **Slew Rate ($SR$)**: Maximum rate of change of output voltage per unit time ($\text{V}/\mu\text{s}$).
   - Full-power bandwidth: $f_{max} = \frac{SR}{2 \pi V_p}$.
3. **Input Offset Voltage ($V_{os}$)**: Small DC voltage between inputs required to force output to zero.
4. **Input Bias Current ($I_b$)**: Current flowing into input terminals; causes voltage errors with high feedback resistances.

## Active Low-Pass Filter Design (Sallen-Key Topology)
- Cutoff frequency: $f_c = \frac{1}{2 \pi \sqrt{R_1 R_2 C_1 C_2}}$.
- Quality factor ($Q$): Determines filter response (Butterworth for flat passband, Bessel for linear phase, Chebyshev for sharp rolloff).
