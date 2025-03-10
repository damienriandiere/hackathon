"""
Stress Detection System Module
===============================

This module implements a stress detection system using physiological data
collected from a BITalino sensor. The system processes ECG and EDA signals
to calculate stress levels in real-time and visualizes the data using Pygame.

Classes:
--------
StressDetectionSystem:
    The main class that manages the stress detection process. It handles
    sensor connection, data processing, stress level calculation, and
    visualization.

Key Features:
-------------
- Real-time stress level detection using ECG and EDA data.
- Visualization of ECG trace and stress level evolution using Pygame.
- Logging of stress states with timestamps.
- Automatic sensor reconnection and calibration.

Dependencies:
-------------
- bitalino: Library to interface with the BITalino sensor.
- numpy: Library for numerical operations.
- pygame: Library for creating the visual interface.
- scipy: Library for signal processing.
- matplotlib: Library for generating summary graphs.
- portalocker: Library for file locking to ensure safe logging.
"""
from collections import deque
import datetime
import sys
import time

import bitalino
import numpy as np
import pygame
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import portalocker

class StressDetectionSystem:
    """
    A system for detecting stress levels using physiological data.
    """

    def __init__(self) -> None:
        """
        Initialize the stress detection system with configuration, logging,
        sensor connection, variable initialization, and display setup.
        """
        self.load_config()
        self.setup_logging()
        self.connect_sensor()
        self.initialize_variables()
        self.setup_display()

    def load_config(self) -> None:
        """
        Load configuration parameters from a file.
        """
        self.args = self.read_args_from_file('./sensors/args.txt')

        self.calm_threshold = self.args['CALM_THRESHOLD']
        self.moderate_threshold = self.args['MODERATE_THRESHOLD']
        self.stress_threshold = self.args['STRESS_THRESHOLD']

        self.eda_weight = self.args['EDA_WEIGHT']
        self.hr_weight = self.args['HR_WEIGHT']
        self.sdnn_weight = self.args['SDNN_WEIGHT']
        self.rmssd_weight = self.args['RMSSD_WEIGHT']
        self.pnn50_weight = self.args['PNN50_WEIGHT']

        self.mac_address = "98:D3:11:FE:03:67"
        self.sampling_rate = 1000
        self.num_frames = 10

    def read_args_from_file(self,  filename : str) -> dict:
        """
        Read configuration arguments from a file.
        """
        args = {}
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=')
                    args[key] = float(value)
        return args

    def setup_logging(self) -> None:
        """
        Set up logging to record stress levels.
        """
        self.log_filename = "./dataset/stress_log.txt"
        with open(self.log_filename, "w", encoding='utf-8') as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            file.write("Timestamp,State\n")
            portalocker.unlock(file)

    def connect_sensor(self) -> None:
        """
        Connect to the BITalino sensor.
        """
        try:
            self.device = bitalino.BITalino(self.mac_address)
            time.sleep(1)
            print("BITalino sensor connected")
            self.device.start(self.sampling_rate, [0, 1])
            print("START")
        except bitalino.BITalinoException as e:
            print(f"BITalino-specific error: {e}")
            sys.exit()
        except TimeoutError as e:
            print(f"Connection timed out: {e}")
            sys.exit()
        except OSError as e:
            print(f"Operating system error: {e}")
            sys.exit()
        except ValueError as e:
            print(f"Invalid parameter value: {e}")
            sys.exit()

    def initialize_variables(self) -> None:
        """
        Initialize variables and data buffers.
        """
        self.ecg_values = []
        self.ecg_buffer = []
        self.eda_buffer = []

        self.heart_rate = 0
        self.hrv_metrics = {"SDNN": 0, "RMSSD": 0, "PNN50": 0}
        self.last_eda_value = 0.0
        self.last_ecg_value = 0.0

        self.calibration_complete = False
        self.calibration_values = {
            "EDA": 0, "HR": 0, "SDNN": 0, "RMSSD": 0, "PNN50": 0
        }

        self.stress_history = deque(maxlen=300)
        self.time_history = deque(maxlen=300)

        self.start_time = time.time()
        self.last_calculation_time = time.time()
        self.last_reconnect_time = time.time()
        self.recording_duration = 0
        self.analysis_started = False
        self.current_stress_level = 0

    def setup_display(self) -> None:
        """
        Set up the Pygame display for visualization.
        """
        pygame.init()
        screen_info = pygame.display.Info()
        self.window_size = (int(screen_info.current_w * 0.9),
                            int(screen_info.current_h * 0.9))
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Stress Detection System - Futuristic Interface")

        self.font = pygame.font.SysFont("Arial", 30)
        self.hud_font = pygame.font.SysFont("Press Start 2P", 25)
        self.status_font = pygame.font.SysFont("Arial", 40)

        self.background_color = (20, 20, 20)
        self.text_color = (0, 255, 0)
        self.highlight_color = (255, 0, 0)
        self.neon_blue = (0, 255, 255)
        self.neon_purple = (255, 0, 255)
        self.ecg_color = (255, 255, 0)
        self.calm_color = (0, 255, 150)
        self.stress_color = (255, 50, 50)

    def calculate_hr_from_raw(self, ecg_data: np.ndarray, sampling_rate: int = 1000) -> tuple:
        """
        Calculate heart rate and HRV metrics from raw ECG data.
        """
        if len(ecg_data) < sampling_rate:
            return 0, 0, 0, 0

        try:
            normalized_ecg = (ecg_data - np.mean(ecg_data)) / np.std(ecg_data)
            peaks, _ = find_peaks(normalized_ecg, height=0.5, distance=sampling_rate//3)
            if len(peaks) < 2:
                peaks, _ = find_peaks(normalized_ecg, height=0.3, distance=sampling_rate//4)

            if len(peaks) < 2:
                print("No R peaks found in raw ECG data.")
                return 0, 0, 0, 0

            rr_intervals = np.diff(peaks) / sampling_rate
            heart_rate = 60 / np.mean(rr_intervals)
            sdnn = np.std(rr_intervals) * 1000
            rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals)))) * 1000

            if len(rr_intervals) < 2:
                pnn50 = 0
            else:
                rr_intervals_ms = rr_intervals * 1000
                nn_diffs = np.abs(np.diff(rr_intervals_ms))
                nn50 = sum(nn_diffs > 50)
                pnn50 = (nn50 / len(nn_diffs)) * 100 if len(nn_diffs) > 0 else 0

            return heart_rate, sdnn, rmssd, pnn50

        except ValueError as e:
            print(f"Value error in HR calculation: {e}")
            return 0, 0, 0, 0
        except IndexError as e:
            print(f"Index error in HR calculation: {e}")
            return 0, 0, 0, 0
        except TypeError as e:
            print(f"Type error in HR calculation: {e}")
            return 0, 0, 0, 0

    def analyze_stress_level(self, eda : float, hr : float, sdnn : float,
                             rmssd : float, pnn50 : float, baseline : dict) -> float:
        """
        Calculate stress level based on physiological parameters.
        """
        weights = {
            "EDA": self.eda_weight, "HR": self.hr_weight,
            "SDNN": self.sdnn_weight, "RMSSD": self.rmssd_weight,
            "PNN50": self.pnn50_weight
        }

        eda_change = min(max(0, (eda - baseline["EDA"]) / max(baseline["EDA"], 1)) * 100, 100)
        hr_change = min(max(0, (hr - baseline["HR"]) / max(baseline["HR"], 1)) * 100, 100)
        sdnn_change = min(max(0, (max(baseline["SDNN"], 1) - sdnn)
                              / max(baseline["SDNN"], 1)) * 100, 100)
        rmssd_change = min(max(0, (max(baseline["RMSSD"], 1) - rmssd)
                               / max(baseline["RMSSD"], 1)) * 100, 100)
        pnn50_change = min(max(0, (max(baseline["PNN50"], 1) - pnn50)
                               / max(baseline["PNN50"], 1)) * 100, 100)

        stress_level = (
            weights["EDA"] * eda_change +
            weights["HR"] * hr_change +
            weights["SDNN"] * sdnn_change +
            weights["RMSSD"] * rmssd_change +
            weights["PNN50"] * pnn50_change
        )

        return max(0, min(stress_level, 100))

    def draw_background(self) -> None:
        """
        Draw the background of the display.
        """
        self.screen.fill(self.background_color)

    def get_stress_color(self, stress_level : int = 0) -> tuple:
        """
        Get a color between CALM_COLOR and STRESS_COLOR based on stress level.
        """
        color_factor = stress_level / 100.0
        return (
            int(self.calm_color[0] + (self.stress_color[0] - self.calm_color[0]) * color_factor),
            int(self.calm_color[1] + (self.stress_color[1] - self.calm_color[1]) * color_factor),
            int(self.calm_color[2] + (self.stress_color[2] - self.calm_color[2]) * color_factor)
        )

    def draw_hud(self) -> None:
        """
        Display HUD interface with all metrics.
        """
        title_text = self.hud_font.render("STRESS DETECTION SYSTEM", True, self.text_color)
        self.screen.blit(title_text, (30, 30))

        time_text = self.font.render(f"Time: {self.recording_duration:.1f}s", True, self.text_color)
        self.screen.blit(time_text, (30, 70))

        if not self.calibration_complete:
            status_text = self.status_font.render("CALIBRATION IN PROGRESS...", True, self.neon_blue)
            self.screen.blit(status_text, (self.window_size[0] // 2 - 250,
                                           self.window_size[1] // 2 - 50))

        metrics = [
            (f"EDA: {self.last_eda_value:.2f}", 120, self.text_color),
            (f"ECG: {self.last_ecg_value:.2f}", self.window_size[1] - 300, self.ecg_color),
            (f"HR: {self.heart_rate:.2f} bpm", self.window_size[1] - 250, self.text_color),
            (f"SDNN: {self.hrv_metrics['SDNN']:.2f}", self.window_size[1] - 200, self.text_color),
            (f"RMSSD: {self.hrv_metrics['RMSSD']:.2f}", self.window_size[1] - 150, self.text_color),
            (f"PNN50: {self.hrv_metrics['PNN50']:.2f}%", self.window_size[1] - 100, self.text_color)
        ]

        for text, y_pos, color in metrics:
            self.screen.blit(self.font.render(text, True, color), (30, y_pos))

        if self.calibration_complete:
            stress_color = self.get_stress_color(self.current_stress_level)
            stress_text = self.status_font.render(f"STRESS: {self.current_stress_level:.1f}%",
                                                  True, stress_color)
            self.screen.blit(stress_text, (self.window_size[0] - 350, 50))

            if self.current_stress_level < self.calm_threshold:
                state_text = self.font.render("State: CALM", True, self.calm_color)
            elif self.current_stress_level < self.moderate_threshold:
                state_text = self.font.render("State: MODERATE TENSION", True, (255, 255, 0))
            else:
                state_text = self.font.render("State: HIGH STRESS", True, self.stress_color)
            self.screen.blit(state_text, (self.window_size[0] - 350, 150))

    def draw_ecg_trace(self) -> None:
        """
        Draw the ECG trace visualization.
        """
        if len(self.ecg_values) < 2:
            return

        ecg_area_height = 100
        ecg_area_top = self.window_size[1] - 150
        scale_factor = 5

        for i in range(1, len(self.ecg_values)):
            x1 = self.window_size[0] - (len(self.ecg_values) - i) * 2
            x2 = self.window_size[0] - (len(self.ecg_values) - i - 1) * 2
            y1 = ecg_area_top + ecg_area_height / 2 - self.ecg_values[i - 1] / scale_factor
            y2 = ecg_area_top + ecg_area_height / 2 - self.ecg_values[i] / scale_factor
            pygame.draw.line(self.screen, self.ecg_color, (x1, y1), (x2, y2), 2)

    def draw_stress_curve(self) -> None:
        """
        Draw the stress level history curve.
        """
        if len(self.stress_history) < 2:
            return

        area = {
            'width': 500, 'height': 150,
            'left': 800, 'top': 250
        }

        pygame.draw.rect(self.screen, self.text_color,
                         (area['left'], area['top'], area['width'], area['height']), 1)
        pygame.draw.line(self.screen, self.text_color,
                         (area['left'], area['top'] + area['height']),
                         (area['left'] + area['width'], area['top'] + area['height']), 1)
        pygame.draw.line(self.screen, self.text_color,
                         (area['left'], area['top']),
                         (area['left'], area['top'] + area['height']), 1)

        curve_title = self.font.render("Stress Level Evolution", True, self.text_color)
        self.screen.blit(curve_title, (area['left'], area['top'] - 50))

        for i in range(0, 101, 25):
            y_pos = area['top'] + area['height'] - (i / 100 * area['height'])
            pygame.draw.line(self.screen, self.text_color,
                             (area['left'] - 5, y_pos), (area['left'], y_pos), 1)
            y_label = self.font.render(f"{i}", True, self.text_color)
            self.screen.blit(y_label, (area['left'] - 25, y_pos - 10))

        points = []
        for i, stress in enumerate(self.stress_history):
            if i >= len(self.stress_history) - area['width']//2:
                x = area['left'] + (i - (len(self.stress_history) - area['width']//2)) * 2
                y = area['top'] + area['height'] - (stress / 100 * area['height'])
                points.append((x, y))

        if len(points) >= 2:
            pygame.draw.lines(self.screen, self.neon_blue, False, points, 2)
            pygame.draw.circle(self.screen,
                               self.get_stress_color(self.stress_history[-1]),
                               points[-1],
                               5)

    def log_stress_state(self, stress_level : int) -> None:
        """
        Record stress state to the log file.
        """
        timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if stress_level < self.calm_threshold:
            state = "CALM"
        elif stress_level < self.moderate_threshold:
            state = "MODERATE"
        else:
            state = "STRESSED"

        portalocker.lock(self.log_file, portalocker.LOCK_EX)
        self.log_file.write(f"{timestamp_now},{state}\n")
        self.log_file.flush()
        portalocker.unlock(self.log_file)

    def calibrate(self) -> None:
        """
        Perform calibration using buffer data.
        """
        print("Calibration complete, starting real-time analysis...")

        if len(self.ecg_buffer) >= 20 * self.sampling_rate * 0.8:
            calculated_hr, calculated_sdnn, calculated_rmssd, calculated_pnn50 = self.calculate_hr_from_raw(
                np.array(self.ecg_buffer), self.sampling_rate)
            self.calibration_values["HR"] = calculated_hr if calculated_hr > 0 else 70
            self.calibration_values["SDNN"] = calculated_sdnn if calculated_sdnn > 0 else 50
            self.calibration_values["RMSSD"] = calculated_rmssd if calculated_rmssd > 0 else 30
            self.calibration_values["PNN50"] = calculated_pnn50 if calculated_pnn50 > 0 else 10

        if len(self.eda_buffer) > 0:
            self.calibration_values["EDA"] = np.mean(self.eda_buffer)

        print(f"Calibration values: {self.calibration_values}")

    def process_data(self) -> bool:
        """
        Process new data from the sensor.
        """
        try:
            data = self.device.read(self.num_frames)

            if np.mean(data[:, 1]) < 1:
                return False

            eda = data[:, 5]
            ecg = data[:, 6]
            self.last_eda_value = eda[-1]
            self.last_ecg_value = ecg[-1]

            self.eda_buffer.extend(eda)
            self.ecg_values.append(self.last_ecg_value)
            self.ecg_buffer.extend(ecg)

            if len(self.ecg_values) > self.window_size[0]:
                self.ecg_values.pop(0)

            buffer_size = 20 * self.sampling_rate
            if len(self.ecg_buffer) > buffer_size:
                self.ecg_buffer = self.ecg_buffer[-buffer_size:]
            if len(self.eda_buffer) > buffer_size:
                self.eda_buffer = self.eda_buffer[-buffer_size:]

            return True

        except OSError as e:
            print(f"Operating system error while reading data: {e}")
            return False
        except ValueError as e:
            print(f"Value error while processing data: {e}")
            return False
        except IndexError as e:
            print(f"Index error while processing data: {e}")
            return False
        except RuntimeError as e:
            print(f"Runtime error while processing data: {e}")
            return False

    def update_metrics(self) -> None:
        """
        Calculate metrics from buffer data.
        """
        if len(self.ecg_buffer) >= 20 * self.sampling_rate * 0.9:
            calculated_hr,calculated_sdnn, calculated_rmssd, calculated_pnn50 = self.calculate_hr_from_raw(
                np.array(self.ecg_buffer), self.sampling_rate)

            if calculated_hr > 0:
                self.heart_rate = calculated_hr
                self.hrv_metrics["SDNN"] = calculated_sdnn
                self.hrv_metrics["RMSSD"] = calculated_rmssd
                self.hrv_metrics["PNN50"] = calculated_pnn50

                mean_eda = np.mean(self.eda_buffer[-int(len(self.eda_buffer)*0.2):])
                self.current_stress_level = self.analyze_stress_level(
                    mean_eda, self.heart_rate, calculated_sdnn, calculated_rmssd, calculated_pnn50,
                    self.calibration_values
                )

                self.stress_history.append(self.current_stress_level)
                self.time_history.append(self.recording_duration)
                self.log_stress_state(self.current_stress_level)

    def generate_summary(self) -> None:
        """
        Generate summary graph after recording.
        """
        if len(self.stress_history) > 0:
            plt.figure(figsize=(10, 6))
            plt.plot(list(self.time_history), list(self.stress_history), 'b-', linewidth=2)
            plt.title('Stress Level Evolution Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Stress Level (%)')
            plt.grid(True)
            plt.ylim(0, 100)

            graph_filename = "./dataset/stress_graph.png"
            plt.savefig(graph_filename)
            print(f"Graph saved in file '{graph_filename}'")

    def cleanup(self) -> None:
        """
        Clean up resources.
        """
        print("STOP")
        self.device.trigger([0, 0])
        self.device.stop()
        self.device.close()
        self.log_file.close()
        print(f"Data recorded in file '{self.log_filename}'")
        pygame.quit()

    def run(self) -> None:
        """
        Main application loop.
        """
        running = True
        while running:
            current_time = time.time()
            self.recording_duration = current_time - self.start_time

            if self.recording_duration >= 20 and not self.calibration_complete:
                self.calibration_complete = True
                self.calibrate()
                self.analysis_started = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if current_time - self.last_reconnect_time >= 60:
                print("Automatic reconnection attempt...")
                self.device.stop()
                self.device.close()
                self.connect_sensor()
                self.last_reconnect_time = current_time

            if not self.process_data():
                break

            if self.analysis_started and current_time - self.last_calculation_time >= 1.0:
                self.update_metrics()
                self.last_calculation_time = current_time

            self.draw_background()
            self.draw_hud()
            self.draw_ecg_trace()

            if self.calibration_complete:
                self.draw_stress_curve()

            pygame.display.flip()
            pygame.time.delay(10)

        self.cleanup()
        self.generate_summary()

if __name__ == "__main__":
    stress_system = StressDetectionSystem()
    stress_system.run()
