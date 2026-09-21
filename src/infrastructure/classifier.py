"""
Electronics Knowledge Classifier.
Classifies text into specific electronics categories with confidence scoring and keyword extraction.
"""
import re
from typing import List, Tuple, Dict
from src.domain.entities import ClassificationCategory
from src.domain.interfaces import ClassifierInterface


class ElectronicsDomainClassifier(ClassifierInterface):
    """Fast, pre-compiled keyword-density classifier for electronics documentation."""

    KEYWORDS_MAP: Dict[ClassificationCategory, List[str]] = {
        ClassificationCategory.POWER_ELECTRONICS: [
            "buck converter", "boost converter", "smps", "flyback", "pwm", "duty cycle",
            "mosfet", "igbt", "rectifier", "inductor saturation", "voltage regulator",
            "switching frequency", "snubber", "gate driver", "drain-source", "vds", "vgs",
            "ripple current", "efficiency", "thermal dissipation", "ldo", "power supply"
        ],
        ClassificationCategory.MICROCONTROLLERS_EMBEDDED: [
            "esp32", "stm32", "arduino", "microcontroller", "arm cortex", "gpio",
            "interrupt", "timer", "freertos", "firmware", "flash memory", "sram", "dma",
            "adc", "dac", "bootloader", "clock tree", "risc-v", "pic32", "avr", "embedded c"
        ],
        ClassificationCategory.ANALOG_CIRCUITS: [
            "op-amp", "operational amplifier", "gain", "bandwidth", "feedback", "inverting",
            "non-inverting", "bode plot", "slew rate", "filter", "active filter", "bjt",
            "transistor", "bias", "common emitter", "differential amplifier", "cmrr",
            "noise figure", "signal conditioning", "analog front end", "instrumentation amp"
        ],
        ClassificationCategory.DIGITAL_SYSTEMS_PROTOCOLS: [
            "i2c", "spi", "uart", "can bus", "rs485", "modbus", "usb", "baud rate",
            "logic level", "fpga", "verilog", "vhdl", "propagation delay", "setup time",
            "hold time", "shift register", "i2s", "ethernet phy", "clock jitter"
        ],
        ClassificationCategory.PASSIVE_COMPONENTS: [
            "resistor", "capacitor", "dielectric", "esr", "esl", "ferrite bead", "thermistor",
            "potentiometer", "varistor", "ptc", "ntc", "piezoelectric", "hall effect sensor",
            "photodiode", "optocoupler", "shunt resistor", "current sense"
        ],
        ClassificationCategory.RF_WIRELESS: [
            "rf", "antenna", "impedance matching", "smith chart", "50 ohm", "vswr",
            "bluetooth", "ble", "wi-fi", "zigbee", "lora", "sub-ghz", "attenuation",
            "lna", "power amplifier", "demodulation", "carrier frequency", "coaxial"
        ]
    }

    def __init__(self):
        # Pre-compile regex patterns for fast matching
        self._compiled_patterns: Dict[ClassificationCategory, List[Tuple[str, re.Pattern, int]]] = {}
        for cat, keywords in self.KEYWORDS_MAP.items():
            patterns = []
            for kw in keywords:
                weight = 2 if len(kw.split()) > 1 else 1
                if len(kw) <= 4:
                    pat = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                else:
                    pat = re.compile(re.escape(kw), re.IGNORECASE)
                patterns.append((kw, pat, weight))
            self._compiled_patterns[cat] = patterns

    def classify(self, text: str) -> Tuple[ClassificationCategory, float, List[str]]:
        """
        Classifies given electronics text into category, confidence, and tags.
        """
        scores: Dict[ClassificationCategory, int] = {}
        matched_tags: Dict[ClassificationCategory, List[str]] = {}

        for category, patterns in self._compiled_patterns.items():
            cat_score = 0
            cat_tags = []
            for kw, pat, weight in patterns:
                matches = len(pat.findall(text))
                if matches > 0:
                    cat_score += matches * weight
                    cat_tags.append(kw)
            scores[category] = cat_score
            matched_tags[category] = cat_tags

        total_score = sum(scores.values())
        if total_score == 0:
            return ClassificationCategory.GENERAL_ELECTRONICS, 0.5, ["general"]

        best_category = max(scores, key=scores.get)
        confidence = min(round(scores[best_category] / total_score, 2), 1.0)
        tags = matched_tags.get(best_category, [])[:5]

        return best_category, confidence, tags

