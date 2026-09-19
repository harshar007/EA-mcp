"""
Electronics Knowledge Classifier.
Classifies text into specific electronics categories with confidence scoring and keyword extraction.
"""
import re
from typing import List, Tuple, Dict
from src.domain.entities import ClassificationCategory
from src.domain.interfaces import ClassifierInterface


class ElectronicsDomainClassifier(ClassifierInterface):
    """Rule-based & keyword-density classifier for electronics documentation."""

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

    def classify(self, text: str) -> Tuple[ClassificationCategory, float, List[str]]:
        """
        Classifies given electronics text into category, confidence, and tags.
        """
        lower_text = text.lower()
        scores: Dict[ClassificationCategory, int] = {}
        matched_tags_map: Dict[ClassificationCategory, List[str]] = {}

        for category, keywords in self.KEYWORDS_MAP.items():
            matches = []
            score = 0
            for kw in keywords:
                # Word boundary match for short acronyms, substring for phrases
                if len(kw) <= 4:
                    pattern = r'\b' + re.escape(kw) + r'\b'
                    found = len(re.findall(pattern, lower_text))
                else:
                    found = lower_text.count(kw)
                
                if found > 0:
                    score += found * (2 if len(kw.split()) > 1 else 1)
                    matches.append(kw)
            
            scores[category] = score
            matched_tags_map[category] = matches

        total_score = sum(scores.values())
        if total_score == 0:
            return ClassificationCategory.GENERAL_ELECTRONICS, 0.5, ["general"]

        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        confidence = min(round(best_score / (total_score + 1e-6), 2), 1.0)
        tags = matched_tags_map.get(best_category, [])[:5]

        return best_category, confidence, tags
