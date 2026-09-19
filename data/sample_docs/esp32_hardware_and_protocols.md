# ESP32 Hardware Architecture and Communication Protocols Guide

## Overview
The ESP32 is a dual-core Xtensa 32-bit LX6 microcontroller designed by Espressif Systems. It integrates Wi-Fi (802.11 b/g/n) and Bluetooth v4.2 BR/EDR and BLE.

## Key Hardware Specifications
- **CPU Clock**: Adjustable from 80 MHz to 240 MHz.
- **Memory**: 520 KB internal SRAM, 448 KB ROM, external SPI flash typically 4MB or 8MB.
- **GPIO Matrix**: 34 programmable GPIOs, full multiplexing capabilities through the GPIO matrix.
- **ADCs**: Two 12-bit SAR ADCs (ADC1 with 8 channels, ADC2 with 10 channels). Note: ADC2 cannot be used concurrently when Wi-Fi is active.
- **DACs**: Two 8-bit DAC channels (GPIO25 and GPIO26).

## Communication Protocols

### 1. I2C Interface
The ESP32 has 2 I2C hardware bus interfaces (I2C0 and I2C1). Default I2C pins:
- **SDA**: GPIO 21
- **SCL**: GPIO 22
- **Standard Mode**: 100 kHz, **Fast Mode**: 400 kHz.
- **Pull-up Resistors**: External pull-ups (typically 4.7kΩ or 2.2kΩ for 3.3V) are required on SDA and SCL lines.

### 2. SPI Interface
ESP32 features four SPI peripherals: SPI0, SPI1 (used internally for Flash memory), VSPI, and HSPI.
- **HSPI default pins**:
  - SCK: GPIO 14
  - MISO: GPIO 12
  - MOSI: GPIO 13
  - CS: GPIO 15
- **VSPI default pins**:
  - SCK: GPIO 18
  - MISO: GPIO 19
  - MOSI: GPIO 23
  - CS: GPIO 5
- Maximum SPI clock speed: Up to 80 MHz in master mode.

### 3. UART Interface
- Three UART controllers (UART0, UART1, UART2).
- Default UART0 (Programming & Serial monitor): TX=GPIO1, RX=GPIO3.
- UART2 default: TX=GPIO17, RX=GPIO16.

## Power Management & Sleep Modes
- **Active Mode**: 80-240 mA depending on RF transmission.
- **Modem-sleep Mode**: Wi-Fi/Bluetooth disabled, CPU running (20-30 mA).
- **Light-sleep Mode**: CPU clock gated, RTC peripherals active (0.8 mA).
- **Deep-sleep Mode**: ULP coprocessor and RTC memory active (~10-15 µA).
