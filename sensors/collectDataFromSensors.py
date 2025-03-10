import bitalino
import numpy as np
import time
import pygame
from scipy.signal import find_peaks
import datetime
import matplotlib.pyplot as plt
from collections import deque
import portalocker

class StressDetectionSystem:
    def __init__(self):
        # Configuration
        self.load_config()
        self.setup_logging()
        self.connect_sensor()
        self.initialize_variables()
        self.setup_display()

    def load_config(self):
        # Load configuration from file
        self.args = self.read_args_from_file('./sensors/args.txt')
        
        # Extract thresholds and weights
        self.CALM_THRESHOLD = self.args['CALM_THRESHOLD']
        self.MODERATE_THRESHOLD = self.args['MODERATE_THRESHOLD']
        self.STRESS_THRESHOLD = self.args['STRESS_THRESHOLD']
        
        self.EDA_WEIGHT = self.args['EDA_WEIGHT']
        self.HR_WEIGHT = self.args['HR_WEIGHT']
        self.SDNN_WEIGHT = self.args['SDNN_WEIGHT']
        self.RMSSD_WEIGHT = self.args['RMSSD_WEIGHT']
        self.PNN50_WEIGHT = self.args['PNN50_WEIGHT']
        
        # Sensor parameters
        self.macAddress = "98:D3:11:FE:03:67"
        self.srate = 1000
        self.nframes = 10

    def read_args_from_file(self, filename):
        args = {}
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=')
                    args[key] = float(value)
        return args

    def setup_logging(self):
        self.log_filename = f"./dataset/stress_log.txt"
        self.log_file = open(self.log_filename, "w")
        portalocker.lock(self.log_file, portalocker.LOCK_EX)
        self.log_file.write("Timestamp,State\n")
        self.log_file.flush()
        portalocker.unlock(self.log_file)

    def connect_sensor(self):
        try:
            self.device = bitalino.BITalino(self.macAddress)
            time.sleep(1)
            print("BITalino sensor connected")
            self.device.start(self.srate, [0, 1])
            print("START")
        except Exception as e:
            print(f"Error connecting to sensor: {e}")
            exit()

    def initialize_variables(self):
        # Data buffers
        self.ecg_values = []
        self.ecg_buffer = []
        self.eda_buffer = []
        
        # Metrics
        self.HR = 0
        self.hrv_metrics = {"SDNN": 0, "RMSSD": 0, "PNN50": 0}
        self.last_EDA_value = 0.0
        self.last_ECG_value = 0.0
        
        # Calibration
        self.calibration_complete = False
        self.calibration_values = {
            "EDA": 0, "HR": 0, "SDNN": 0, "RMSSD": 0, "PNN50": 0
        }
        
        # History tracking
        self.stress_history = deque(maxlen=300)
        self.time_history = deque(maxlen=300)
        
        # Timing
        self.start_time = time.time()
        self.last_calculation_time = time.time()
        self.last_reconnect_time = time.time()
        self.recording_duration = 0
        self.analysis_started = False
        self.current_stress_level = 0

    def setup_display(self):
        # Initialize Pygame
        pygame.init()
        
        # Set window size to 90% of screen
        screen_info = pygame.display.Info()
        self.window_size = (int(screen_info.current_w * 0.9), int(screen_info.current_h * 0.9))
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Stress Detection System - Futuristic Interface")
        
        # Fonts
        self.font = pygame.font.SysFont("Arial", 30)
        self.hud_font = pygame.font.SysFont("Press Start 2P", 25)
        self.status_font = pygame.font.SysFont("Arial", 40)
        
        # Colors
        self.BACKGROUND_COLOR = (20, 20, 20)
        self.TEXT_COLOR = (0, 255, 0)
        self.HIGHLIGHT_COLOR = (255, 0, 0)
        self.NEON_BLUE = (0, 255, 255)
        self.NEON_PURPLE = (255, 0, 255)
        self.ECG_COLOR = (255, 255, 0)
        self.CALM_COLOR = (0, 255, 150)
        self.STRESS_COLOR = (255, 50, 50)

    def calculate_hr_from_raw(self, ecg_data, sampling_rate=1000):
        """Calculates heart rate and HRV metrics from raw ECG data."""
        if len(ecg_data) < sampling_rate:
            return 0, 0, 0, 0

        try:
            # Data normalization
            normalized_ecg = (ecg_data - np.mean(ecg_data)) / np.std(ecg_data)

            # Find R peaks with adaptive sensitivity
            peaks, _ = find_peaks(normalized_ecg, height=0.5, distance=sampling_rate//3)
            if len(peaks) < 2:
                peaks, _ = find_peaks(normalized_ecg, height=0.3, distance=sampling_rate//4)
            
            if len(peaks) < 2:
                print("No R peaks found in raw ECG data.")
                return 0, 0, 0, 0

            # Calculate RR intervals in seconds
            rr_intervals = np.diff(peaks) / sampling_rate

            # Heart rate in BPM
            hr = 60 / np.mean(rr_intervals)

            # HRV metrics
            sdnn = np.std(rr_intervals) * 1000  # in ms
            rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals)))) * 1000  # in ms

            # PNN50 calculation
            if len(rr_intervals) < 2:
                pnn50 = 0
            else:
                rr_intervals_ms = rr_intervals * 1000
                nn_diffs = np.abs(np.diff(rr_intervals_ms))
                nn50 = sum(nn_diffs > 50)
                pnn50 = (nn50 / len(nn_diffs)) * 100 if len(nn_diffs) > 0 else 0

            return hr, sdnn, rmssd, pnn50

        except Exception as e:
            print(f"Error in direct HR calculation: {e}")
            return 0, 0, 0, 0

    def analyze_stress_level(self, eda, hr, sdnn, rmssd, pnn50, baseline):
        """Calculates stress level based on physiological parameters."""
        # Weights
        weights = {
            "EDA": self.EDA_WEIGHT, "HR": self.HR_WEIGHT, 
            "SDNN": self.SDNN_WEIGHT, "RMSSD": self.RMSSD_WEIGHT, 
            "PNN50": self.PNN50_WEIGHT
        }

        # Baseline values with safety
        eda_baseline = baseline["EDA"]
        hr_baseline = baseline["HR"]
        sdnn_baseline = max(baseline["SDNN"], 1)
        rmssd_baseline = max(baseline["RMSSD"], 1)
        pnn50_baseline = max(baseline["PNN50"], 1)

        # Calculate changes from baseline (capped at 100%)
        eda_change = min(max(0, (eda - eda_baseline) / max(eda_baseline, 1)) * 100, 100)
        hr_change = min(max(0, (hr - hr_baseline) / max(hr_baseline, 1)) * 100, 100)
        sdnn_change = min(max(0, (sdnn_baseline - sdnn) / sdnn_baseline) * 100, 100)
        rmssd_change = min(max(0, (rmssd_baseline - rmssd) / rmssd_baseline) * 100, 100)
        pnn50_change = min(max(0, (pnn50_baseline - pnn50) / pnn50_baseline) * 100, 100)

        # Calculate weighted stress level
        stress_level = (
            weights["EDA"] * eda_change +
            weights["HR"] * hr_change +
            weights["SDNN"] * sdnn_change +
            weights["RMSSD"] * rmssd_change +
            weights["PNN50"] * pnn50_change
        )

        return max(0, min(stress_level, 100))

    def draw_background(self):
        self.screen.fill(self.BACKGROUND_COLOR)

    def get_stress_color(self, stress_level):
        """Returns a color between CALM_COLOR and STRESS_COLOR based on stress level."""
        color_factor = stress_level / 100.0
        return (
            int(self.CALM_COLOR[0] + (self.STRESS_COLOR[0] - self.CALM_COLOR[0]) * color_factor),
            int(self.CALM_COLOR[1] + (self.STRESS_COLOR[1] - self.CALM_COLOR[1]) * color_factor),
            int(self.CALM_COLOR[2] + (self.STRESS_COLOR[2] - self.CALM_COLOR[2]) * color_factor)
        )

    def draw_hud(self):
        """Display HUD interface with all metrics."""
        # Title
        title_text = self.hud_font.render("STRESS DETECTION SYSTEM", True, self.TEXT_COLOR)
        self.screen.blit(title_text, (30, 30))

        # Recording time counter
        time_text = self.font.render(f"Time: {self.recording_duration:.1f}s", True, self.TEXT_COLOR)
        self.screen.blit(time_text, (30, 70))

        # System status during calibration
        if not self.calibration_complete:
            status_text = self.status_font.render("CALIBRATION IN PROGRESS...", True, self.NEON_BLUE)
            self.screen.blit(status_text, (self.window_size[0]//2 - 250, self.window_size[1]//2 - 50))

        # Current metrics
        metrics = [
            (f"EDA: {self.last_EDA_value:.2f}", 120, self.TEXT_COLOR),
            (f"ECG: {self.last_ECG_value:.2f}", self.window_size[1] - 300, self.ECG_COLOR),
            (f"HR: {self.HR:.2f} bpm", self.window_size[1] - 250, self.TEXT_COLOR),
            (f"SDNN: {self.hrv_metrics['SDNN']:.2f}", self.window_size[1] - 200, self.TEXT_COLOR),
            (f"RMSSD: {self.hrv_metrics['RMSSD']:.2f}", self.window_size[1] - 150, self.TEXT_COLOR),
            (f"PNN50: {self.hrv_metrics['PNN50']:.2f}%", self.window_size[1] - 100, self.TEXT_COLOR)
        ]
        
        for text, y_pos, color in metrics:
            self.screen.blit(self.font.render(text, True, color), (30, y_pos))

        # Display stress level if calibration is complete
        if self.calibration_complete:
            stress_color = self.get_stress_color(self.current_stress_level)
            
            stress_text = self.status_font.render(f"STRESS: {self.current_stress_level:.1f}%", True, stress_color)
            self.screen.blit(stress_text, (self.window_size[0] - 350, 50))

            # State text based on stress level
            if self.current_stress_level < self.CALM_THRESHOLD:
                state_text = self.font.render("State: CALM", True, self.CALM_COLOR)
            elif self.current_stress_level < self.MODERATE_THRESHOLD:
                state_text = self.font.render("State: MODERATE TENSION", True, (255, 255, 0))
            else:
                state_text = self.font.render("State: HIGH STRESS", True, self.STRESS_COLOR)
            self.screen.blit(state_text, (self.window_size[0] - 350, 150))

    def draw_ecg_trace(self):
        """Draws the ECG trace visualization."""
        if len(self.ecg_values) < 2:
            return

        # Define ECG trace area
        ecg_area_height = 100
        ecg_area_top = self.window_size[1] - 150
        scale_factor = 5

        # Plot ECG values
        for i in range(1, len(self.ecg_values)):
            x1 = self.window_size[0] - (len(self.ecg_values) - i) * 2
            x2 = self.window_size[0] - (len(self.ecg_values) - i - 1) * 2
            y1 = ecg_area_top + ecg_area_height / 2 - self.ecg_values[i - 1] / scale_factor
            y2 = ecg_area_top + ecg_area_height / 2 - self.ecg_values[i] / scale_factor
            pygame.draw.line(self.screen, self.ECG_COLOR, (x1, y1), (x2, y2), 2)

    def draw_stress_curve(self):
        """Draws the stress level history curve."""
        if len(self.stress_history) < 2:
            return

        # Define stress curve area
        area = {
            'width': 500, 'height': 150, 
            'left': 800, 'top': 250
        }

        # Draw frame and axes
        pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                        (area['left'], area['top'], area['width'], area['height']), 1)
        pygame.draw.line(self.screen, self.TEXT_COLOR,
                        (area['left'], area['top'] + area['height']),
                        (area['left'] + area['width'], area['top'] + area['height']), 1)
        pygame.draw.line(self.screen, self.TEXT_COLOR,
                        (area['left'], area['top']),
                        (area['left'], area['top'] + area['height']), 1)

        # Draw title
        curve_title = self.font.render("Stress Level Evolution", True, self.TEXT_COLOR)
        self.screen.blit(curve_title, (area['left'], area['top'] - 50))

        # Mark graduations on Y axis
        for i in range(0, 101, 25):
            y_pos = area['top'] + area['height'] - (i / 100 * area['height'])
            pygame.draw.line(self.screen, self.TEXT_COLOR, 
                           (area['left'] - 5, y_pos), (area['left'], y_pos), 1)
            y_label = self.font.render(f"{i}", True, self.TEXT_COLOR)
            self.screen.blit(y_label, (area['left'] - 25, y_pos - 10))

        # Plot stress curve
        points = []
        for i, stress in enumerate(self.stress_history):
            if i >= len(self.stress_history) - area['width']//2:
                x = area['left'] + (i - (len(self.stress_history) - area['width']//2)) * 2
                y = area['top'] + area['height'] - (stress / 100 * area['height'])
                points.append((x, y))

        if len(points) >= 2:
            # Draw line and highlight last point
            pygame.draw.lines(self.screen, self.NEON_BLUE, False, points, 2)
            pygame.draw.circle(self.screen, self.get_stress_color(self.stress_history[-1]), points[-1], 5)

    def log_stress_state(self, stress_level):
        """Records stress state to the log file."""
        timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if stress_level < self.CALM_THRESHOLD:
            state = "CALM"
        elif stress_level < self.MODERATE_THRESHOLD:
            state = "MODERATE"
        else:
            state = "STRESSED"
            
        portalocker.lock(self.log_file, portalocker.LOCK_EX)
        self.log_file.write(f"{timestamp_now},{state}\n")
        self.log_file.flush()
        portalocker.unlock(self.log_file)

    def calibrate(self):
        """Perform calibration using buffer data."""
        print("Calibration complete, starting real-time analysis...")

        # Calculate baseline values from buffers
        if len(self.ecg_buffer) >= 20 * self.srate * 0.8:  # At least 80% of expected data
            calculated_hr, calculated_sdnn, calculated_rmssd, calculated_pnn50 = self.calculate_hr_from_raw(
                np.array(self.ecg_buffer), self.srate)
            self.calibration_values["HR"] = calculated_hr if calculated_hr > 0 else 70  # Default value if failed
            self.calibration_values["SDNN"] = calculated_sdnn if calculated_sdnn > 0 else 50
            self.calibration_values["RMSSD"] = calculated_rmssd if calculated_rmssd > 0 else 30
            self.calibration_values["PNN50"] = calculated_pnn50 if calculated_pnn50 > 0 else 10

        if len(self.eda_buffer) > 0:
            self.calibration_values["EDA"] = np.mean(self.eda_buffer)

        print(f"Calibration values: {self.calibration_values}")

    def process_data(self):
        """Process new data from the sensor."""
        try:
            # Read sensor data
            data = self.device.read(self.nframes)
            
            # Check if data is valid
            if np.mean(data[:, 1]) < 1:
                return False

            # Extract EDA and ECG values
            EDA = data[:, 5]
            ECG = data[:, 6]
            self.last_EDA_value = EDA[-1]
            self.last_ECG_value = ECG[-1]

            # Update buffers
            self.eda_buffer.extend(EDA)
            self.ecg_values.append(self.last_ECG_value)
            self.ecg_buffer.extend(ECG)
            
            # Maintain buffer sizes
            if len(self.ecg_values) > self.window_size[0]:
                self.ecg_values.pop(0)
                
            buffer_size = 20 * self.srate
            if len(self.ecg_buffer) > buffer_size:
                self.ecg_buffer = self.ecg_buffer[-buffer_size:]
            if len(self.eda_buffer) > buffer_size:
                self.eda_buffer = self.eda_buffer[-buffer_size:]
                
            return True
            
        except Exception as e:
            print(f"Error reading data: {e}")
            return False

    def update_metrics(self):
        """Calculate metrics from buffer data."""
        if len(self.ecg_buffer) >= 20 * self.srate * 0.9:  # At least 90% of desired buffer size
            # Calculate HR and HRV metrics
            calculated_hr, calculated_sdnn, calculated_rmssd, calculated_pnn50 = self.calculate_hr_from_raw(
                np.array(self.ecg_buffer), self.srate)

            # Update values if calculation was successful
            if calculated_hr > 0:
                self.HR = calculated_hr
                self.hrv_metrics["SDNN"] = calculated_sdnn
                self.hrv_metrics["RMSSD"] = calculated_rmssd
                self.hrv_metrics["PNN50"] = calculated_pnn50

                # Calculate stress level
                mean_eda = np.mean(self.eda_buffer[-int(len(self.eda_buffer)*0.2):])  # Average of last 20% values
                self.current_stress_level = self.analyze_stress_level(
                    mean_eda, self.HR, calculated_sdnn, calculated_rmssd, calculated_pnn50,
                    self.calibration_values
                )

                # Add to history and log
                self.stress_history.append(self.current_stress_level)
                self.time_history.append(self.recording_duration)
                self.log_stress_state(self.current_stress_level)

    def generate_summary(self):
        """Generate summary graph after recording."""
        if len(self.stress_history) > 0:
            plt.figure(figsize=(10, 6))
            plt.plot(list(self.time_history), list(self.stress_history), 'b-', linewidth=2)
            plt.title('Stress Level Evolution Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Stress Level (%)')
            plt.grid(True)
            plt.ylim(0, 100)

            graph_filename = f"./dataset/stress_graph.png"
            plt.savefig(graph_filename)
            print(f"Graph saved in file '{graph_filename}'")

    def cleanup(self):
        """Clean up resources."""
        print("STOP")
        self.device.trigger([0, 0])
        self.device.stop()
        self.device.close()
        self.log_file.close()
        print(f"Data recorded in file '{self.log_filename}'")
        pygame.quit()

    def run(self):
        """Main application loop."""
        running = True
        while running:
            # Update recording time
            current_time = time.time()
            self.recording_duration = current_time - self.start_time

            # Handle calibration after 20 seconds
            if self.recording_duration >= 20 and not self.calibration_complete:
                self.calibration_complete = True
                self.calibrate()
                self.analysis_started = True

            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Check connection every minute
            if current_time - self.last_reconnect_time >= 60:
                print("Automatic reconnection attempt...")
                self.device.stop()
                self.device.close()
                self.connect_sensor()
                self.last_reconnect_time = current_time

            # Process sensor data
            if not self.process_data():
                break

            # Update metrics every second
            if self.analysis_started and current_time - self.last_calculation_time >= 1.0:
                self.update_metrics()
                self.last_calculation_time = current_time

            # Update display
            self.draw_background()
            self.draw_hud()
            self.draw_ecg_trace()
            
            if self.calibration_complete:
                self.draw_stress_curve()

            # Update display and wait briefly
            pygame.display.flip()
            pygame.time.delay(10)

        # Clean up after exit
        self.cleanup()
        self.generate_summary()


# Run the application
if __name__ == "__main__":
    stress_system = StressDetectionSystem()
    stress_system.run()