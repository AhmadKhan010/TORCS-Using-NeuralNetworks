import msgParser
import carState
import carControl
import keyboard
import time
import os
import csv
from datetime import datetime

class Driver(object):
    '''
    A driver object for the SCRC
    '''

    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage
        
        self.parser = msgParser.MsgParser()
        
        self.state = carState.CarState()
        
        self.control = carControl.CarControl()
        
        self.steer_lock = 0.785398  # Maximum steering lock (in radians)
        self.max_speed = 100
        self.prev_rpm = None
        
        # Initialize CSV logging
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = os.path.join(log_dir, f"telemetry_{timestamp}.csv")
        self.create_csv_file()
        
        # Control settings for smooth steering
        self.acceleration_step = 0.1
        self.manual_influence = 0.0      # How much manual steering is applied (0.0-1.0)
        self.target_position = 0.0       # Target track position (-1.0 to 1.0)
        self.position_change_rate = 0.05 # How quickly target position changes
        
        # steering parameters
        self.steer_lock = 0.785398
        self.max_speed = 300
        self.prev_rpm = None
        self.current_steer = 0.0  # Track current steering position
        self.steer_step = 0.04    # How quickly steering changes
        self.return_rate = 0.10   # How quickly steering returns to center
        self.shift_delay = 0  # Prevent too rapid gear changes
        self.shift_delay_time = 10  # Frames to wait between shifts
        
        print("Driver initialized. Controls:")
        print("W: Accelerate | S: Brake/Reverse | A: Turn Left | D: Turn Right | Q: Quit")
        print("\nAutomatic transmission enabled")
    
    def create_csv_file(self):
        '''Create CSV file with headers for telemetry data'''
        with open(self.csv_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'angle', 'curLapTime', 'damage', 'distFromStart', 
                'distRaced', 'fuel', 'gear', 'lastLapTime', 'racePos', 'rpm',
                'speedX', 'speedY', 'speedZ', 'trackPos', 'z', 'opponents','wheelSpinVel','focus','track',
                'accel_input', 'brake_input', 'steer_input', 'gear_input',
                'key_w', 'key_s', 'key_a', 'key_d' 
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        print(f"Telemetry will be saved to: {self.csv_filename}")
    
    def log_data(self):
        '''Log current state and control data to CSV'''
        with open(self.csv_filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'timestamp', 'angle', 'curLapTime', 'damage', 'distFromStart', 
                'distRaced', 'fuel', 'gear', 'lastLapTime', 'racePos', 'rpm',
                'speedX', 'speedY', 'speedZ', 'trackPos','opponents','wheelSpinVel','focus','track', 'z',
                'accel_input', 'brake_input', 'steer_input', 'gear_input',
                'key_w', 'key_s', 'key_a', 'key_d'  
            ])
            
       
            data = {
                'timestamp': time.time(),
                'angle': self.state.angle,
                'curLapTime': self.state.curLapTime,
                'damage': self.state.damage,
                'distFromStart': self.state.distFromStart,
                'distRaced': self.state.distRaced,
                'fuel': self.state.fuel,
                'gear': self.state.gear,
                'lastLapTime': self.state.lastLapTime,
                'racePos': self.state.racePos,
                'rpm': self.state.rpm,
                'speedX': self.state.speedX,
                'speedY': self.state.speedY,
                'speedZ': self.state.speedZ,
                'trackPos': self.state.trackPos,
                'opponents': self.state.opponents,
                'wheelSpinVel': self.state.wheelSpinVel,
                'focus': self.state.focus,
                'track': self.state.track,
                'z': self.state.z,
                'accel_input': self.control.getAccel(),
                'brake_input': self.control.getBrake(),
                'steer_input': self.control.getSteer(),
                'gear_input': self.control.getGear(),
                # Store keyboard states (1 for pressed, 0 for not pressed)
                'key_w': 1 if keyboard.is_pressed('w') else 0,
                'key_s': 1 if keyboard.is_pressed('s') else 0,
                'key_a': 1 if keyboard.is_pressed('a') else 0,
                'key_d': 1 if keyboard.is_pressed('d') else 0
            }
            
            writer.writerow(data)
    
    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]
        
        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15
        
        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5
        
        return self.parser.stringify({'init': self.angles})
    
    def drive(self, msg):
       
        self.state.setFromMsg(msg)
        
        self.handle_keyboard_input()
        
        # Save telemetry data
        self.log_data()
        
        if keyboard.is_pressed('q'):
            print("User requested to quit")
            return "(meta 1)"
        
        return self.control.toMsg()
    
    def handle_keyboard_input(self):
        '''Get keyboard input and apply to car controls'''
        # Get current control values
        accel = self.control.getAccel()
        brake = self.control.getBrake()
        steer = self.current_steer
        gear = self.control.getGear()
        speed = self.state.getSpeedX()
        rpm = self.state.getRpm()
        
        # Default decay
        accel *= 0.9
        brake *= 0.9

        # Decrease shift delay counter
        if self.shift_delay > 0:
            self.shift_delay -= 1
        
        # Handle acceleration (W key)
        if keyboard.is_pressed('w'):
            if gear == -1:  # If in reverse gear and pressing W, switch to first gear
                gear = 1
            accel += self.acceleration_step
            brake = 0
            if accel > 1.0:
                accel = 1.0
        
        if keyboard.is_pressed('s'):
            if gear == -1:
                # accelerate backwords
                accel += self.acceleration_step
                brake = 0
                if accel > 1.0:
                    accel = 1.0
            else:
                # Normal braking in forward gears
                brake += self.acceleration_step
                accel = 0
                if brake > 1.0:
                    brake = 1.0
                
                # Switch to reverse gear if nearly stopped and brake is applied
                if abs(speed) < 2.0 and brake > 0.5:
                    gear = -1

        if self.shift_delay == 0 and gear >= -1:  
            if gear == -1:
                # Only shift out of reverse when going forward
                if keyboard.is_pressed('w'):
                    gear = 1
                    self.shift_delay = self.shift_delay_time
            else:
                
                if gear == 0:  
                    gear = 1
                elif gear > 0:  # Forward gears
                    if rpm > 8000 and gear < 6 and accel > 0.0:
                        gear += 1
                        self.shift_delay = self.shift_delay_time
                    elif rpm < 3000 and gear > 1:
                        gear -= 1
                        self.shift_delay = self.shift_delay_time
                    elif speed < 5 and gear > 1:  # Downshift at very low speeds
                        gear = 1
                        self.shift_delay = self.shift_delay_time

     
        if keyboard.is_pressed('a'):  # Left turn (+1)
            self.current_steer = min(1.0, self.current_steer + self.steer_step)
        elif keyboard.is_pressed('d'):  # Right turn (-1)
            self.current_steer = max(-1.0, self.current_steer - self.steer_step)
        else:
            # Gradually return to center when no keys are pressed
            if abs(self.current_steer) < self.return_rate:
                self.current_steer = 0
            elif self.current_steer > 0:
                self.current_steer -= self.return_rate
            else:
                self.current_steer += self.return_rate

        steer = self.current_steer
        
        self.control.setAccel(accel)
        self.control.setBrake(brake)
        self.control.setSteer(steer)
        self.control.setGear(gear)
        
        # Update previous RPM
        self.prev_rpm = rpm
    
    def onShutDown(self):
        print("Session ended - telemetry saved to:", self.csv_filename)
    
    def onRestart(self):
        print("Session restarted - continuing to log telemetry")
