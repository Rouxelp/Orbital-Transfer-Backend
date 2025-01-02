# Hohmann Transfer Process and Calculations

## Overview
The Hohmann transfer is a two-impulse maneuver used to transfer between two coplanar orbits. This document explains the process step-by-step.

## Calculations

### Step 1: Semi-major Axis of Transfer Orbit
To calculate the semi-major axis `a_transfer`:
$$
a_{\text{transfer}} = \frac{r_{\text{perigee}} + r_{\text{apogee}}}{2}
$$

### Step 2: Velocity in Each Orbit
1. Velocity in the initial orbit:
$$
v_1 = \sqrt{\mu \cdot \frac{1}{r_1}}
$$

2. Velocity in the transfer orbit at perigee:
$$
v_{\text{transfer,1}} = \sqrt{\mu \cdot \left( \frac{2}{r_1} - \frac{1}{a_{\text{transfer}}} \right)}
$$

3. Velocity in the transfer orbit at apogee:
$$
v_{\text{transfer,2}} = \sqrt{\mu \cdot \left( \frac{2}{r_2} - \frac{1}{a_{\text{transfer}}} \right)}
$$

4. Velocity in the final orbit:
$$
v_2 = \sqrt{\mu \cdot \frac{1}{r_2}}
$$

### Step 3: Delta-V Calculation
1. First impulse:
$$
\Delta v_1 = v_{\text{transfer,1}} - v_1
$$

2. Second impulse:
$$
\Delta v_2 = v_2 - v_{\text{transfer,2}}
$$

 
